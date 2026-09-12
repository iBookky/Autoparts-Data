import os
import sys
import unittest
import hashlib
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from backend.database import (
    get_db_connection,
    get_org_aftermarket_brand_entitlements,
    update_org_aftermarket_brand_entitlements,
    register_trial_tenant_db
)
from backend.services.entitlement_service import EntitlementService

class AftermarketBrandEntitlementTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.conn = get_db_connection()
        cls.cursor = cls.conn.cursor()

        # Set up a test tenant user
        cls.test_email = "test_aftermarket_owner@example.com"
        cls.cursor.execute("SELECT id FROM users WHERE username = ?", (cls.test_email,))
        u_row = cls.cursor.fetchone()
        if not u_row:
            pwd_hash = hashlib.sha256("password123".encode()).hexdigest()
            cls.cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'STAFF')", (cls.test_email, pwd_hash))
            cls.cursor.execute("SELECT id FROM users WHERE username = ?", (cls.test_email,))
            cls.user_id = cls.cursor.fetchone()["id"]
        else:
            cls.user_id = u_row["id"]

        cls.cursor.execute("SELECT id FROM organizations WHERE slug = 'test-aftermarket-org'")
        org_row = cls.cursor.fetchone()
        if not org_row:
            cls.cursor.execute("INSERT INTO organizations (name, slug, plan_tier) VALUES ('Test Aftermarket Org', 'test-aftermarket-org', 'PROFESSIONAL')")
            cls.cursor.execute("SELECT id FROM organizations WHERE slug = 'test-aftermarket-org'")
            cls.org_id = cls.cursor.fetchone()["id"]
        else:
            cls.org_id = org_row["id"]
            cls.cursor.execute("UPDATE organizations SET plan_tier = 'PROFESSIONAL' WHERE id = ?", (cls.org_id,))

        cls.cursor.execute("DELETE FROM organization_members WHERE org_id = ? AND user_id = ?", (cls.org_id, cls.user_id))
        cls.cursor.execute("""
            INSERT INTO organization_members (org_id, user_id, org_role, status)
            VALUES (?, ?, 'OWNER', 'ACTIVE')
        """, (cls.org_id, cls.user_id))

        cls.cursor.execute("DELETE FROM subscriptions WHERE org_id = ?", (cls.org_id,))
        cls.cursor.execute("""
            INSERT INTO subscriptions (org_id, plan_id, status, billing_cycle, current_period_end)
            VALUES (?, 'professional', 'ACTIVE', 'MONTHLY', NOW() + INTERVAL '30 days')
        """, (cls.org_id,))

        # Initialize explicit entitlements: allow DENSO and AISIN only
        cls.cursor.execute("DELETE FROM entitlements WHERE org_id = ?", (cls.org_id,))
        cls.cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'BRAND', 'TOYOTA', 1)", (cls.org_id,))
        cls.cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'CATEGORY', '*', 1)", (cls.org_id,))
        cls.cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'AFTERMARKET_BRAND', 'DENSO', 1)", (cls.org_id,))
        cls.cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'AFTERMARKET_BRAND', 'AISIN', 1)", (cls.org_id,))

        cls.conn.commit()
        cls.auth_headers = {"x-username": cls.test_email}

    @classmethod
    def tearDownClass(cls):
        try:
            cls.cursor.execute("DELETE FROM usage_records WHERE org_id = ?", (cls.org_id,))
            cls.cursor.execute("DELETE FROM commercial_audit_logs WHERE org_id = ?", (cls.org_id,))
            cls.cursor.execute("DELETE FROM entitlements WHERE org_id = ?", (cls.org_id,))
            cls.cursor.execute("DELETE FROM subscriptions WHERE org_id = ?", (cls.org_id,))
            cls.cursor.execute("DELETE FROM organization_members WHERE org_id = ? AND user_id = ?", (cls.org_id, cls.user_id))
            cls.cursor.execute("DELETE FROM organizations WHERE id = ?", (cls.org_id,))
            cls.cursor.execute("DELETE FROM users WHERE id = ?", (cls.user_id,))
            cls.conn.commit()
            cls.conn.close()
        except Exception:
            pass

    def test_01_get_org_aftermarket_brand_entitlements(self):
        """Verify get_org_aftermarket_brand_entitlements returns granted status correctly."""
        data = get_org_aftermarket_brand_entitlements(self.org_id)
        self.assertEqual(data["org_id"], self.org_id)
        self.assertIn("DENSO", data["granted_brands"])
        self.assertIn("AISIN", data["granted_brands"])
        self.assertNotIn("BOSCH", data["granted_brands"])
        
        # Check brand matrix items
        brands_map = {b["name"]: b["is_granted"] for b in data["aftermarket_brands"]}
        self.assertTrue(brands_map.get("DENSO"))
        self.assertTrue(brands_map.get("AISIN"))
        if "BOSCH" in brands_map:
            self.assertFalse(brands_map.get("BOSCH"))

    def test_02_update_org_aftermarket_brand_entitlements(self):
        """Verify update_org_aftermarket_brand_entitlements modifies granted brands."""
        ok, msg, brands = update_org_aftermarket_brand_entitlements(self.org_id, ["BOSCH", "BREMBO", "TRW"])
        self.assertTrue(ok)
        self.assertCountEqual(brands, ["BOSCH", "BREMBO", "TRW"])

        data = get_org_aftermarket_brand_entitlements(self.org_id)
        self.assertIn("BOSCH", data["granted_brands"])
        self.assertIn("BREMBO", data["granted_brands"])
        self.assertIn("TRW", data["granted_brands"])
        self.assertNotIn("DENSO", data["granted_brands"])

        # Restore DENSO & AISIN for following tests
        update_org_aftermarket_brand_entitlements(self.org_id, ["DENSO", "AISIN"])

    def test_03_validate_search_access_aftermarket_brand(self):
        """Verify validate_search_access locks unauthorized aftermarket brands."""
        # DENSO is granted -> should succeed
        allowed, locked, _ = EntitlementService.validate_search_access(
            username=self.test_email,
            user_role="STAFF",
            aftermarket_brand="DENSO"
        )
        self.assertTrue(allowed)
        self.assertIsNone(locked)

        # BOSCH is not granted -> should be locked with AFTERMARKET_BRAND_LOCKED
        allowed, locked, _ = EntitlementService.validate_search_access(
            username=self.test_email,
            user_role="STAFF",
            aftermarket_brand="BOSCH"
        )
        self.assertFalse(allowed)
        self.assertIsNotNone(locked)
        self.assertEqual(locked.get("reason"), "AFTERMARKET_BRAND_LOCKED")
        self.assertEqual(locked.get("locked_entity_name"), "BOSCH")

    def test_04_validate_product_access_aftermarket_brand(self):
        """Verify validate_product_access checks part's aftermarket brand."""
        # Insert test parts into master_parts
        self.cursor.execute("""
            INSERT INTO master_parts (part_number, product_name_en, category, brand, oem_number, car_brand)
            VALUES ('DN-TEST-001', 'Denso Spark Plug Test', 'Engine', 'DENSO', 'OEM-DN-1', 'TOYOTA')
        """)
        denso_part_id = self.cursor.lastrowid

        self.cursor.execute("""
            INSERT INTO master_parts (part_number, product_name_en, category, brand, oem_number, car_brand)
            VALUES ('BS-TEST-001', 'Bosch Brake Disc Test', 'Brake', 'BOSCH', 'OEM-BS-1', 'TOYOTA')
        """)
        bosch_part_id = self.cursor.lastrowid
        self.conn.commit()

        try:
            allowed, locked = EntitlementService.validate_product_access(
                username=self.test_email,
                user_role="STAFF",
                part_id=denso_part_id
            )
            self.assertTrue(allowed)
            self.assertIsNone(locked)

            allowed, locked = EntitlementService.validate_product_access(
                username=self.test_email,
                user_role="STAFF",
                part_id=bosch_part_id
            )
            self.assertFalse(allowed)
            self.assertIsNotNone(locked)
            self.assertEqual(locked.get("reason"), "AFTERMARKET_BRAND_LOCKED")
        finally:
            self.cursor.execute("DELETE FROM master_parts WHERE id IN (?, ?)", (denso_part_id, bosch_part_id))
            self.conn.commit()

    def test_05_api_aftermarket_brands_endpoints(self):
        """Verify GET and POST /api/saas/subscription/aftermarket-brands via HTTP."""
        resp = self.client.get("/api/saas/subscription/aftermarket-brands", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        json_data = resp.json()
        self.assertTrue(json_data.get("success"))
        self.assertIn("DENSO", json_data.get("granted_brands", []))

        # Update via POST
        post_resp = self.client.post(
            "/api/saas/subscription/aftermarket-brands",
            headers=self.auth_headers,
            json={"selected_brands": ["DENSO", "AISIN", "NGK"]}
        )
        self.assertEqual(post_resp.status_code, 200)
        post_data = post_resp.json()
        self.assertTrue(post_data.get("success"))
        self.assertIn("NGK", post_data.get("aftermarket_brands", []))

        # Re-fetch to confirm NGK was added
        resp2 = self.client.get("/api/saas/subscription/aftermarket-brands", headers=self.auth_headers)
        self.assertIn("NGK", resp2.json().get("granted_brands", []))

    def test_06_search_api_aftermarket_brand_lock(self):
        """Verify /api/parts/search returns locked card for excluded aftermarket brand."""
        resp = self.client.get("/api/parts/search?aftermarket_brand=BOSCH", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("locked"))
        self.assertEqual(data.get("reason"), "AFTERMARKET_BRAND_LOCKED")
        self.assertEqual(data.get("locked_entity_name"), "BOSCH")

    def test_07_trial_registration_with_aftermarket_brands(self):
        """Verify registering trial with custom aftermarket brands creates entitlements."""
        from backend.database import create_verification_code
        trial_email = "trial_brand_tester@example.com"
        
        # Ensure clean state
        self.cursor.execute("SELECT id FROM users WHERE username = ?", (trial_email,))
        old_u = self.cursor.fetchone()
        if old_u:
            uid = old_u["id"]
            self.cursor.execute("SELECT org_id FROM organization_members WHERE user_id = ?", (uid,))
            for r in self.cursor.fetchall():
                oid = r["org_id"]
                self.cursor.execute("DELETE FROM usage_records WHERE org_id = ?", (oid,))
                self.cursor.execute("DELETE FROM commercial_audit_logs WHERE org_id = ?", (oid,))
                self.cursor.execute("DELETE FROM entitlements WHERE org_id = ?", (oid,))
                self.cursor.execute("DELETE FROM subscriptions WHERE org_id = ?", (oid,))
                self.cursor.execute("DELETE FROM organization_members WHERE org_id = ?", (oid,))
                self.cursor.execute("DELETE FROM organizations WHERE id = ?", (oid,))
            self.cursor.execute("DELETE FROM customer_leads WHERE email = ?", (trial_email,))
            self.cursor.execute("DELETE FROM verification_codes WHERE email = ?", (trial_email,))
            self.cursor.execute("DELETE FROM organization_members WHERE user_id = ?", (uid,))
            self.cursor.execute("DELETE FROM users WHERE id = ?", (uid,))
            self.conn.commit()

        otp = create_verification_code(trial_email)

        res = register_trial_tenant_db({
            "contact_name": "Trial Tester",
            "company_name": "Tester Aftermarket Garage",
            "email": trial_email,
            "password": "Password123!",
            "phone": "0812345678",
            "verification_code": otp,
            "primary_car_brand": "TOYOTA",
            "selected_brands": ["TOYOTA", "HONDA"],
            "selected_categories": ["Brake", "Engine"],
            "selected_aftermarket_brands": ["DENSO", "TOKICO"]
        })
        self.assertTrue(res.get("success"), f"Trial registration failed: {res.get('error')}")
        tid = res["org_id"]

        try:
            # Check created entitlements for trial org
            wl = EntitlementService.get_organization_whitelist(tid)
            self.assertIn("DENSO", wl.get("allowed_aftermarket_brands", []))
            self.assertIn("TOKICO", wl.get("allowed_aftermarket_brands", []))
            self.assertNotIn("BOSCH", wl.get("allowed_aftermarket_brands", []))
        finally:
            # Clean up trial tenant
            self.cursor.execute("DELETE FROM usage_records WHERE org_id = ?", (tid,))
            self.cursor.execute("DELETE FROM commercial_audit_logs WHERE org_id = ?", (tid,))
            self.cursor.execute("DELETE FROM entitlements WHERE org_id = ?", (tid,))
            self.cursor.execute("DELETE FROM subscriptions WHERE org_id = ?", (tid,))
            self.cursor.execute("DELETE FROM organization_members WHERE org_id = ?", (tid,))
            self.cursor.execute("DELETE FROM organizations WHERE id = ?", (tid,))
            self.cursor.execute("DELETE FROM customer_leads WHERE email = ?", (trial_email,))
            self.cursor.execute("DELETE FROM verification_codes WHERE email = ?", (trial_email,))
            self.cursor.execute("DELETE FROM users WHERE username = ?", (trial_email,))
            self.conn.commit()

if __name__ == "__main__":
    unittest.main()
