import unittest
from fastapi.testclient import TestClient
from main import app
from backend.database import (
    get_db_connection,
    get_public_payment_methods_db,
    register_trial_tenant_db
)
from backend.services.payment_gateway import PaymentGateway

class TestPaymentCheckoutFlow(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_public_payment_methods_endpoint(self):
        """Test GET /api/public/payment-methods returns configured public methods safely."""
        res = self.client.get("/api/public/payment-methods")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        gateways = data.get("gateways", [])
        self.assertGreaterEqual(len(gateways), 1)

        # Check that no secrets are leaked
        for gw in gateways:
            self.assertNotIn("secret_key", gw)
            self.assertNotIn("webhook_secret", gw)
            self.assertIn("gateway_provider", gw)

        providers = [gw["gateway_provider"] for gw in gateways]
        self.assertIn("PROMPTPAY", providers)
        self.assertIn("BANK_TRANSFER", providers)

    def test_direct_signup_creates_open_invoice_and_pending_subscription(self):
        """Test direct signup on paid plan provisions PENDING_PAYMENT subscription and OPEN invoice."""
        test_email = "direct_signup_test@example.com"
        
        # Clean up if existed
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (test_email,))
        user_row = cursor.fetchone()
        if user_row:
            u_id = user_row[0] if isinstance(user_row, tuple) else user_row["id"]
            cursor.execute("DELETE FROM organization_members WHERE user_id = ?", (u_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (u_id,))
            conn.commit()
        conn.close()

        res = register_trial_tenant_db({
            "company_name": "Direct Auto Test Ltd",
            "contact_name": "Somchai Test",
            "email": test_email,
            "password": "Password123!",
            "phone": "0812345678",
            "segment": "GARAGE",
            "plan_id": "professional",
            "signup_type": "DIRECT",
            "verification_code": "999999",
            "selected_categories": ["Brake Systems"],
            "selected_aftermarket_brands": ["BREMBO"]
        })

        self.assertTrue(res.get("success"), f"Registration failed: {res.get('error')}")
        self.assertFalse(res.get("is_trial"))
        self.assertEqual(res.get("status"), "PAST_DUE")
        self.assertIsNotNone(res.get("invoice_id"))
        self.assertIsNotNone(res.get("invoice_number"))
        self.assertGreater(res.get("total_amount"), 0)

        # Verify Invoice in DB
        inv_id = res["invoice_id"]
        org_id = res["org_id"]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status, total_amount FROM invoices WHERE id = ?", (inv_id,))
        inv_row = cursor.fetchone()
        self.assertIsNotNone(inv_row)
        inv_status = inv_row[0] if isinstance(inv_row, tuple) else inv_row["status"]
        self.assertEqual(inv_status, "OPEN")

        # Now pay the invoice via charge_payment
        charge_res = self.client.post("/api/saas/payments/charge", json={
            "invoice_id": inv_id,
            "amount": float(res["total_amount"]),
            "payment_method": "PROMPTPAY"
        }, headers={"x-username": test_email})
        self.assertEqual(charge_res.status_code, 200)
        c_data = charge_res.json()
        self.assertTrue(c_data.get("success"))
        self.assertEqual(c_data.get("status"), "SUCCESS")

        # Verify subscription is now ACTIVE and invoice is PAID
        cursor.execute("SELECT status FROM invoices WHERE id = ?", (inv_id,))
        inv_paid_row = cursor.fetchone()
        inv_paid_status = inv_paid_row[0] if isinstance(inv_paid_row, tuple) else inv_paid_row["status"]
        self.assertEqual(inv_paid_status, "PAID")

        cursor.execute("SELECT status FROM subscriptions WHERE org_id = ?", (org_id,))
        sub_row = cursor.fetchone()
        sub_status = sub_row[0] if isinstance(sub_row, tuple) else sub_row["status"]
        self.assertEqual(sub_status, "ACTIVE")
        conn.close()

    def test_customer_bank_transfer_submission(self):
        """Test customer submitting bank transfer proof sets invoice to PENDING_VERIFICATION."""
        test_email = "transfer_test@example.com"
        
        # Clean up if existed
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (test_email,))
        user_row = cursor.fetchone()
        if user_row:
            u_id = user_row[0] if isinstance(user_row, tuple) else user_row["id"]
            cursor.execute("DELETE FROM organization_members WHERE user_id = ?", (u_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (u_id,))
            conn.commit()
        conn.close()

        res = register_trial_tenant_db({
            "company_name": "Bank Transfer Test Ltd",
            "contact_name": "Transfer User",
            "email": test_email,
            "password": "Password123!",
            "phone": "0899998888",
            "segment": "GARAGE",
            "plan_id": "professional",
            "signup_type": "DIRECT",
            "verification_code": "999999"
        })
        self.assertTrue(res.get("success"))
        inv_id = res["invoice_id"]

        submit_res = self.client.post("/api/saas/payments/submit-bank-transfer", json={
            "invoice_id": inv_id,
            "amount": float(res["total_amount"]),
            "proof_reference": "REF-TEST-998811",
            "slip_url": "https://example.com/slip.png"
        }, headers={"x-username": test_email})
        self.assertEqual(submit_res.status_code, 200)
        s_data = submit_res.json()
        self.assertTrue(s_data.get("success"))
        self.assertEqual(s_data.get("status"), "PENDING_VERIFICATION")

        # Verify DB invoice status
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM invoices WHERE id = ?", (inv_id,))
        row = cursor.fetchone()
        status_val = row[0] if isinstance(row, tuple) else row["status"]
        self.assertEqual(status_val, "PENDING_VERIFICATION")
        conn.close()

if __name__ == "__main__":
    unittest.main()
