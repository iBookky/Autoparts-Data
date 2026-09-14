import unittest
from fastapi.testclient import TestClient
from main import app
from backend import database as db
from backend.services.billing_calculator import BillingCalculator

class TestOwnerAddonSaleToggle(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Ensure default clean state for tests
        db.set_addons_global_sale(True)

    def tearDown(self):
        # Restore clean state
        db.set_addons_global_sale(True)

    def test_database_global_sale_toggle(self):
        # Disable global sale
        res = db.set_addons_global_sale(False)
        self.assertTrue(res)

        # Check in get_all_add_ons
        addons = db.get_all_add_ons(include_inactive=True)
        self.assertTrue(len(addons) > 0)
        for a in addons:
            self.assertFalse(a.get("is_for_sale"), "All add-ons should have is_for_sale=False when global sale is disabled")

        # Enable global sale back
        res2 = db.set_addons_global_sale(True)
        self.assertTrue(res2)
        addons2 = db.get_all_add_ons(include_inactive=True)
        active_found = False
        for a in addons2:
            if a.get("status") == "ACTIVE":
                self.assertTrue(a.get("is_for_sale"))
                active_found = True
        self.assertTrue(active_found)

    def test_database_individual_addon_toggle(self):
        addons = db.get_all_add_ons(include_inactive=True)
        self.assertTrue(len(addons) > 0)
        target_addon = addons[0]
        addon_id = target_addon["id"]
        original_status = target_addon["status"]

        # Toggle status
        toggle_res = db.toggle_addon_sale_status(addon_id)
        self.assertTrue(toggle_res.get("success"))
        expected_status = "DISABLED" if original_status == "ACTIVE" else "ACTIVE"
        self.assertEqual(toggle_res.get("new_status"), expected_status)

        # Verify through get_all_add_ons
        updated_addons = {a["id"]: a for a in db.get_all_add_ons(include_inactive=True)}
        self.assertEqual(updated_addons[addon_id]["status"], expected_status)

        # Toggle back
        restore_res = db.toggle_addon_sale_status(addon_id, original_status)
        self.assertTrue(restore_res.get("success"))
        self.assertEqual(restore_res.get("new_status"), original_status)

    def test_billing_calculator_respects_sale_status(self):
        addons = db.get_all_add_ons(include_inactive=True)
        self.assertTrue(len(addons) >= 2)
        a1, a2 = addons[0], addons[1]

        # Case 1: Both active, global sale enabled
        db.set_addons_global_sale(True)
        db.toggle_addon_sale_status(a1["id"], "ACTIVE")
        db.toggle_addon_sale_status(a2["id"], "ACTIVE")

        subtotal, selected = BillingCalculator.calculate_add_ons([a1["id"], a2["id"]], "MONTHLY")
        self.assertEqual(len(selected), 2)
        self.assertEqual(subtotal, a1["price_monthly"] + a2["price_monthly"])

        # Case 2: One addon DISABLED -> ignored in checkout calculation
        db.toggle_addon_sale_status(a2["id"], "DISABLED")
        subtotal2, selected2 = BillingCalculator.calculate_add_ons([a1["id"], a2["id"]], "MONTHLY")
        self.assertEqual(len(selected2), 1)
        self.assertEqual(selected2[0]["id"], a1["id"])
        self.assertEqual(subtotal2, a1["price_monthly"])

        # Case 3: Global sale DISABLED -> all addons ignored
        db.set_addons_global_sale(False)
        subtotal3, selected3 = BillingCalculator.calculate_add_ons([a1["id"], a2["id"]], "MONTHLY")
        self.assertEqual(len(selected3), 0)
        self.assertEqual(subtotal3, 0.0)

        # Restore
        db.set_addons_global_sale(True)
        db.toggle_addon_sale_status(a1["id"], "ACTIVE")
        db.toggle_addon_sale_status(a2["id"], "ACTIVE")

    def test_api_owner_endpoints_rbac(self):
        addons = db.get_all_add_ons(include_inactive=True)
        addon_id = addons[0]["id"]

        # 1. Non-owner (CUSTOMER role) should receive 403 Forbidden
        cust_headers = {"X-User-Role": "CUSTOMER", "X-Username": "customer_test"}
        
        resp_global = self.client.post("/api/owner/addons/toggle-global-sale", json={"enabled": False}, headers=cust_headers)
        self.assertEqual(resp_global.status_code, 403)

        resp_addon = self.client.post(f"/api/owner/addons/{addon_id}/toggle-sale", json={"status": "DISABLED"}, headers=cust_headers)
        self.assertEqual(resp_addon.status_code, 403)

        # 2. Owner should receive 200 OK
        owner_headers = {"X-User-Role": "OWNER", "X-Username": "owner_admin"}

        resp_global_ok = self.client.post("/api/owner/addons/toggle-global-sale", json={"enabled": False}, headers=owner_headers)
        self.assertEqual(resp_global_ok.status_code, 200)
        self.assertFalse(resp_global_ok.json().get("addons_sale_enabled"))

        # Verify in public api/saas/plans
        plans_resp = self.client.get("/api/saas/plans")
        self.assertEqual(plans_resp.status_code, 200)
        self.assertFalse(plans_resp.json().get("addons_sale_enabled"))

        # Owner re-enables global sale
        resp_global_ok2 = self.client.post("/api/owner/addons/toggle-global-sale", json={"enabled": True}, headers=owner_headers)
        self.assertEqual(resp_global_ok2.status_code, 200)
        self.assertTrue(resp_global_ok2.json().get("addons_sale_enabled"))

        # Owner toggles individual addon
        resp_toggle_ok = self.client.post(f"/api/owner/addons/{addon_id}/toggle-sale", json={}, headers=owner_headers)
        self.assertEqual(resp_toggle_ok.status_code, 200)
        self.assertTrue(resp_toggle_ok.json().get("success"))

        # Restore individual addon
        self.client.post(f"/api/owner/addons/{addon_id}/toggle-sale", json={"status": "ACTIVE"}, headers=owner_headers)


if __name__ == "__main__":
    unittest.main()
