import unittest
from fastapi.testclient import TestClient
from main import app
from backend.database import advanced_search_parts, register_trial_tenant_db

class TestLocalFirstSearchAndRegistration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_multi_token_car_model_search(self):
        """Verify searching compound model string matches both Hilux and Fortuner across master and temp."""
        results = advanced_search_parts(car_brand='TOYOTA', car_model='HiLux / Fortuner')
        self.assertGreater(len(results), 0)
        models = [r.get('car_model') for r in results]
        # Must match Fortuner from master or Hilux Vigo from temp
        self.assertTrue(any('Fortuner' in m for m in models if m))
        self.assertTrue(any('Hilux' in m for m in models if m))

    def test_live_search_local_db_first_priority(self):
        """Verify /api/parts/live-search checks local DB first before external scraping."""
        # 04465-0K090 is in temp_parts
        res = self.client.post("/api/parts/live-search", data={"q": "04465-0K090"})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("source"), "DATABASE_LOCAL")
        self.assertEqual(data.get("search_tier"), "LOCAL_FIRST")
        self.assertGreater(data.get("total"), 0)

    def test_registration_password_length_validation(self):
        """Verify registration rejects passwords shorter than 6 characters."""
        payload = {
            "company_name": "Short Pwd Garage",
            "email": "short_pwd_test@example.com",
            "password": "123", # < 6 chars
            "signup_type": "TRIAL"
        }
        res = register_trial_tenant_db(payload)
        self.assertFalse(res.get("success"))
        self.assertIn("6 ตัวอักษร", res.get("error", ""))

if __name__ == '__main__':
    unittest.main()
