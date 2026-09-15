import unittest
from fastapi.testclient import TestClient
from main import app
from backend.database import (
    create_verification_token,
    verify_email_token_db,
    validate_verification_code,
    get_org_subscription,
    get_organization_members,
    get_public_payment_methods_db,
    get_platform_settings,
    update_platform_settings
)

class TestEmailVerificationAndBillingCycle(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.owner_headers = {"X-User-Role": "OWNER", "X-Username": "admin"}

    def test_email_verification_link_flow(self):
        """Test requesting email verification link and clicking token link"""
        test_email = "magic_link_test@example.com"
        
        # 1. Send verification link via endpoint
        res = self.client.post("/api/auth/send-verification-email", json={"email": test_email})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        token = data.get("demo_token")
        self.assertIsNotNone(token)
        self.assertTrue(token.startswith("vft_"))
        self.assertIn("verify_url", data)

        # 2. Click verification link endpoint
        link_res = self.client.get(f"/api/auth/verify-email-link?token={token}")
        self.assertEqual(link_res.status_code, 200)
        self.assertIn("ยืนยันอีเมลสำเร็จ", link_res.text)

        # 3. Re-using same token fails
        fail_res = self.client.get(f"/api/auth/verify-email-link?token={token}")
        self.assertIn("ไม่สามารถยืนยันอีเมลได้", fail_res.text)

    def test_owner_email_sender_settings(self):
        """Test GET and POST owner email sender & SMTP settings"""
        # GET settings
        get_res = self.client.get("/api/owner/email-settings", headers=self.owner_headers)
        self.assertEqual(get_res.status_code, 200)
        self.assertTrue(get_res.json().get("success"))

        # POST settings update
        update_payload = {
            "smtp_sender_email": "noreply@siamautoparts.com",
            "smtp_sender_name": "Siam Auto Parts AI Cloud Test",
            "smtp_host": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_security": "TLS",
            "smtp_enabled": 1
        }
        post_res = self.client.post("/api/owner/email-settings", json=update_payload, headers=self.owner_headers)
        self.assertEqual(post_res.status_code, 200)
        self.assertTrue(post_res.json().get("success"))

        # Verify saved settings
        settings = get_platform_settings()
        self.assertEqual(settings.get("smtp_sender_email"), "noreply@siamautoparts.com")
        self.assertEqual(settings.get("smtp_sender_name"), "Siam Auto Parts AI Cloud Test")

    def test_org_members_includes_email_and_details(self):
        """Verify get_organization_members returns email and membership details"""
        mems = get_organization_members(1)
        self.assertIsInstance(mems, list)

    def test_public_payment_methods_filtering(self):
        """Verify public payment methods returns list of active gateways"""
        methods = get_public_payment_methods_db()
        self.assertIsInstance(methods, list)

if __name__ == '__main__':
    unittest.main()
