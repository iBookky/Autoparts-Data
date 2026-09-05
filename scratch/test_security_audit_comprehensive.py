"""
================================================================================
Comprehensive Security Audit & Penetration-Resistance Test Suite
AutoParts OEM vs Aftermarket SaaS Platform
================================================================================
Tests cover:
1. RBAC & Privilege Escalation Defenses (Owner, SuperAdmin, Admin, Staff, Customer, Anonymous)
2. Multi-Tenant Data Isolation & Horizontal Privilege Access Prevention
3. SQL Injection Defense Verification across all Search & Query Endpoints
4. Password Hashing & Secret Masking Verification
5. Sensitive AI Key Non-Leakage Auditing
6. Permanent Customer Deny-List Enforcement
7. Rate Limiting & Quota Boundary Validation
"""

import os
import sys
import unittest
import sqlite3
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import app
from backend.database import get_db_connection

class TestSecurityAuditComprehensive(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.conn = get_db_connection()

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    # ================= 1. RBAC & PRIVILEGE ESCALATION DEFENSE =================
    def test_owner_endpoints_reject_unprivileged_roles(self):
        """Verify /api/owner/* endpoints strictly reject non-owner and unauthenticated requests."""
        owner_endpoints = [
            ("GET", "/api/owner/overview"),
            ("GET", "/api/owner/revenue"),
            ("GET", "/api/owner/customers"),
            ("GET", "/api/owner/ai/overview"),
            ("GET", "/api/owner/ai/models"),
            ("GET", "/api/owner/ai/keys"),
            ("GET", "/api/owner/ai/skills"),
            ("GET", "/api/owner/roles"),
            ("GET", "/api/owner/plans"),
            ("POST", "/api/owner/ai/keys")
        ]

        unauthorized_headers = [
            ("ANONYMOUS", {}),
            ("CUSTOMER_MEMBER", {"x-username": "somchai_cust", "x-user-role": "CUSTOMER_MEMBER"}),
            ("CUSTOMER_OWNER", {"x-username": "somchai_cust", "x-user-role": "CUSTOMER_OWNER"}),
            ("STAFF", {"x-username": "staff_user", "x-user-role": "STAFF"}),
            ("ADMIN", {"x-username": "admin_user", "x-user-role": "ADMIN"})
        ]

        for method, endpoint in owner_endpoints:
            for role_name, headers in unauthorized_headers:
                if method == "GET":
                    res = self.client.get(endpoint, headers=headers)
                else:
                    res = self.client.post(endpoint, json={"provider": "openai", "api_key": "test"}, headers=headers)
                
                self.assertIn(
                    res.status_code, 
                    [401, 403], 
                    f"VULNERABILITY: Role {role_name} accessed {method} {endpoint} with status {res.status_code}"
                )

    def test_superadmin_endpoints_reject_unprivileged_roles(self):
        """Verify /api/superadmin/* endpoints strictly reject customer and staff access."""
        superadmin_endpoints = [
            ("/api/superadmin/permission-audit", "GET")
        ]
        
        unauthorized_headers = [
            ("ANONYMOUS", {}),
            ("CUSTOMER_MEMBER", {"x-username": "somchai_cust", "x-user-role": "CUSTOMER_MEMBER"}),
            ("CUSTOMER_OWNER", {"x-username": "somchai_cust", "x-user-role": "CUSTOMER_OWNER"}),
            ("STAFF", {"x-username": "staff_user", "x-user-role": "STAFF"})
        ]

        for endpoint, method in superadmin_endpoints:
            for role_name, headers in unauthorized_headers:
                res = self.client.get(endpoint, headers=headers)
                self.assertIn(
                    res.status_code,
                    [401, 403],
                    f"VULNERABILITY: Non-superadmin ({role_name}) accessed {endpoint} with status {res.status_code}"
                )

    # ================= 2. MULTI-TENANT ISOLATION & HORIZONTAL ACCESS =================
    def test_customer_tenant_data_isolation(self):
        """Verify Customer cannot access other organizations' sensitive data."""
        # Tenant 1 user attempting to access tenant endpoints
        headers_tenant1 = {"x-username": "somchai_cust", "x-user-role": "CUSTOMER_OWNER", "x-org-id": "1"}
        
        # Invoices endpoint must be scoped to the authenticated user's organization
        res = self.client.get("/api/saas/invoices", headers=headers_tenant1)
        self.assertEqual(res.status_code, 200)
        invoices = res.json().get("invoices", [])
        for inv in invoices:
            if "organization_id" in inv:
                self.assertEqual(
                    inv["organization_id"], 
                    1, 
                    f"VULNERABILITY: Tenant 1 received invoice for Tenant {inv['organization_id']}"
                )

    # ================= 3. SQL INJECTION DEFENSE =================
    def test_sql_injection_resilience_in_search_and_query(self):
        """Fuzz search endpoints with classic and advanced SQL injection payloads."""
        sqli_payloads = [
            "' OR '1'='1",
            "1; DROP TABLE temp_parts; --",
            "' UNION SELECT username, password, role, 4, 5, 6, 7, 8, 9 FROM users --",
            "\" OR \"\"=\"",
            "admin'--",
            "1' AND SLEEP(2) --",
            "1' AND 1=(SELECT COUNT(*) FROM users); --"
        ]

        for payload in sqli_payloads:
            # 1. Search by OEM Code
            res = self.client.get("/api/parts/search", params={"oem_code": payload})
            self.assertEqual(res.status_code, 200, f"Search crashed on payload: {payload}")
            data = res.json()
            self.assertTrue(data.get("success", False))

            # 2. Search by SKU
            res = self.client.get("/api/parts/search", params={"sku": payload})
            self.assertEqual(res.status_code, 200, f"SKU Search crashed on payload: {payload}")

            # 3. Cross-reference matrix lookup
            res = self.client.get("/api/parts/cross-reference-matrix", params={"part_number": payload})
            self.assertEqual(res.status_code, 200, f"Matrix lookup crashed on payload: {payload}")

        # Verify critical table integrity was not compromised
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='temp_parts'")
        self.assertIsNotNone(cursor.fetchone(), "CRITICAL: temp_parts table was dropped or damaged by SQLi fuzzing!")

    # ================= 4. PASSWORD & CREDENTIAL STORAGE SECURITY =================
    def test_passwords_are_cryptographically_hashed(self):
        """Verify no plaintext passwords exist in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, username, password FROM users")
        users = cursor.fetchall()
        
        self.assertGreater(len(users), 0, "No users found in database to audit!")
        for u in users:
            uid, uname, p_hash = u["id"], u["username"], u["password"]
            # SHA-256 hash length is 64 hex characters
            self.assertIsNotNone(p_hash, f"User {uname} has null password")
            self.assertNotEqual(p_hash, "password", f"User {uname} has plaintext password")
            self.assertNotEqual(p_hash, "1234", f"User {uname} has plaintext password")
            self.assertNotEqual(p_hash, "admin", f"User {uname} has plaintext password")
            self.assertTrue(
                len(p_hash) >= 32, 
                f"User {uname} password is too short ({len(p_hash)} chars), not a cryptographic hash!"
            )

    # ================= 5. SENSITIVE AI KEY NON-LEAKAGE AUDITING =================
    def test_ai_keys_not_leaked_in_public_or_customer_endpoints(self):
        """Verify AI provider credentials and keys are never exposed in public or customer APIs."""
        public_endpoints = [
            "/health",
            "/api/health",
            "/api/public/coverage-stats",
            "/api/public/demo-search?query=04465",
            "/api/metadata/car-brands",
            "/api/metadata/aftermarket-brands"
        ]
        
        for ep in public_endpoints:
            res = self.client.get(ep)
            self.assertEqual(res.status_code, 200)
            text = res.text.lower()
            self.assertNotIn("sk-proj-", text, f"Potential OpenAI key leakage in {ep}")
            self.assertNotIn("sk-ant-", text, f"Potential Anthropic key leakage in {ep}")
            self.assertNotIn("aizasy", text, f"Potential Gemini key leakage in {ep}")

    # ================= 6. PERMANENT CUSTOMER DENY LIST =================
    def test_permanent_customer_deny_list(self):
        """Verify customers cannot trigger bulk scrapers, full exports, or internal database actions."""
        customer_headers = {"x-username": "somchai_cust", "x-user-role": "CUSTOMER_OWNER"}
        
        # 1. Export automotive catalog
        res = self.client.post("/api/saas/export", json={"filter_brand": ""}, headers=customer_headers)
        self.assertEqual(res.status_code, 403, "Customer bypassed export block!")

        # 2. Trigger web scraper
        res = self.client.post("/api/admin/scrape-url", json={"url": "https://example.com"}, headers=customer_headers)
        self.assertIn(res.status_code, [401, 403], "Customer bypassed scraper execution block!")

    # ================= 7. INPUT VALIDATION & BUFFER SAFETY =================
    def test_oversized_payload_and_special_character_resilience(self):
        """Verify API handles extremely large inputs and unusual unicode gracefully without crashing."""
        oversized_str = "A" * 5000
        res = self.client.get("/api/parts/search", params={"oem_code": oversized_str})
        self.assertIn(res.status_code, [200, 400, 422], f"Server crashed on oversized query with code {res.status_code}")

        unicode_payload = "🚗 อะไหล่ แท้ 🛠️ <script>alert('xss')</script> &quot;test&quot;"
        res = self.client.get("/api/parts/search", params={"sku": unicode_payload})
        self.assertIn(res.status_code, [200, 400, 422], f"Server crashed on unicode payload with code {res.status_code}")

if __name__ == "__main__":
    unittest.main()
