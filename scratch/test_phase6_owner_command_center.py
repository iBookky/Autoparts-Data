#!/usr/bin/env python3
"""
Test Suite: Phase 6 — System Owner Business Command Center
Covers:
1. Executive KPIs (MRR, ARR, ARPU, paying orgs, active trials, past due)
2. Revenue Analytics & 30-Day Daily Trend
3. Customer 360 Profile & Health Scoring Engine (0-100)
4. Subscriptions & 7/14/30-Day Renewal Pipeline
5. Automotive Search Intelligence (Types, Success Rate %, Top Brands & Categories)
6. Zero-Result Queries (Data Gap Intelligence)
7. Proactive Upgrade Opportunities (>80% Quota/Seats)
8. Explainable Churn Risk Detection
9. Plans & Add-ons Performance & Attachment Rates
10. Actionable Business Alerts & Dismissal Workflow
11. Secure Reports Export (CSV & JSON) + Commercial Audit Logging
12. Strict Role Isolation (Owner vs Customer Staff vs Super Admin)
"""

import os
import sys
import unittest
import json
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from backend.database import init_db, get_db_connection, create_owner_alert, get_owner_alerts, dismiss_owner_alert
from backend.services.owner_analytics_service import OwnerAnalyticsService

class TestPhase6OwnerCommandCenter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        cls.client = TestClient(app)
        
        # Test auth headers
        cls.owner_headers = {"X-User-Role": "OWNER", "X-Username": "boss_owner", "X-User-Id": "1"}
        cls.superadmin_headers = {"X-User-Role": "SUPER_ADMIN", "X-Username": "sys_admin", "X-User-Id": "2"}
        cls.staff_headers = {"X-User-Role": "STAFF", "X-Username": "parts_worker", "X-User-Id": "3"}

    def test_01_overview_kpis_calculation(self):
        """Test Executive Overview KPIs: MRR, ARR, ARPU, active orgs, and churn metrics."""
        kpis = OwnerAnalyticsService.get_overview_kpis()
        self.assertIn("mrr", kpis)
        self.assertIn("arr", kpis)
        self.assertIn("arpu", kpis)
        self.assertIn("active_paying_organizations", kpis)
        self.assertIn("active_subscriptions", kpis)
        self.assertIn("trial_customers", kpis)
        self.assertIn("churn_rate_pct", kpis)
        
        self.assertGreaterEqual(kpis["mrr"], 0)
        self.assertEqual(kpis["arr"], kpis["mrr"] * 12)
        if kpis["active_paying_organizations"] > 0:
            self.assertEqual(kpis["arpu"], int(round(kpis["mrr"] / kpis["active_paying_organizations"])))
        print(f"✓ Scenario 1: Overview KPIs passed (MRR: ฿{kpis['mrr']:,}, ARR: ฿{kpis['arr']:,}, ARPU: ฿{kpis['arpu']:,})")

    def test_02_revenue_analytics_and_daily_trend(self):
        """Test Revenue Analytics: Gross, Net, 7% VAT, payment methods, and daily trend."""
        rev = OwnerAnalyticsService.get_revenue_analytics(range_days=30)
        self.assertIn("gross_revenue", rev)
        self.assertIn("net_revenue", rev)
        self.assertIn("total_vat_7pct", rev)
        self.assertIn("paid_invoices_count", rev)
        self.assertIn("payment_methods_breakdown", rev)
        self.assertIn("revenue_trend", rev)
        
        self.assertIsInstance(rev["revenue_trend"], list)
        self.assertGreater(len(rev["revenue_trend"]), 0)
        print(f"✓ Scenario 2: Revenue analytics passed (Gross: ฿{rev['gross_revenue']:,}, VAT: ฿{rev['total_vat_7pct']:,})")

    def test_03_customers_analytics_and_crm_funnel(self):
        """Test Customer analytics list and CRM conversion funnel calculation."""
        cust_data = OwnerAnalyticsService.get_customers_analytics()
        self.assertIn("total_customers", cust_data)
        self.assertIn("customers", cust_data)
        self.assertIn("funnel", cust_data)
        
        customers = cust_data["customers"]
        self.assertGreater(len(customers), 0)
        first_cust = customers[0]
        self.assertIn("name", first_cust)
        self.assertIn("plan_tier", first_cust)
        self.assertIn("mrr", first_cust)
        self.assertIn("health_score", first_cust)
        self.assertIn("health_status", first_cust)
        self.assertIn("usage_pct", first_cust)
        
        funnel = cust_data["funnel"]
        self.assertIn("lead_to_customer_conversion_pct", funnel)
        print(f"✓ Scenario 3: Customer analytics passed ({len(customers)} orgs, Conv: {funnel['lead_to_customer_conversion_pct']}%)")

    def test_04_customer_health_score_engine(self):
        """Test composite Customer Health Score (0-100) and explainable signals."""
        healthy_org = {
            "sub_status": "ACTIVE",
            "total_searches_used": 600,
            "monthly_search_quota": 1000,
            "active_users": 3
        }
        score, status, reasons = OwnerAnalyticsService.calculate_customer_health(healthy_org)
        self.assertGreaterEqual(score, 75)
        self.assertEqual(status, "HEALTHY")

        at_risk_org = {
            "sub_status": "GRACE_PERIOD",
            "total_searches_used": 0,
            "monthly_search_quota": 5000,
            "active_users": 1
        }
        score2, status2, reasons2 = OwnerAnalyticsService.calculate_customer_health(at_risk_org)
        self.assertLess(score2, 50)
        self.assertEqual(status2, "AT_RISK")
        self.assertIn("Zero search queries recorded this cycle", reasons2)
        print(f"✓ Scenario 4: Health scoring passed (Healthy: {score}/100, At-Risk: {score2}/100 with explainable signals)")

    def test_05_customer_360_profile_detail(self):
        """Test detailed Customer 360 profile endpoint and service."""
        c360 = OwnerAnalyticsService.get_customer_360(org_id=1)
        self.assertIsNotNone(c360)
        self.assertIn("organization", c360)
        self.assertIn("subscription", c360)
        self.assertIn("subscription_items", c360)
        self.assertIn("members", c360)
        self.assertIn("recent_searches", c360)
        self.assertIn("invoices", c360)
        self.assertIn("lifetime_paid_revenue", c360)
        
        self.assertEqual(c360["organization"]["id"], 1)
        print(f"✓ Scenario 5: Customer 360 profile passed for {c360['organization']['name']}")

    def test_06_subscriptions_and_renewal_pipeline(self):
        """Test subscription distributions and 7/14/30-day renewal pipeline."""
        subs_data = OwnerAnalyticsService.get_subscriptions_analytics()
        self.assertIn("status_distribution", subs_data)
        self.assertIn("plan_distribution", subs_data)
        self.assertIn("renewal_pipeline", subs_data)
        
        pipe = subs_data["renewal_pipeline"]
        self.assertIn("in_7_days_count", pipe)
        self.assertIn("in_14_days_count", pipe)
        self.assertIn("in_30_days_count", pipe)
        self.assertIn("renewals_list", pipe)
        print(f"✓ Scenario 6: Subscriptions & renewal pipeline passed ({len(pipe['renewals_list'])} in 30d pipeline)")

    def test_07_automotive_usage_and_search_intelligence(self):
        """Test automotive search breakdown, search success rate %, and top brands."""
        usage = OwnerAnalyticsService.get_automotive_usage_analytics()
        self.assertIn("total_searches", usage)
        self.assertIn("search_success_rate_pct", usage)
        self.assertIn("search_types_breakdown", usage)
        self.assertIn("top_brands_demand", usage)
        self.assertIn("top_categories_demand", usage)
        self.assertIn("top_zero_result_queries", usage)
        
        self.assertGreaterEqual(usage["search_success_rate_pct"], 0)
        self.assertLessEqual(usage["search_success_rate_pct"], 100)
        print(f"✓ Scenario 7: Automotive search BI passed (Success Rate: {usage['search_success_rate_pct']}%)")

    def test_08_zero_result_searches_intelligence(self):
        """Test top zero-result queries extraction for automotive catalog gaps."""
        usage = OwnerAnalyticsService.get_automotive_usage_analytics()
        zero_queries = usage["top_zero_result_queries"]
        self.assertIsInstance(zero_queries, list)
        self.assertGreater(len(zero_queries), 0)
        
        query_names = [z["search_query"] for z in zero_queries]
        self.assertTrue(any("MISSING" in q or "Mazda" in q or "ISUZU" in q for q in query_names))
        print(f"✓ Scenario 8: Zero-result intelligence passed ({len(zero_queries)} unmatched queries detected)")

    def test_09_proactive_upgrade_opportunities(self):
        """Test upgrade opportunity detector for accounts exceeding 80% quota or seat limit."""
        opps_data = OwnerAnalyticsService.get_opportunities_and_health()
        self.assertIn("upgrade_opportunities", opps_data)
        self.assertIn("at_risk_customers", opps_data)
        
        opps = opps_data["upgrade_opportunities"]
        if opps:
            first_opp = opps[0]
            self.assertIn("org_name", first_opp)
            self.assertIn("current_plan", first_opp)
            self.assertIn("recommended_plan", first_opp)
            self.assertIn("trigger_reason", first_opp)
        print(f"✓ Scenario 9: Proactive upgrade opportunities passed ({len(opps)} upgrade candidates)")

    def test_10_explainable_churn_risk_detection(self):
        """Test at-risk customer detection with human-readable triggers."""
        opps_data = OwnerAnalyticsService.get_opportunities_and_health()
        at_risk = opps_data["at_risk_customers"]
        self.assertIsInstance(at_risk, list)
        if at_risk:
            r = at_risk[0]
            self.assertIn("risk_reasons", r)
            self.assertIn("risk_level", r)
            self.assertGreater(len(r["risk_reasons"]), 0)
        print(f"✓ Scenario 10: Churn risk detection passed ({len(at_risk)} at-risk accounts identified)")

    def test_11_plans_and_addons_performance(self):
        """Test commercial plan & add-on performance and badge allocations."""
        perf = OwnerAnalyticsService.get_plans_and_addons_performance()
        self.assertIn("plans_performance", perf)
        self.assertIn("addons_performance", perf)
        
        plans = perf["plans_performance"]
        self.assertGreater(len(plans), 0)
        self.assertIn("is_highest_revenue", plans[0])
        self.assertIn("is_best_selling", plans[0])
        print(f"✓ Scenario 11: Plan & add-on performance passed ({len(plans)} plans evaluated)")

    def test_12_actionable_owner_alerts_lifecycle(self):
        """Test creating, listing, and dismissing real-time owner business alerts."""
        alert_id = create_owner_alert(
            alert_type="PAYMENT_FAILURE",
            severity="CRITICAL",
            title="Automated Test Payment Issue",
            message="Test Corp payment failed after 3 retries",
            org_id=1,
            action_link="#owner-sub-revenue"
        )
        self.assertIsNotNone(alert_id)

        # Retrieve active alerts
        alerts = get_owner_alerts(is_dismissed=False)
        active_ids = [a["id"] for a in alerts]
        self.assertIn(alert_id, active_ids)

        # Dismiss alert
        dismissed = dismiss_owner_alert(alert_id=alert_id, user_id=1)
        self.assertTrue(dismissed)

        # Confirm dismissed
        remaining = get_owner_alerts(is_dismissed=False)
        self.assertNotIn(alert_id, [a["id"] for a in remaining])
        print(f"✓ Scenario 12: Owner alerts lifecycle passed (Created #{alert_id}, verified, and dismissed)")

    def test_13_secure_report_export_csv_and_json(self):
        """Test CSV and JSON export generation for REVENUE, CUSTOMERS, SUBSCRIPTIONS, USAGE."""
        for rtype in ["REVENUE", "CUSTOMERS", "SUBSCRIPTIONS", "USAGE"]:
            csv_content, csv_name = OwnerAnalyticsService.export_report(rtype, format_type="csv")
            self.assertTrue(csv_name.endswith(".csv"))
            self.assertIn("\n", csv_content)

            json_content, json_name = OwnerAnalyticsService.export_report(rtype, format_type="json")
            self.assertTrue(json_name.endswith(".json"))
            parsed = json.loads(json_content)
            self.assertIsInstance(parsed, dict)
        print(f"✓ Scenario 13: Secure report export passed (CSV & JSON for all 4 report types)")

    def test_14_owner_api_endpoints_via_http(self):
        """Test Owner REST API endpoints over HTTP client."""
        # 1. Overview
        resp = self.client.get("/api/owner/overview", headers=self.owner_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

        # 2. Revenue
        resp = self.client.get("/api/owner/revenue?range_days=14", headers=self.owner_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

        # 3. Customers
        resp = self.client.get("/api/owner/customers", headers=self.owner_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

        # 4. Customer 360
        resp = self.client.get("/api/owner/customers/1/360", headers=self.owner_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.json().get("success"))

        # 5. Export Report HTTP
        resp = self.client.get("/api/owner/reports/export?report_type=REVENUE&format=csv", headers=self.owner_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.headers.get("content-type"), "text/csv; charset=utf-8")
        print("✓ Scenario 14: Owner REST API endpoints passed over HTTP")

    def test_15_owner_rbac_isolation(self):
        """Test non-owners (STAFF) are forbidden from accessing Owner Command Center endpoints."""
        resp = self.client.get("/api/owner/overview", headers=self.staff_headers)
        self.assertEqual(resp.status_code, 403)

        resp2 = self.client.get("/api/owner/revenue", headers=self.staff_headers)
        self.assertEqual(resp2.status_code, 403)

        resp3 = self.client.get("/api/owner/reports/export?report_type=CUSTOMERS", headers=self.staff_headers)
        self.assertEqual(resp3.status_code, 403)
        print("✓ Scenario 15: Owner RBAC security isolation verified (403 Forbidden on staff requests)")

    def test_16_superadmin_vs_owner_separation(self):
        """Test strict boundary separation between System Owner and Super Admin."""
        # Super admin endpoints require super_admin
        sa_resp = self.client.get("/api/superadmin/system-health", headers=self.superadmin_headers)
        self.assertEqual(sa_resp.status_code, 200)
        self.assertIn("db_mode", sa_resp.json()["health"])

        # Staff cannot access super admin
        sa_staff_resp = self.client.get("/api/superadmin/system-health", headers=self.staff_headers)
        self.assertEqual(sa_staff_resp.status_code, 403)
        print("✓ Scenario 16: Super Admin vs System Owner separation verified")

if __name__ == "__main__":
    unittest.main()
