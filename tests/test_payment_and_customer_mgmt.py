import unittest
from fastapi.testclient import TestClient
from main import app
import backend.database as db

class TestPaymentAndCustomerMgmt(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.owner_headers = {"x-username": "owner", "x-user-role": "OWNER"}

    def test_payment_gateways_retrieval_and_masking(self):
        """Verify GET /api/owner/payment-settings returns seeded gateways with masked secrets."""
        res = self.client.get("/api/owner/payment-settings", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        gateways = data.get("gateways", [])
        self.assertGreaterEqual(len(gateways), 5)
        
        providers = {g.get("provider") or g.get("gateway_provider") for g in gateways}
        self.assertIn("PROMPTPAY", providers)
        self.assertIn("STRIPE", providers)
        self.assertIn("OMISE", providers)
        self.assertIn("GB_PRIME_PAY", providers)
        self.assertIn("BANK_TRANSFER", providers)

        for g in gateways:
            if g.get("secret_key"):
                self.assertIn("••••", g["secret_key"], "Secret keys must be masked")

    def test_payment_gateway_save_and_preserve_secret(self):
        """Verify POST /api/owner/payment-settings saves config and preserves masked secret keys."""
        # 1. Save with a specific secret
        payload = {
            "provider": "STRIPE",
            "is_enabled": True,
            "public_key": "pk_test_autoparts_unit_test",
            "secret_key": "sk_test_secret_initial_key",
            "webhook_secret": "whsec_test_secret",
            "mode": "SANDBOX"
        }
        res = self.client.post("/api/owner/payment-settings", json=payload, headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get("success"))

        # 2. Update with masked secret - should preserve original secret
        payload_masked = {
            "provider": "STRIPE",
            "is_enabled": True,
            "public_key": "pk_test_autoparts_unit_test_updated",
            "secret_key": "••••••••",
            "webhook_secret": "whsec_test_secret",
            "mode": "PRODUCTION"
        }
        res2 = self.client.post("/api/owner/payment-settings", json=payload_masked, headers=self.owner_headers)
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(res2.json().get("success"))

        # Verify in database that real secret was not overwritten with literal dots
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT secret_key, public_key, environment FROM payment_gateway_settings WHERE gateway_provider = 'STRIPE'")
        row = cur.fetchone()
        self.assertIsNotNone(row)
        self.assertEqual(row["secret_key"], "sk_test_secret_initial_key")
        self.assertEqual(row["public_key"], "pk_test_autoparts_unit_test_updated")
        self.assertEqual(row["environment"], "PRODUCTION")
        conn.close()

    def test_payment_gateway_test_connection(self):
        """Verify POST /api/owner/payment-settings/test-connection responds with latency."""
        res = self.client.post(
            "/api/owner/payment-settings/test-connection",
            json={"provider": "PROMPTPAY"},
            headers=self.owner_headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("latency_ms", data)

    def test_customer_editing_and_package_modification(self):
        """Verify customer profile editing, subscription upgrading, and quota adjustments."""
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO organizations (name, slug, plan_tier)
            VALUES ('Test Garage Auto Mgmt', 'test-garage-mgmt-99', 'STARTER')
        """)
        test_org_id = cur.lastrowid

        cur.execute("""
            INSERT INTO subscriptions (org_id, plan_id, status, billing_interval, base_price, current_period_start, current_period_end)
            VALUES (?, 'starter', 'ACTIVE', 'MONTHLY', 990, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '30 days')
        """, (test_org_id,))
        conn.commit()
        conn.close()

        try:
            # 1. Edit customer profile
            edit_payload = {
                "name": "Updated Test Garage Co., Ltd.",
                "legal_name": "Test Garage Thailand Ltd.",
                "tax_id": "0105559998881",
                "email": "billing@testgarage.com",
                "phone": "0812345678",
                "billing_address": "123 Test Road, Bangkok 10110",
                "contact_name": "Somchai Test",
                "industry_type": "GARAGE"
            }
            res_edit = self.client.put(
                f"/api/owner/customers/{test_org_id}",
                json=edit_payload,
                headers=self.owner_headers
            )
            self.assertEqual(res_edit.status_code, 200)
            self.assertTrue(res_edit.json().get("success"))

            # Verify profile update in DB
            conn = db.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT name, legal_name, tax_id, billing_email FROM organizations WHERE id = ?", (test_org_id,))
            org_row = cur.fetchone()
            self.assertEqual(org_row["name"], "Updated Test Garage Co., Ltd.")
            self.assertEqual(org_row["legal_name"], "Test Garage Thailand Ltd.")
            self.assertEqual(org_row["tax_id"], "0105559998881")
            self.assertEqual(org_row["billing_email"], "billing@testgarage.com")
            conn.close()

            # 2. Modify subscription package
            sub_payload = {
                "plan_id": "business",
                "status": "ACTIVE",
                "billing_cycle": "YEARLY",
                "search_quota": 25000
            }
            res_sub = self.client.put(
                f"/api/owner/customers/{test_org_id}/subscription",
                json=sub_payload,
                headers=self.owner_headers
            )
            self.assertEqual(res_sub.status_code, 200)
            self.assertTrue(res_sub.json().get("success"))

            # Verify subscription update in DB
            conn = db.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT plan_tier FROM organizations WHERE id = ?", (test_org_id,))
            org_row = cur.fetchone()
            self.assertEqual(org_row["plan_tier"], "BUSINESS")

            cur.execute("SELECT plan_id, billing_cycle FROM subscriptions WHERE org_id = ?", (test_org_id,))
            sub_row = cur.fetchone()
            self.assertEqual(sub_row["plan_id"], "business")
            self.assertEqual(sub_row["billing_cycle"], "YEARLY")
            conn.close()

            # 3. System HQ deletion protection (org_id = 1)
            res_del_hq = self.client.delete("/api/owner/customers/1", headers=self.owner_headers)
            self.assertEqual(res_del_hq.status_code, 400)
            self.assertIn("Platform Headquarters", res_del_hq.json().get("detail", ""))

            # 4. Delete the test organization
            res_del = self.client.delete(f"/api/owner/customers/{test_org_id}", headers=self.owner_headers)
            self.assertEqual(res_del.status_code, 200)
            self.assertTrue(res_del.json().get("success"))

            # Verify deletion
            conn = db.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM organizations WHERE id = ?", (test_org_id,))
            self.assertIsNone(cur.fetchone())
            conn.close()

        finally:
            # Cleanup if still exists
            db.delete_organization_db(test_org_id)

    def test_owner_financial_summary_and_invoice_confirmation(self):
        """Verify GET /api/owner/financial-summary and invoice payment confirmation."""
        # Create a test pending invoice
        conn = db.get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO invoices (org_id, invoice_number, amount, total_amount, status, payment_method)
            VALUES (1, 'INV-TEST-001', 5990.00, 5990.00, 'PENDING', 'PROMPTPAY')
        """)
        test_inv_id = cur.lastrowid
        conn.commit()
        conn.close()

        try:
            # Check financial summary
            res = self.client.get("/api/owner/financial-summary", headers=self.owner_headers)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data.get("success"))
            summary = data.get("summary", {})
            self.assertIn("cash_collected", summary)
            self.assertIn("gateway_fees", summary)
            self.assertIn("owner_net_payout", summary)
            self.assertIn("pending_invoices", summary)
            self.assertIn("invoices", summary)

            # Confirm payment on test invoice
            res_conf = self.client.post(f"/api/owner/invoices/{test_inv_id}/confirm-payment", headers=self.owner_headers)
            self.assertEqual(res_conf.status_code, 200)
            self.assertTrue(res_conf.json().get("success"))

            # Verify invoice is now PAID
            conn = db.get_db_connection()
            cur = conn.cursor()
            cur.execute("SELECT status FROM invoices WHERE id = ?", (test_inv_id,))
            inv_row = cur.fetchone()
            self.assertEqual(inv_row["status"], "PAID")
            conn.close()

        finally:
            conn = db.get_db_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM invoices WHERE id = ?", (test_inv_id,))
            conn.commit()
            conn.close()

    def test_clean_test_data_endpoint(self):
        """Verify POST /api/owner/clean-test-data endpoint succeeds."""
        res = self.client.post(
            "/api/owner/clean-test-data",
            json={"confirm": "CLEAN", "preserve_users": True, "preserve_parts": True},
            headers=self.owner_headers
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("detail", data)

if __name__ == '__main__':
    unittest.main()
