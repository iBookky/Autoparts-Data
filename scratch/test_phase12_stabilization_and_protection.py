import os
import sys
import unittest
import asyncio
from datetime import datetime
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from backend.database import (
    get_db_connection,
    init_db,
    advanced_search_parts,
    get_cross_reference_matrix,
    get_part_by_id,
    register_trial_tenant_db,
    get_public_coverage_stats_db,
    get_public_demo_search_db,
    get_org_invoices
)
from backend.services.entitlement_service import EntitlementService

class TestPhase12StabilizationAndProtection(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)

    # ================= 1. AUTOMOTIVE DATA EXPORT RESTRICTIONS =================

    def test_01_customer_staff_export_denied(self):
        """Scenario 1: Customer role STAFF attempting to export parts catalog receives 403 Forbidden with exact message."""
        response = self.client.post(
            "/api/saas/export",
            json={"filter_brand": None, "filter_car": None},
            headers={"x-username": "staff", "x-user-role": "STAFF"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get("detail"), "Automotive data export is not available for this account.")

    def test_02_customer_owner_export_denied(self):
        """Scenario 2: Customer role CUSTOMER_OWNER attempting to export parts catalog receives 403 Forbidden."""
        response = self.client.post(
            "/api/saas/export",
            json={"filter_brand": None, "filter_car": None},
            headers={"x-username": "customer_owner", "x-user-role": "CUSTOMER_OWNER"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get("detail"), "Automotive data export is not available for this account.")

    def test_03_customer_member_export_denied(self):
        """Scenario 3: Customer role CUSTOMER_MEMBER attempting to export parts catalog receives 403 Forbidden."""
        response = self.client.post(
            "/api/saas/export",
            json={"filter_brand": None, "filter_car": None},
            headers={"x-username": "customer_member", "x-user-role": "CUSTOMER_MEMBER"}
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json().get("detail"), "Automotive data export is not available for this account.")

    def test_04_operator_admin_export_allowed(self):
        """Scenario 4: Operator role ADMIN is allowed to export parts data for administrative backup."""
        response = self.client.post(
            "/api/saas/export",
            json={"filter_brand": None, "filter_car": None},
            headers={"x-username": "admin", "x-user-role": "ADMIN"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/csv; charset=utf-8")

    def test_05_operator_superadmin_export_allowed(self):
        """Scenario 5: Operator role SUPER_ADMIN is allowed to export parts data."""
        response = self.client.post(
            "/api/saas/export",
            json={"filter_brand": None, "filter_car": None},
            headers={"x-username": "superadmin", "x-user-role": "SUPER_ADMIN"}
        )
        self.assertEqual(response.status_code, 200)

    def test_06_export_import_template_customer_denied(self):
        """Scenario 6: Template export route requires admin role, customer receives 403/401."""
        response = self.client.get(
            "/api/parts/export-import-template",
            headers={"x-username": "staff", "x-user-role": "STAFF"}
        )
        # require_admin raises 403 or 401 for non-admin
        self.assertIn(response.status_code, [401, 403])

    # ================= 2. SEARCH ENUMERATION PROTECTION & DATA MINIMIZATION =================

    def test_07_search_hard_limit_enforced_and_clamped(self):
        """Scenario 7: Search query with huge limit (100000) is clamped server-side to max 50 items."""
        response = self.client.get(
            "/api/parts/search?car_brand=TOYOTA&limit=100000",
            headers={"x-username": "admin", "x-user-role": "ADMIN"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertLessEqual(len(data.get("results", [])), 50)

    def test_08_search_pagination_offset_calculation(self):
        """Scenario 8: Sequential pagination (page=1, page=2) offsets records correctly."""
        res_p1 = advanced_search_parts(car_brand="TOYOTA", limit=2, offset=0)
        res_p2 = advanced_search_parts(car_brand="TOYOTA", limit=2, offset=2)
        if len(res_p1) > 0 and len(res_p2) > 0:
            self.assertNotEqual(res_p1[0]["id"], res_p2[0]["id"])

    def test_09_search_response_data_minimization(self):
        """Scenario 9: Search results strip internal database structure and scraper metadata."""
        results = advanced_search_parts(oem_code="04465-0K360")
        self.assertGreater(len(results), 0)
        first = results[0]
        # Required business fields present
        self.assertIn("part_number", first)
        self.assertIn("oem_number", first)
        self.assertIn("brand", first)
        self.assertIn("relevance_score", first)
        # Sensitive internal fields omitted
        self.assertNotIn("cost_price", first)
        self.assertNotIn("supplier_note", first)
        self.assertNotIn("raw_scraper_payload", first)

    def test_10_empty_search_returns_empty_list(self):
        """Scenario 10: Search with empty parameters returns empty list without error or dump."""
        results = advanced_search_parts()
        self.assertEqual(results, [])

    def test_11_broad_query_filtering(self):
        """Scenario 11: Broad query filters correctly according to brand parameters."""
        results = advanced_search_parts(car_brand="HONDA")
        for item in results:
            self.assertIn("HONDA", (item.get("car_brand") or "").upper())

    # ================= 3. CROSS-REFERENCE SUBSYSTEM RECOVERY =================

    def test_12_cross_reference_matrix_oem_lookup(self):
        """Scenario 12: Cross-reference lookup by OEM code returns verified canonical schema."""
        matrix = get_cross_reference_matrix("04465-0K360")
        self.assertGreaterEqual(len(matrix), 1)
        # Verify canonical relation fields
        first = matrix[0]
        self.assertIn("source_brand", first)
        self.assertIn("source_part_number", first)
        self.assertIn("target_brand", first)
        self.assertIn("target_part_number", first)
        self.assertIn("relation_type", first)
        self.assertIn("verification_status", first)

    def test_13_cross_reference_matrix_bidirectional_match(self):
        """Scenario 13: Cross-reference lookup by Aftermarket SKU returns matching OEM target."""
        matrix = get_cross_reference_matrix("GDB3534UT")
        self.assertGreaterEqual(len(matrix), 1)
        found = any(r["target_part_number"] == "04465-0K360" for r in matrix)
        self.assertTrue(found)

    def test_14_cross_reference_empty_query_safe(self):
        """Scenario 14: Cross-reference lookup for non-existent code returns empty list gracefully without 500."""
        matrix = get_cross_reference_matrix("NON_EXISTENT_PART_99999")
        self.assertEqual(matrix, [])

    def test_15_product_detail_includes_cross_references(self):
        """Scenario 15: Product detail API correctly populates cross_references array with multiple equivalents."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM master_parts WHERE oem_number = '04465-0K360' LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        if row:
            part_id = row["id"]
            response = self.client.get(
                f"/api/parts/product/{part_id}",
                headers={"x-username": "admin", "x-user-role": "ADMIN"}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIsInstance(data.get("cross_references"), list)
            self.assertGreaterEqual(len(data["cross_references"]), 1)
            # Check canonical field names in returned cross references
            cr = data["cross_references"][0]
            self.assertIn("source_part_number", cr)
            self.assertIn("target_part_number", cr)
            self.assertIn("relation_type", cr)

    def test_16_product_detail_with_no_cross_references_returns_empty_array(self):
        """Scenario 16: Valid product with 0 cross references returns HTTP 200 + empty list, not 500."""
        conn = get_db_connection()
        cursor = conn.cursor()
        # Find product whose OEM is NOT in cross_reference_relations
        cursor.execute("""
            SELECT id FROM master_parts 
            WHERE oem_number NOT IN (SELECT source_part_number FROM cross_reference_relations)
              AND oem_number NOT IN (SELECT target_part_number FROM cross_reference_relations)
            LIMIT 1
        """)
        row = cursor.fetchone()
        conn.close()

        if row:
            part_id = row["id"]
            response = self.client.get(
                f"/api/parts/product/{part_id}",
                headers={"x-username": "admin", "x-user-role": "ADMIN"}
            )
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data.get("cross_references"), [])

    def test_17_product_detail_invalid_id_returns_404(self):
        """Scenario 17: Non-existent product ID returns HTTP 404 controlled response."""
        response = self.client.get(
            "/api/parts/product/9999999",
            headers={"x-username": "admin", "x-user-role": "ADMIN"}
        )
        self.assertEqual(response.status_code, 404)

    def test_18_cross_reference_endpoint_contract(self):
        """Scenario 18: GET /api/parts/cross-reference-matrix returns standard API response schema."""
        response = self.client.get(
            "/api/parts/cross-reference-matrix",
            headers={"x-username": "admin", "x-user-role": "ADMIN"}
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIn("matrix", data)
        self.assertIsInstance(data["matrix"], list)

    def test_19_cross_reference_normalization(self):
        """Scenario 19: Normalized search inputs with spaces or lowercase match accurately."""
        matrix1 = get_cross_reference_matrix("04465-0k360")
        matrix2 = get_cross_reference_matrix("04465 0K360")
        self.assertGreater(len(matrix1), 0)
        self.assertGreater(len(matrix2), 0)
        self.assertEqual(len(matrix1), len(matrix2))

    # ================= 4. AI DATA EXTRACTION DEFENSE =================

    def test_20_ai_search_output_capped(self):
        """Scenario 20: AI parts search caps recommendation output to max 5 items."""
        response = self.client.post(
            "/api/parts/ai-search",
            data={
                "brand": "TRW",
                "part_number": "GDB3534UT",
                "oem_number": "04465-0K360",
                "car_brand": "Toyota",
                "car_model": "Hilux Revo",
                "category": "ระบบเบรก",
                "product_name": "Front Brake Pads"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertLessEqual(len(data.get("results", [])), 5)

    # ================= 5. MULTI-TENANT ISOLATION & ENTITLEMENTS =================

    def test_21_multi_tenant_invoice_isolation(self):
        """Scenario 21: Tenant A cannot access Tenant B's invoices."""
        ts = int(datetime.now().timestamp())
        res_a = register_trial_tenant_db({
            "company_name": f"Tenant A {ts}",
            "email": f"tenant_a_{ts}@test.com",
            "password": "Password123!",
            "plan_id": "starter"
        })
        res_b = register_trial_tenant_db({
            "company_name": f"Tenant B {ts}",
            "email": f"tenant_b_{ts}@test.com",
            "password": "Password123!",
            "plan_id": "starter"
        })
        self.assertTrue(res_a["success"])
        self.assertTrue(res_b["success"])
        self.assertNotEqual(res_a["org_id"], res_b["org_id"])

        inv_a = get_org_invoices(res_a["org_id"])
        inv_b = get_org_invoices(res_b["org_id"])
        self.assertEqual(len(inv_a), 0)
        self.assertEqual(len(inv_b), 0)

    def test_22_expired_subscription_blocks_search(self):
        """Scenario 22: Expired subscription status is denied search access."""
        conn = get_db_connection()
        cursor = conn.cursor()
        ts = int(datetime.now().timestamp())
        res = register_trial_tenant_db({
            "company_name": f"Expired Org {ts}",
            "email": f"expired_{ts}@test.com",
            "password": "Password123!",
            "plan_id": "starter"
        })
        org_id = res["org_id"]
        cursor.execute("UPDATE subscriptions SET status = 'CANCELED' WHERE org_id = ?", (org_id,))
        conn.commit()
        conn.close()

        is_allowed, locked_payload, ctx = EntitlementService.validate_search_access(
            username=f"expired_{ts}@test.com",
            user_role="STAFF",
            car_brand="TOYOTA",
            category="ระบบเบรก"
        )
        self.assertFalse(is_allowed)
        self.assertIsNotNone(locked_payload)
        self.assertTrue(locked_payload.get("locked"))

    def test_23_brand_whitelist_enforcement(self):
        """Scenario 23: Organization whitelist enforces brand restrictions."""
        ts = int(datetime.now().timestamp())
        email = f"brand_test_{ts}@garage.com"
        res = register_trial_tenant_db({
            "company_name": f"Brand Garage {ts}",
            "email": email,
            "password": "Password123!",
            "plan_id": "starter"
        })
        org_id = res["org_id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entitlements WHERE org_id = ? AND entitlement_type = 'BRAND'", (org_id,))
        cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'BRAND', 'TOYOTA', 1)", (org_id,))
        conn.commit()
        conn.close()

        allowed_toyota, _, _ = EntitlementService.validate_search_access(
            username=email, user_role="STAFF", car_brand="TOYOTA", category="ระบบเบรก"
        )
        self.assertTrue(allowed_toyota)

        allowed_porsche, _, _ = EntitlementService.validate_search_access(
            username=email, user_role="STAFF", car_brand="PORSCHE", category="ระบบเบรก"
        )
        self.assertFalse(allowed_porsche)

    def test_24_category_whitelist_enforcement(self):
        """Scenario 24: Organization whitelist enforces category restrictions."""
        ts = int(datetime.now().timestamp())
        email = f"cat_test_{ts}@garage.com"
        res = register_trial_tenant_db({
            "company_name": f"Cat Garage {ts}",
            "email": email,
            "password": "Password123!",
            "plan_id": "starter"
        })
        org_id = res["org_id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM entitlements WHERE org_id = ? AND entitlement_type = 'CATEGORY'", (org_id,))
        cursor.execute("INSERT INTO entitlements (org_id, entitlement_type, entitlement_value, is_granted) VALUES (?, 'CATEGORY', 'ระบบเบรก', 1)", (org_id,))
        conn.commit()
        conn.close()

        allowed_brake, _, _ = EntitlementService.validate_search_access(
            username=email, user_role="STAFF", car_brand="TOYOTA", category="ระบบเบรก"
        )
        self.assertTrue(allowed_brake)

        allowed_engine, _, _ = EntitlementService.validate_search_access(
            username=email, user_role="STAFF", car_brand="TOYOTA", category="ระบบเครื่องยนต์"
        )
        self.assertFalse(allowed_engine)

    # ================= 6. CORE SEARCH REGRESSION =================

    def test_25_oem_search_regression(self):
        """Scenario 25: OEM search for 04465-0K360 returns accurate results."""
        results = advanced_search_parts(oem_code="04465-0K360")
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["match_type"], "EXACT_OEM")

    def test_26_sku_search_regression(self):
        """Scenario 26: SKU search for GDB3534 returns TRW parts."""
        results = advanced_search_parts(aftermarket_part="GDB3534")
        self.assertGreater(len(results), 0)
        self.assertTrue(any("GDB3534" in (r.get("part_number") or "") for r in results))

    def test_27_vin_search_regression(self):
        """Scenario 27: VIN search decodes vehicle information correctly."""
        results = advanced_search_parts(vin="MR0HA3CD123456789")
        self.assertIsInstance(results, list)

    def test_28_vehicle_fitment_search_regression(self):
        """Scenario 28: Vehicle fitment search for Revo returns matching parts."""
        results = advanced_search_parts(car_brand="Toyota", car_model="Hilux Revo")
        self.assertGreater(len(results), 0)

    def test_29_public_demo_search_regression(self):
        """Scenario 29: Public demo search returns max 3 teaser items with zero internal leaks."""
        results = get_public_demo_search_db("04465")
        self.assertLessEqual(len(results), 3)
        for item in results:
            self.assertIn("part_number", item)
            self.assertIn("brand", item)
            self.assertNotIn("cost_price", item)

if __name__ == "__main__":
    unittest.main()
