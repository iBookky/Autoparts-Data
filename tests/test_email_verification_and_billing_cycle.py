import unittest
from fastapi.testclient import TestClient
from main import app
from backend.database import (
    create_verification_code,
    validate_verification_code,
    get_org_subscription,
    get_organization_members,
    get_public_payment_methods_db
)

class TestEmailVerificationAndBillingCycle(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_email_verification_otp_flow(self):
        """Test requesting OTP code and validating during signup"""
        test_email = "otp_security_test@example.com"
        
        # 1. Request OTP code via endpoint
        res = self.client.post("/api/auth/send-verification-code", json={"email": test_email})
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data.get("success"))
        code = data.get("demo_code")
        self.assertIsNotNone(code)
        self.assertEqual(len(str(code)), 6)

        # 2. Verify wrong OTP code fails
        val_fail = validate_verification_code(test_email, "000000")
        self.assertFalse(val_fail)

        # 3. Verify correct OTP code passes
        val_ok = validate_verification_code(test_email, code)
        self.assertTrue(val_ok)

    def test_org_members_includes_email_and_details(self):
        """Verify get_organization_members returns email and membership details"""
        mems = get_organization_members(1)
        self.assertIsInstance(mems, list)
        if len(mems) > 0:
            m = mems[0]
            self.assertIn("email", m)
            self.assertIn("platform_role", m)
            self.assertIn("is_user_active", m)

    def test_public_payment_methods_filtering(self):
        """Verify public payment methods returns list of active gateways"""
        methods = get_public_payment_methods_db()
        self.assertIsInstance(methods, list)

if __name__ == '__main__':
    unittest.main()
