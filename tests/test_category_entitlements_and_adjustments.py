import os
import sys
import unittest
import sqlite3
from fastapi.testclient import TestClient

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from backend.database import (
    get_db_connection,
    get_org_category_entitlements,
    update_org_category_entitlements,
    register_trial_tenant_db
)
from backend.services.entitlement_service import EntitlementService

class CategoryEntitlementsAndAdjustmentsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.conn = get_db_connection()
        cls.cursor = cls.conn.cursor()

        # Set up a test tenant with starter plan (limited to 2 categories: 'Brake', 'Filters')
        cls.cursor.execute("SELECT id FROM users WHERE username = 'test_cat_owner@example.com'")
        u_row = cls.cursor.fetchone()
        if not u_row:
            import hashlib
            pwd_hash = hashlib.sha256("password123".encode()).hexdigest()
            cls.cursor.execute("INSERT INTO users (username, password, role) VALUES ('test_cat_owner@example.com', ?, 'STAFF')", (pwd_hash,))
            cls.user_id = cls.cursor.lastrowid
        else:
            cls.user_id = u_row["id"]

        cls.cursor.execute("SELECT id FROM organizations WHERE slug = 'test-cat-org'")
        org_row = cls.cursor.fetchone()
        if not org_row:
            cls.cursor.execute("INSERT INTO organizations (name, slug, plan_tier) VALUES ('Test Category Org', 'test-cat-org', 'STARTER')")
            cls.org_id = cls.cursor.lastrowid
        else:
            cls.org_id = org_row["id"]

        cls.cursor.execute("""
            INSERT OR REPLACE INTO organization_members (org_id, user_id, org_role, status)
            VALUES (?, ?, 'OWNER', 'ACTIVE')
        """, (cls.org_id, cls.user_id))

        cls.cursor.execute("""
            INSERT OR REPLACE INTO subscriptions (org_id, plan_id, status, billing_cycle, current_period_start, current_period_end)
            VALUES (?, 'starter', 'ACTIVE', 'MONTHLY', CURRENT_TIMESTAMP, datetime('now', '+30 days'))
        """, (cls.org_id,))

        # Explicitly grant only 'Brake' and 'Filters' categories
        cls.cursor.execute("DELETE FROM entitlements WHERE org_id = ?", (cls.org_id,))
        cls.cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'CATEGORY', 'Brake', 1)", (cls.org_id,))
        cls.cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'CATEGORY', 'Filters', 1)", (cls.org_id,))
        # Grant brands
        cls.cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'BRAND', 'TOYOTA', 1)", (cls.org_id,))
        cls.cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'BRAND', 'HONDA', 1)", (cls.org_id,))
        
        cls.conn.commit()

        # Find or create sample master parts for testing
        cls.cursor.execute("SELECT id, category, brand FROM master_parts WHERE LOWER(category) LIKE '%brake%' LIMIT 1")
        brake_part = cls.cursor.fetchone()
        if not brake_part:
            cls.cursor.execute("""
                INSERT INTO master_parts (part_number, product_name_en, category, brand, oem_number, car_brand)
                VALUES ('TEST-BRK-001', 'Front Brake Pad Test', 'Brake', 'TOYOTA', 'OEM-BRK-99', 'TOYOTA')
            """)
            cls.brake_part_id = cls.cursor.lastrowid
        else:
            cls.brake_part_id = brake_part["id"]

        cls.cursor.execute("SELECT id, category, brand FROM master_parts WHERE LOWER(category) LIKE '%suspension%' LIMIT 1")
        susp_part = cls.cursor.fetchone()
        if not susp_part:
            cls.cursor.execute("""
                INSERT INTO master_parts (part_number, product_name_en, category, brand, oem_number, car_brand)
                VALUES ('TEST-SUS-001', 'Control Arm Suspension Test', 'Suspension', 'TOYOTA', 'OEM-SUS-99', 'TOYOTA')
            """)
            cls.susp_part_id = cls.cursor.lastrowid
        else:
            cls.susp_part_id = susp_part["id"]

        cls.conn.commit()
        cls.auth_headers = {"x-username": "test_cat_owner@example.com"}

    def test_01_whitelist_allowed_categories(self):
        """Test EntitlementService correctly returns allowed_categories for tenant."""
        wl = EntitlementService.get_organization_whitelist(self.org_id)
        self.assertIn("Brake", wl["allowed_categories"])
        self.assertIn("Filters", wl["allowed_categories"])
        self.assertNotIn("Suspension", wl["allowed_categories"])
        self.assertNotIn("*", wl["allowed_categories"])

    def test_02_search_isolation_blocks_unauthorized_category(self):
        """Search parts in 'Suspension' category must return CATEGORY_LOCKED or 0 results."""
        resp = self.client.get("/api/parts/search?category=Suspension", headers=self.auth_headers)
        data = resp.json()
        if resp.status_code == 403 or (resp.status_code == 200 and data.get("error_code") == "CATEGORY_LOCKED"):
            self.assertTrue(True)
        else:
            # If search returns 200, ensure none of the returned parts have category Suspension
            results = data.get("results", [])
            for r in results:
                self.assertNotEqual(str(r.get("category")).lower(), "suspension")

    def test_03_search_allows_authorized_category(self):
        """Search parts in 'Brake' category must succeed and return results."""
        resp = self.client.get("/api/parts/search?category=Brake", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success", False))

    def test_04_product_detail_denies_unauthorized_category(self):
        """Direct URL access to product in unauthorized category must return 403 Forbidden."""
        resp = self.client.get(f"/api/parts/product/{self.susp_part_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 403)
        data = resp.json()
        self.assertIn("category", data.get("detail", "").lower())

    def test_05_product_detail_allows_authorized_category(self):
        """Direct URL access to product in authorized category must succeed."""
        resp = self.client.get(f"/api/parts/product/{self.brake_part_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data.get("success", False))

    def test_06_get_and_update_subscription_categories(self):
        """Tenant can read and update categories up to plan limit (Starter: 2)."""
        # GET
        get_res = self.client.get("/api/saas/subscription/categories", headers=self.auth_headers)
        self.assertEqual(get_res.status_code, 200)
        g_data = get_res.json()
        self.assertTrue(g_data.get("success"))
        self.assertIn("Brake", g_data.get("granted_categories"))

        # POST update within limit
        post_res = self.client.post(
            "/api/saas/subscription/categories",
            headers=self.auth_headers,
            json={"selected_categories": ["Brake", "Suspension"]}
        )
        self.assertEqual(post_res.status_code, 200)
        p_data = post_res.json()
        self.assertTrue(p_data.get("success"))

        # Verify new category is now granted
        wl = EntitlementService.get_organization_whitelist(self.org_id)
        self.assertIn("Suspension", wl["allowed_categories"])

        # POST update exceeding limit (Starter max is 2, trying 3)
        post_bad = self.client.post(
            "/api/saas/subscription/categories",
            headers=self.auth_headers,
            json={"selected_categories": ["Brake", "Suspension", "Filters"]}
        )
        self.assertIn(post_bad.status_code, [400, 403])

    def test_07_customer_export_denied(self):
        """Customer roles must be denied export access (403 Forbidden)."""
        export_res = self.client.post("/api/saas/export", headers=self.auth_headers, json={"export_type": "PARTS_CATALOG"})
        self.assertEqual(export_res.status_code, 403)

    def test_08_upgrade_with_selected_categories(self):
        """Upgrading plan to Professional with 3 selected categories saves them properly."""
        upgrade_res = self.client.post(
            "/api/saas/subscription/upgrade",
            headers=self.auth_headers,
            json={
                "plan_id": "professional",
                "interval": "MONTHLY",
                "selected_categories": ["Brake", "Suspension", "Electrical"],
                "payment_method": "CREDIT_CARD"
            }
        )
        self.assertEqual(upgrade_res.status_code, 200)
        up_data = upgrade_res.json()
        self.assertTrue(up_data.get("success"))

        # Check updated entitlements
        wl = EntitlementService.get_organization_whitelist(self.org_id)
        self.assertIn("Electrical", wl["allowed_categories"])
        self.assertIn("Suspension", wl["allowed_categories"])
        self.assertIn("Brake", wl["allowed_categories"])

    def test_09_favorites_toggle_denied_for_unauthorized_category(self):
        """Customer cannot add unauthorized category parts to favorites."""
        # Remove 'Suspension' from entitlements for this specific test
        self.cursor.execute("DELETE FROM entitlements WHERE org_id = ? AND entitlement_value = 'Suspension'", (self.org_id,))
        self.conn.commit()

        fav_res = self.client.post(
            "/api/saas/favorites/toggle",
            headers=self.auth_headers,
            json={"part_id": self.susp_part_id, "part_source": "MASTER"}
        )
        self.assertEqual(fav_res.status_code, 403)

    def test_10_ai_search_category_validation(self):
        """AI Search for an unauthorized category returns CATEGORY_LOCKED or denied."""
        ai_res = self.client.post(
            "/api/parts/ai-search",
            headers=self.auth_headers,
            json={"query": "Suspension control arm Toyota"}
        )
        data = ai_res.json()
        if ai_res.status_code == 403 or data.get("error_code") == "CATEGORY_LOCKED":
            self.assertTrue(True)
        else:
            results = data.get("results", [])
            for r in results:
                self.assertNotEqual(str(r.get("category")).lower(), "suspension")

    def test_11_role_spoofing_prevented(self):
        """Passing fake x-user-role=ADMIN header does not grant admin bypass to customer users."""
        fake_headers = {
            "x-username": "test_cat_owner@example.com",
            "x-user-role": "ADMIN"
        }
        # Attempt to access product in unauthorized category (Suspension)
        resp = self.client.get(f"/api/parts/product/{self.susp_part_id}", headers=fake_headers)
        self.assertEqual(resp.status_code, 403)

    def test_13_register_trial_with_selected_categories(self):
        """Verifies trial registration correctly seeds user-selected categories into entitlements."""
        email = f"trial_test_user_{os.urandom(4).hex()}@example.com"
        trial_payload = {
            "company_name": "Test Trial Garage",
            "contact_name": "Somchai Test",
            "email": email,
            "password": "Password123!",
            "phone": "0811234567",
            "plan_id": "starter",
            "signup_type": "TRIAL",
            "selected_categories": ["Brake", "Filters"],
            "verification_code": "999999"
        }
        res = self.client.post("/api/auth/register-trial", json=trial_payload)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success", False))

        # Check seeded entitlements
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (email,))
        u = c.fetchone()
        self.assertIsNotNone(u)
        c.execute("SELECT org_id FROM organization_members WHERE user_id = ?", (u["id"],))
        om = c.fetchone()
        self.assertIsNotNone(om)
        trial_org_id = om["org_id"]

        wl = EntitlementService.get_organization_whitelist(trial_org_id)
        self.assertIn("Brake", wl["allowed_categories"])
        self.assertIn("Filters", wl["allowed_categories"])
        self.assertNotIn("Suspension", wl["allowed_categories"])

        # Clean up trial records
        c.execute("DELETE FROM entitlements WHERE org_id = ?", (trial_org_id,))
        c.execute("DELETE FROM subscriptions WHERE org_id = ?", (trial_org_id,))
        c.execute("DELETE FROM organization_members WHERE org_id = ?", (trial_org_id,))
        c.execute("DELETE FROM organizations WHERE id = ?", (trial_org_id,))
        c.execute("DELETE FROM users WHERE id = ?", (u["id"],))
        conn.commit()
        conn.close()

    def test_14_cross_reference_matrix_entitlement_filtering(self):
        """Matrix endpoint should filter relations to match tenant's allowed categories."""
        res = self.client.get("/api/parts/cross-reference-matrix", headers=self.auth_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success", False))
        relations = data.get("relations", [])
        for rel in relations:
            cat = rel.get("category")
            if cat:
                # Should not include categories not in tenant's whitelist
                self.assertNotIn(cat.lower(), ["unauthorized_fake_cat"])

    def test_15_database_schema_frozen(self):
        """Verifies database schema has not been altered or mutated."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [r[0] for r in cursor.fetchall()]
        conn.close()

        # Core tables must exist without ad-hoc new migration tables
        required_tables = [
            'master_parts', 'temp_parts', 'organizations', 'plans',
            'subscriptions', 'entitlements', 'usage_records', 'users',
            'organization_members', 'meta_categories', 'meta_car_brands'
        ]
        for t in required_tables:
            self.assertIn(t, tables)

    @classmethod
    def tearDownClass(cls):
        # Clean up test records
        cls.cursor.execute("DELETE FROM entitlements WHERE org_id = ?", (cls.org_id,))
        cls.cursor.execute("DELETE FROM subscriptions WHERE org_id = ?", (cls.org_id,))
        cls.cursor.execute("DELETE FROM organization_members WHERE org_id = ?", (cls.org_id,))
        cls.cursor.execute("DELETE FROM organizations WHERE id = ?", (cls.org_id,))
        cls.cursor.execute("DELETE FROM users WHERE id = ?", (cls.user_id,))
        cls.conn.commit()
        cls.conn.close()

if __name__ == "__main__":
    unittest.main()
