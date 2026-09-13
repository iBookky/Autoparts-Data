import unittest
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

class TestOwnerMembersAndVinSearch(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.owner_headers = {
            "x-username": "owner",
            "x-user-role": "OWNER"
        }

    def test_owner_tabs_return_real_data(self):
        """Verify all owner cockpit analytics endpoints return 200 without PostgreSQL date/group by crashes."""
        endpoints = [
            "/api/owner/overview",
            "/api/owner/revenue?days=30",
            "/api/owner/financial-summary",
            "/api/owner/customers",
            "/api/owner/subscriptions",
            "/api/owner/search-analytics",
            "/api/owner/opportunities",
            "/api/owner/plans-performance",
            "/api/owner/plans",
            "/api/owner/addons",
            "/api/owner/pipeline",
            "/api/owner/roles",
            "/api/owner/audit-logs",
            "/api/owner/ai/overview",
            "/api/owner/ai/models",
            "/api/owner/ai/keys",
            "/api/owner/ai/skills",
            "/api/owner/settings/branding",
            "/api/owner/settings/company",
            "/api/owner/settings/invoice",
            "/api/owner/payment-settings"
        ]
        for ep in endpoints:
            res = self.client.get(ep, headers=self.owner_headers)
            self.assertEqual(res.status_code, 200, f"Endpoint {ep} failed with status {res.status_code}: {res.text}")
            data = res.json()
            self.assertTrue(data.get("success", False), f"Endpoint {ep} did not return success=True")

    def test_owner_customer_toggle_active(self):
        """Test toggling customer active/suspended status."""
        cust_res = self.client.get("/api/owner/customers", headers=self.owner_headers)
        self.assertEqual(cust_res.status_code, 200)
        customers = cust_res.json().get("customers", [])
        self.assertTrue(len(customers) > 0)
        
        target_cust = next((c for c in customers if c["id"] != 1), customers[0])
        org_id = target_cust["id"]

        # Toggle to suspended
        res = self.client.post(f"/api/owner/customers/{org_id}/toggle-active", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json()["success"])

        # Toggle back
        res_back = self.client.post(f"/api/owner/customers/{org_id}/toggle-active", headers=self.owner_headers)
        self.assertEqual(res_back.status_code, 200)
        self.assertTrue(res_back.json()["success"])

    def test_owner_member_crud(self):
        """Test full CRUD operations for members in Owner Cockpit."""
        # 1. List members
        res = self.client.get("/api/owner/members", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        members = res.json().get("members", [])
        self.assertTrue(len(members) >= 1)

        # 2. Create member
        test_username = "member_test_crud@example.com"
        create_payload = {
            "username": test_username,
            "email": test_username,
            "password": "Password123!",
            "role": "STAFF",
            "org_id": 1,
            "org_role": "STAFF"
        }
        res_create = self.client.post("/api/owner/members", json=create_payload, headers=self.owner_headers)
        self.assertEqual(res_create.status_code, 200)
        user_id = res_create.json().get("user_id")
        self.assertIsNotNone(user_id)

        # 3. Update member
        res_update = self.client.put(f"/api/owner/members/{user_id}", json={
            "username": test_username,
            "email": "updated_" + test_username,
            "role": "ADMIN",
            "is_active": 1
        }, headers=self.owner_headers)
        self.assertEqual(res_update.status_code, 200)

        # 4. Toggle member active/suspended
        res_toggle = self.client.post(f"/api/owner/members/{user_id}/toggle-active", headers=self.owner_headers)
        self.assertEqual(res_toggle.status_code, 200)
        self.assertEqual(res_toggle.json().get("is_active"), 0)

        res_toggle_back = self.client.post(f"/api/owner/members/{user_id}/toggle-active", headers=self.owner_headers)
        self.assertEqual(res_toggle_back.status_code, 200)
        self.assertEqual(res_toggle_back.json().get("is_active"), 1)

        # 5. Delete member
        res_delete = self.client.delete(f"/api/owner/members/{user_id}", headers=self.owner_headers)
        self.assertEqual(res_delete.status_code, 200)
        self.assertTrue(res_delete.json()["success"])

    def test_vin_decoding_and_search(self):
        """Test that VIN MR0ZZ69G803102002 decodes and searches real matching automotive parts."""
        # 1. Decode VIN
        vin = "MR0ZZ69G803102002"
        res_dec = self.client.get(f"/api/parts/decode-vin?vin={vin}", headers=self.owner_headers)
        self.assertEqual(res_dec.status_code, 200)
        data_dec = res_dec.json()
        self.assertTrue(data_dec["success"])
        specs = data_dec["results"]
        self.assertEqual(specs["brand"].upper(), "TOYOTA")
        self.assertIn("FORTUNER", specs["model"].upper())

        # 2. Search parts by VIN
        res_search = self.client.get(f"/api/parts/search?vin={vin}", headers=self.owner_headers)
        self.assertEqual(res_search.status_code, 200)
        data_search = res_search.json()
        self.assertTrue(data_search["success"])
        results = data_search.get("results", [])
        self.assertTrue(len(results) > 0, "VIN search should return matching parts")
        
        # Check that parts match Toyota vehicle fitment
        for r in results:
            self.assertEqual(r["car_brand"].upper(), "TOYOTA")

    def test_oem_and_sku_parts_lookup(self):
        """Test searching with OEM 04465-0K360 and SKU GDB3534UT returns matching cross-reference parts."""
        res_oem = self.client.get("/api/parts/search?oem_code=04465-0K360", headers=self.owner_headers)
        self.assertEqual(res_oem.status_code, 200)
        self.assertTrue(len(res_oem.json().get("results", [])) > 0)

        res_sku = self.client.get("/api/parts/search?aftermarket_part=GDB3534UT", headers=self.owner_headers)
        self.assertEqual(res_sku.status_code, 200)
        self.assertTrue(len(res_sku.json().get("results", [])) > 0)

if __name__ == "__main__":
    unittest.main()
