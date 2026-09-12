import unittest
from fastapi.testclient import TestClient
from main import app
from backend.services.entitlement_service import EntitlementService
from backend.database import get_user_tenant_context

class TestOwnerUnrestrictedAccess(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_owner_validate_search_access(self):
        """Verify EntitlementService grants unrestricted search access to OWNER without locks."""
        allowed, locked, ctx = EntitlementService.validate_search_access(
            username="owner",
            user_role="OWNER",
            car_brand="FERRARI_TEST",
            category="RANDOM_UNPURCHASED_CATEGORY",
            aftermarket_brand="RANDOM_AFTERMARKET"
        )
        self.assertTrue(allowed)
        self.assertIsNone(locked)
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["subscription"]["plan_name"], "SYSTEM OWNER (UNLIMITED)")
        self.assertEqual(ctx["usage"]["searches_quota"], 999999999)

    def test_owner_validate_product_access(self):
        """Verify EntitlementService grants unrestricted product view access to OWNER."""
        allowed, locked = EntitlementService.validate_product_access(
            username="owner",
            user_role="OWNER",
            part_id=999999,
            source="MASTER"
        )
        self.assertTrue(allowed)
        self.assertIsNone(locked)

    def test_owner_tenant_context(self):
        """Verify get_user_tenant_context returns unlimited Enterprise status for OWNER."""
        ctx = get_user_tenant_context("owner")
        self.assertIsNotNone(ctx)
        self.assertEqual(ctx["user"]["role"], "OWNER")
        self.assertEqual(ctx["organization"]["org_role"], "OWNER")
        self.assertEqual(ctx["organization"]["plan_tier"], "ENTERPRISE")
        self.assertEqual(ctx["subscription"]["monthly_search_quota"], 999999999)
        self.assertEqual(ctx["subscription"]["max_brands"], -1)
        self.assertEqual(ctx["subscription"]["max_categories"], -1)
        self.assertEqual(ctx["subscription"]["max_users"], -1)
        self.assertEqual(ctx["subscription"]["export_enabled"], 1)

    def test_owner_api_search_endpoint(self):
        """Verify GET /api/parts/search for OWNER never returns commercial locked response."""
        res = self.client.get(
            "/api/parts/search?car_brand=TOYOTA&category=ANY",
            headers={"x-username": "owner", "x-user-role": "OWNER"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertFalse(data.get("locked", False))
        self.assertEqual(data.get("usage", {}).get("searches_quota"), 999999999)

    def test_owner_api_export_endpoint(self):
        """Verify POST /api/saas/export succeeds for OWNER role."""
        res = self.client.post(
            "/api/saas/export",
            headers={"x-username": "owner", "x-user-role": "OWNER"},
            json={"filter_brand": "", "filter_car": ""}
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/csv", res.headers.get("content-type", ""))
        self.assertIn("autoparts_export", res.headers.get("content-disposition", ""))

if __name__ == "__main__":
    unittest.main()
