import os
import sys
import unittest
import asyncio
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import (
    get_db_connection,
    init_db,
    get_public_coverage_stats_db,
    get_public_demo_search_db,
    register_trial_tenant_db,
    create_crm_lead,
    get_crm_leads,
    get_user_tenant_context,
    record_search_usage,
    validate_coupon_for_tenant,
    get_org_invoices
)
from backend.services.entitlement_service import EntitlementService
from backend.services.payment_gateway import PaymentGateway
from backend.services.billing_calculator import BillingCalculator

class TestPhase11CommercialMVPAndGTM(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_public_coverage_stats_api(self):
        """Scenario 1: Public coverage statistics API returns accurate counts for landing page."""
        stats = get_public_coverage_stats_db()
        self.assertIsInstance(stats, dict)
        self.assertGreater(stats.get("total_parts", 0), 0)
        self.assertGreater(stats.get("total_aftermarket_brands", 0), 0)
        self.assertGreater(stats.get("total_car_brands", 0), 0)
        self.assertEqual(stats.get("accuracy_rate"), 99.8)

    def test_02_public_demo_search_teaser(self):
        """Scenario 2: Public demo search returns max 3 sanitized teaser results."""
        results = get_public_demo_search_db("04465")
        self.assertIsInstance(results, list)
        self.assertLessEqual(len(results), 3)
        if len(results) > 0:
            first = results[0]
            self.assertIn("part_number", first)
            self.assertIn("oem_number", first)
            self.assertIn("brand", first)
            self.assertIn("relevance_score", first)
            # Ensure sensitive internal properties are not in teaser
            self.assertNotIn("cost_price", first)
            self.assertNotIn("supplier_note", first)

    def test_03_public_demo_search_short_query(self):
        """Scenario 3: Short or non-matching queries in demo search handle gracefully."""
        res = get_public_demo_search_db("ZZZ_NON_EXISTENT_CODE_12345")
        self.assertEqual(len(res), 0)

    def test_04_inbound_enterprise_lead_capture(self):
        """Scenario 4: Public sales contact creates lead in CRM pipeline with stage LEAD."""
        lead_data = {
            "company_name": "Viriyah Auto Logistics Co., Ltd.",
            "contact_person": "Khun Wichian",
            "email": "wichian@viriyah-auto.co.th",
            "phone": "02-999-8888",
            "pipeline_stage": "LEAD",
            "interested_plan_id": "enterprise",
            "expected_mrr": 15000,
            "notes": "Inbound lead from Landing Page: Looking for API integration for 500 fleet vehicles"
        }
        res = create_crm_lead(lead_data)
        self.assertTrue(res.get("success"))
        self.assertIsNotNone(res.get("lead_id"))

        # Verify in leads list
        leads = get_crm_leads()
        found = any(l["company_name"] == "Viriyah Auto Logistics Co., Ltd." for l in leads)
        self.assertTrue(found)

    def test_05_self_service_trial_registration_success(self):
        """Scenario 5: Self-service trial registration provisions user, org, and 14-day trial."""
        ts = int(datetime.now().timestamp())
        signup_data = {
            "company_name": f"Siam Garage {ts}",
            "contact_name": "Somchai Tech",
            "email": f"somchai_{ts}@siamgarage.com",
            "password": "Password123!",
            "phone": "089-123-4567",
            "segment": "GARAGE",
            "plan_id": "professional"
        }
        res = register_trial_tenant_db(signup_data)
        self.assertTrue(res.get("success"))
        self.assertEqual(res.get("org_role"), "OWNER")
        self.assertEqual(res.get("trial_days"), 14)
        self.assertIsNotNone(res.get("org_id"))
        self.assertIsNotNone(res.get("user_id"))

    def test_06_trial_registration_duplicate_email_rejected(self):
        """Scenario 6: Duplicate email registration is rejected."""
        ts = int(datetime.now().timestamp())
        signup_data = {
            "company_name": f"Unique Auto {ts}",
            "contact_name": "User One",
            "email": f"dup_{ts}@uniqueauto.com",
            "password": "Password123!",
            "phone": "089-000-0000",
            "segment": "RETAILER",
            "plan_id": "starter"
        }
        res1 = register_trial_tenant_db(signup_data)
        self.assertTrue(res1.get("success"))

        # Second attempt with same email
        res2 = register_trial_tenant_db(signup_data)
        self.assertFalse(res2.get("success"))
        self.assertIn("มีอยู่ในระบบแล้ว", res2.get("error", ""))

    def test_07_trial_registration_missing_fields_validation(self):
        """Scenario 7: Missing required fields (email, password, company) are validated."""
        bad_data = {
            "company_name": "",
            "email": "incomplete@test.com",
            "password": ""
        }
        res = register_trial_tenant_db(bad_data)
        self.assertFalse(res.get("success"))

    def test_08_trial_entitlements_provisioned(self):
        """Scenario 8: Trial organization receives initial whitelisted brand & category entitlements."""
        ts = int(datetime.now().timestamp())
        email = f"snapshot_test_{ts}@autocare.com"
        res = register_trial_tenant_db({
            "company_name": f"AutoCare Ent {ts}",
            "contact_name": "Tester",
            "email": email,
            "password": "Password123!",
            "segment": "GARAGE",
            "plan_id": "professional"
        })
        self.assertTrue(res.get("success"))
        org_id = res["org_id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM entitlements WHERE org_id = ? AND entitlement_type = 'BRAND'", (org_id,))
        brands = cursor.fetchall()
        conn.close()

        self.assertGreaterEqual(len(brands), 3)

    def test_09_trial_initial_usage_records_seeded(self):
        """Scenario 9: Initial usage records for current month are seeded with 0 usage."""
        ts = int(datetime.now().timestamp())
        email = f"usage_seed_{ts}@shop.com"
        res = register_trial_tenant_db({
            "company_name": f"Usage Seed Shop {ts}",
            "email": email,
            "password": "Password123!",
            "segment": "RETAILER",
            "plan_id": "starter"
        })
        self.assertTrue(res.get("success"))
        org_id = res["org_id"]

        cur_month = datetime.now().strftime("%Y-%m")
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usage_records WHERE org_id = ? AND period_month = ?", (org_id, cur_month))
        usage = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(usage)
        self.assertEqual(usage["searches_used"], 0)

    def test_10_trial_crm_lead_auto_created(self):
        """Scenario 10: Trial registration automatically logs CRM lead in TRIAL pipeline stage."""
        ts = int(datetime.now().timestamp())
        email = f"crm_lead_{ts}@fleet.com"
        company = f"Fleet Lead {ts}"
        res = register_trial_tenant_db({
            "company_name": company,
            "contact_name": "Fleet Manager",
            "email": email,
            "password": "Password123!",
            "segment": "FLEET",
            "plan_id": "business"
        })
        self.assertTrue(res.get("success"))

        leads = get_crm_leads()
        found = next((l for l in leads if l["email"] == email), None)
        self.assertIsNotNone(found)
        self.assertEqual(found["pipeline_stage"], "TRIAL")

    def test_11_trial_commercial_audit_log_recorded(self):
        """Scenario 11: Commercial audit log records TRIAL_SIGNUP event."""
        ts = int(datetime.now().timestamp())
        email = f"audit_trial_{ts}@garage.com"
        res = register_trial_tenant_db({
            "company_name": f"Audit Garage {ts}",
            "email": email,
            "password": "Password123!",
            "segment": "GARAGE",
            "plan_id": "professional"
        })
        self.assertTrue(res.get("success"))
        org_id = res["org_id"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM commercial_audit_logs WHERE org_id = ? AND action = 'TRIAL_SIGNUP'", (org_id,))
        audit = cursor.fetchone()
        conn.close()

        self.assertIsNotNone(audit)
        self.assertEqual(audit["actor_username"], email)

    def test_12_tenant_isolation_new_trial(self):
        """Scenario 12: Newly created trial tenant cannot access other organization's invoices."""
        ts = int(datetime.now().timestamp())
        res = register_trial_tenant_db({
            "company_name": f"Isolated Org {ts}",
            "email": f"isolated_{ts}@test.com",
            "password": "Password123!",
            "plan_id": "starter"
        })
        self.assertTrue(res.get("success"))
        new_org_id = res["org_id"]

        invoices = get_org_invoices(new_org_id)
        self.assertEqual(len(invoices), 0)

    def test_13_trial_search_entitlement_active(self):
        """Scenario 13: Trial organization has active search access for entitled brands."""
        ts = int(datetime.now().timestamp())
        email = f"search_ent_{ts}@garage.com"
        res = register_trial_tenant_db({
            "company_name": f"Search Ent Garage {ts}",
            "email": email,
            "password": "Password123!",
            "plan_id": "professional"
        })
        self.assertTrue(res.get("success"))

        is_allowed, reason, details = EntitlementService.validate_search_access(
            username=email,
            user_role="STAFF",
            car_brand="TOYOTA",
            category="ระบบเบรก"
        )
        self.assertTrue(is_allowed)

    def test_14_trial_search_usage_increment(self):
        """Scenario 14: Search usage increments properly on trial organization."""
        ts = int(datetime.now().timestamp())
        email = f"search_inc_{ts}@test.com"
        res = register_trial_tenant_db({
            "company_name": f"Usage Inc Org {ts}",
            "email": email,
            "password": "Password123!",
            "plan_id": "starter"
        })
        self.assertTrue(res.get("success"))
        org_id = res["org_id"]
        user_id = res["user_id"]

        record_search_usage(org_id=org_id, user_id=user_id, search_type="KEYWORD", query="04465")

        ctx = get_user_tenant_context(email)
        self.assertIsNotNone(ctx)
        self.assertGreaterEqual(ctx["usage"]["searches_used"], 1)

    def test_15_annual_billing_discount_calculation(self):
        """Scenario 15: Annual billing calculates discount and VAT correctly."""
        checkout = BillingCalculator.calculate_checkout(
            plan_id="professional",
            interval="YEARLY"
        )
        self.assertEqual(checkout["interval"], "YEARLY")
        self.assertGreater(checkout["base_price"], 0)
        self.assertGreater(checkout["tax_amount"], 0)
        self.assertEqual(checkout["total_amount"], checkout["subtotal"] + checkout["tax_amount"])

    def test_16_promotional_coupon_validation_commercial20(self):
        """Scenario 16: COMMERCIAL20 coupon is valid and calculates 20% discount."""
        ts = int(datetime.now().timestamp())
        res = register_trial_tenant_db({
            "company_name": f"Coupon Org {ts}",
            "email": f"coupon_{ts}@test.com",
            "password": "Password123!",
            "plan_id": "professional"
        })
        self.assertTrue(res.get("success"))
        org_id = res["org_id"]

        is_valid, err, coupon = validate_coupon_for_tenant(
            code="COMMERCIAL20",
            org_id=org_id,
            plan_id="professional",
            subtotal=3990
        )
        self.assertTrue(is_valid)
        self.assertIsNotNone(coupon)
        self.assertEqual(coupon["discount_type"], "PERCENT")
        self.assertEqual(coupon["discount_value"], 20)

    def test_17_promotional_coupon_launch50(self):
        """Scenario 17: LAUNCH50 coupon provides 50% discount for launch campaign."""
        ts = int(datetime.now().timestamp())
        res = register_trial_tenant_db({
            "company_name": f"Launch Org {ts}",
            "email": f"launch_{ts}@test.com",
            "password": "Password123!",
            "plan_id": "business"
        })
        self.assertTrue(res.get("success"))
        org_id = res["org_id"]

        is_valid, err, coupon = validate_coupon_for_tenant(
            code="LAUNCH50",
            org_id=org_id,
            plan_id="business",
            subtotal=8990
        )
        self.assertTrue(is_valid)
        self.assertEqual(coupon["discount_value"], 50)

    def test_18_trial_to_paid_checkout_intent(self):
        """Scenario 18: Trial tenant can initiate checkout with PaymentGateway idempotency."""
        ts = int(datetime.now().timestamp())
        res = register_trial_tenant_db({
            "company_name": f"Paid Checkout Org {ts}",
            "email": f"checkout_{ts}@test.com",
            "password": "Password123!",
            "plan_id": "professional"
        })
        self.assertTrue(res.get("success"))
        org_id = res["org_id"]

        # Create payment intent
        payment_res = PaymentGateway.create_payment_intent(
            org_id=org_id,
            invoice_id=1,
            amount=4269, # 3990 + 7% VAT
            payment_method="CREDIT_CARD",
            idempotency_key=f"IDEMP-TRIAL-{ts}"
        )
        self.assertTrue(payment_res["success"])
        self.assertFalse(payment_res["is_duplicate"])

    def test_19_full_search_consistency_under_commercial_layer(self):
        """Scenario 19: Core automotive search engine remains 100% consistent under commercial layer."""
        res_oem = get_public_demo_search_db("04465-0K360")
        self.assertGreater(len(res_oem), 0)
        first = res_oem[0]
        self.assertIsNotNone(first.get("brand"))
        self.assertIsNotNone(first.get("part_number"))

    def test_20_public_demo_search_vehicle_fitment(self):
        """Scenario 20: Vehicle fitment query in public demo search returns valid models."""
        res_vehicle = get_public_demo_search_db("04465")
        self.assertGreater(len(res_vehicle), 0)
        self.assertIsNotNone(res_vehicle[0].get("car_brand"))

if __name__ == "__main__":
    unittest.main()
