import os
import sys
import unittest
from fastapi.testclient import TestClient

# Ensure root directory is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import app
from backend.database import get_db_connection, init_db

class TestOwnerAiEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        
        # Test auth headers
        cls.owner_headers = {"X-User-Role": "OWNER", "X-Username": "boss_owner", "X-User-Id": "1"}
        cls.superadmin_headers = {"X-User-Role": "SUPER_ADMIN", "X-Username": "sys_admin", "X-User-Id": "2"}
        cls.admin_headers = {"X-User-Role": "ADMIN", "X-Username": "parts_admin", "X-User-Id": "3"}
        cls.customer_headers = {"X-User-Role": "CUSTOMER", "X-Username": "buyer_cust", "X-User-Id": "4"}

    def test_01_rbac_protection(self):
        """Verify non-owner/non-superadmin cannot access /api/owner/ai/*"""
        # Customer access
        res = self.client.get("/api/owner/ai/overview", headers=self.customer_headers)
        self.assertEqual(res.status_code, 403)

        # Admin access (only OWNER and SUPER_ADMIN allowed)
        res = self.client.get("/api/owner/ai/overview", headers=self.admin_headers)
        self.assertEqual(res.status_code, 403)

        # Owner access
        res = self.client.get("/api/owner/ai/overview", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)

        # SuperAdmin access
        res = self.client.get("/api/owner/ai/overview", headers=self.superadmin_headers)
        self.assertEqual(res.status_code, 200)

    def test_02_get_ai_overview(self):
        """Verify AI overview metrics structure"""
        res = self.client.get("/api/owner/ai/overview", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        analytics = data.get("analytics", {})
        self.assertIn("active_models_count", analytics)
        self.assertIn("total_calls", analytics)
        self.assertIn("total_tokens", analytics)
        self.assertIn("total_cost_usd", analytics)
        self.assertIn("total_cost_thb", analytics)
        self.assertIn("model_usage", analytics)
        self.assertIn("capability_breakdown", analytics)
        self.assertIn("recent_logs", analytics)

    def test_03_ai_models_crud(self):
        """Test full CRUD lifecycle for AI models"""
        # 1. List models
        res = self.client.get("/api/owner/ai/models", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        initial_models = res.json().get("models", [])
        self.assertIsInstance(initial_models, list)

        # 2. Add new model
        payload = {
            "provider": "Custom",
            "model_name": "Test LLM Auto 1.0",
            "model_id": "test-llm-auto-1",
            "max_tokens": 4096,
            "cost_per_1k_tokens": 0.0002
        }
        res = self.client.post("/api/owner/ai/models", json=payload, headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        created_id = data.get("model_id")
        self.assertIsNotNone(created_id)

        # 3. Update model
        update_payload = {
            "model_name": "Test LLM Auto 1.0 Updated",
            "is_active": 0
        }
        res = self.client.put(f"/api/owner/ai/models/{created_id}", json=update_payload, headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get("success"))

        # 4. Set as default
        res = self.client.post(f"/api/owner/ai/models/{created_id}/default", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get("success"))

        # 5. Delete model
        res = self.client.delete(f"/api/owner/ai/models/{created_id}", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get("success"))

    def test_04_ai_keys_management_and_testing(self):
        """Test AI Key retrieval, saving, and ping test"""
        # 1. Get keys
        res = self.client.get("/api/owner/ai/keys", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        keys = res.json().get("keys", [])
        self.assertTrue(len(keys) >= 5)
        for k in keys:
            self.assertIn("provider", k)
            self.assertIn("is_configured", k)
            self.assertIn("masked_key", k)

        # 2. Save a key
        payload = {"provider": "deepseek", "api_key": "sk-deepseek-test-key-1234567890"}
        res = self.client.post("/api/owner/ai/keys", json=payload, headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.json().get("success"))

        # Verify key is masked
        res = self.client.get("/api/owner/ai/keys", headers=self.owner_headers)
        keys = res.json().get("keys", [])
        deepseek_key = next((k for k in keys if k["provider"] == "deepseek"), None)
        self.assertIsNotNone(deepseek_key)
        self.assertTrue(deepseek_key["is_configured"])
        self.assertTrue("••••" in deepseek_key["masked_key"])

        # 3. Test Connection
        test_payload = {"provider": "deepseek"}
        res = self.client.post("/api/owner/ai/keys/test", json=test_payload, headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        self.assertIn("latency_ms", data)
        self.assertIn("model_status", data)

    def test_05_ai_skills_management(self):
        """Test AI Skills retrieval and toggling"""
        res = self.client.get("/api/owner/ai/skills", headers=self.owner_headers)
        self.assertEqual(res.status_code, 200)
        skills = res.json().get("skills", [])
        self.assertTrue(len(skills) >= 1)

        first_skill = skills[0]
        skill_key = first_skill["skill_key"]
        new_active = 0 if first_skill.get("is_active") else 1

        toggle_res = self.client.post("/api/owner/ai/skills", json={"skill_key": skill_key, "is_active": new_active}, headers=self.owner_headers)
        self.assertEqual(toggle_res.status_code, 200)
        self.assertTrue(toggle_res.json().get("success"))

if __name__ == "__main__":
    unittest.main()
