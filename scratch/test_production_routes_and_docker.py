import os
import sys
import unittest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app

class TestProductionRoutesAndDocker(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_spa_web_routes(self):
        routes = [
            "/",
            "/search",
            "/pricing",
            "/portal",
            "/settings",
            "/coverage",
            "/crossref",
            "/favorites",
            "/history",
            "/invoices",
            "/usage",
            "/api-hub",
            "/developer",
            "/owner",
            "/admin",
            "/superadmin",
            "/staff",
            "/app"
        ]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed with status {res.status_code}")
            self.assertIn("<html", res.text.lower(), f"Route {route} did not return HTML content")

    def test_healthcheck_endpoints(self):
        for route in ["/health", "/api/health"]:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["database"], "connected")
            self.assertEqual(data["service"], "autoparts-crossref-saas")

    def test_docker_files_exist(self):
        required_files = [
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.prod.yml",
            "Caddyfile",
            ".env.production.example",
            "requirements.txt",
            "docs/PRODUCTION_DOCKER_DEPLOYMENT_GUIDE.md"
        ]
        for file in required_files:
            self.assertTrue(os.path.exists(file), f"File {file} is missing!")
            self.assertGreater(os.path.getsize(file), 50, f"File {file} is unexpectedly empty!")

if __name__ == "__main__":
    unittest.main()
