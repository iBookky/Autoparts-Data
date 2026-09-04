# Phase 12.1 — Authoritative Test Inventory

**Date**: 2026-09-03  
**Platform Version**: v12.0.0-rc1  
**Total Executed Test Suites**: 3  
**Total Executed Test Scenarios**: 65  
**Total Passed**: 65 (100% OK)  
**Total Failed**: 0  

---

## 1. Suite 1: Phase 12 Stabilization, Protection & Recovery (`scratch/test_phase12_stabilization_and_protection.py`)

| Test ID | Method Name | Objective & Assertions | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **P12-01** | `test_01_customer_staff_export_denied` | Customer role `STAFF` calling `POST /api/saas/export` | HTTP 403 (`"Automotive data export is not available for this account."`) | HTTP 403 Forbidden | **PASS ✅** |
| **P12-02** | `test_02_customer_owner_export_denied` | Customer role `CUSTOMER_OWNER` calling `POST /api/saas/export` | HTTP 403 | HTTP 403 Forbidden | **PASS ✅** |
| **P12-03** | `test_03_customer_member_export_denied` | Customer role `CUSTOMER_MEMBER` calling `POST /api/saas/export` | HTTP 403 | HTTP 403 Forbidden | **PASS ✅** |
| **P12-04** | `test_04_operator_admin_export_allowed` | Operator role `ADMIN` calling `POST /api/saas/export` | HTTP 200 CSV Stream | HTTP 200 CSV Stream | **PASS ✅** |
| **P12-05** | `test_05_operator_superadmin_export_allowed` | Operator role `SUPER_ADMIN` calling `POST /api/saas/export` | HTTP 200 CSV Stream | HTTP 200 CSV Stream | **PASS ✅** |
| **P12-06** | `test_06_export_import_template_customer_denied` | Customer accessing `/api/parts/export-import-template` | HTTP 401 / 403 | HTTP 401 / 403 | **PASS ✅** |
| **P12-07** | `test_07_search_hard_limit_enforced_and_clamped` | Requesting `limit=100000` on `/api/parts/search` | Results clamped $\le 50$ | Results capped at 50 | **PASS ✅** |
| **P12-08** | `test_08_search_pagination_offset_calculation` | Sequential offset querying (`page=1`, `page=2`) | Non-overlapping distinct records | Correct pagination offsets | **PASS ✅** |
| **P12-09** | `test_09_search_response_data_minimization` | Querying OEM part for customer view | No internal IDs, cost figures, or scraper logs | Sanitized DTO fields only | **PASS ✅** |
| **P12-10** | `test_10_empty_search_returns_empty_list` | Invoking search without query parameters | Clean empty list `[]`, no database dump | Returns `[]` safely | **PASS ✅** |
| **P12-11** | `test_11_broad_query_filtering` | Searching with broad brand filter `HONDA` | All returned items match Honda | Filter strictly enforced | **PASS ✅** |
| **P12-12** | `test_12_cross_reference_matrix_oem_lookup` | Querying cross-reference matrix by OEM | Canonical schema with verified equivalents | TRW/BOSCH/AISIN matches | **PASS ✅** |
| **P12-13** | `test_13_cross_reference_matrix_bidirectional_match` | Querying cross-reference matrix by SKU `GDB3534UT` | Target OEM `04465-0K360` returned | Bidirectional link valid | **PASS ✅** |
| **P12-14** | `test_14_cross_reference_empty_query_safe` | Querying non-existent part code | Returns empty list `[]` without 500 error | Returns `[]` safely | **PASS ✅** |
| **P12-15** | `test_15_product_detail_includes_cross_references` | Product Drawer lookup for part with relations | `cross_references` array populated | Populated with 4 items | **PASS ✅** |
| **P12-16** | `test_16_product_detail_with_no_cross_references_returns_empty_array` | Product Drawer lookup for part without relations | HTTP 200 + `cross_references: []`, not 500 | Valid business state | **PASS ✅** |
| **P12-17** | `test_17_product_detail_invalid_id_returns_404` | Product Drawer lookup for non-existent ID | HTTP 404 `"Product not found."` | HTTP 404 | **PASS ✅** |
| **P12-18** | `test_18_cross_reference_endpoint_contract` | `GET /api/parts/cross-reference-matrix` | `{"success": true, "matrix": [...]}` | Standard API schema | **PASS ✅** |
| **P12-19** | `test_19_cross_reference_normalization` | Querying with whitespace and lowercase variants | Normalized matching identical results count | Exact normalized match | **PASS ✅** |
| **P12-20** | `test_20_ai_search_output_capped` | Invoking `/api/parts/ai-search` | Recommendations capped $\le 5$ items | Max 5 items returned | **PASS ✅** |
| **P12-21** | `test_21_multi_tenant_invoice_isolation` | Tenant A attempting to access Tenant B's invoices | Zero leakage across tenant boundary | Fully isolated | **PASS ✅** |
| **P12-22** | `test_22_expired_subscription_blocks_search` | Canceled/expired subscription executing search | Search blocked with locked status card | Access denied | **PASS ✅** |
| **P12-23** | `test_23_brand_whitelist_enforcement` | Searching brand outside licensed entitlements | Entitlement engine denies unauthorized brand | Rejected accurately | **PASS ✅** |
| **P12-24** | `test_24_category_whitelist_enforcement` | Searching category outside licensed entitlements | Entitlement engine denies category | Rejected accurately | **PASS ✅** |
| **P12-25** | `test_25_oem_search_regression` | Exact OEM code search `04465-0K360` | Exact OEM match score 100 | Match score 100 | **PASS ✅** |
| **P12-26** | `test_26_sku_search_regression` | SKU search `GDB3534` | Exact SKU match score 95 | Match score 95 | **PASS ✅** |
| **P12-27** | `test_27_vin_search_regression` | 17-digit VIN lookup `MR0HA3CD...` | Decodes vehicle specs and chassis | Specs decoded | **PASS ✅** |
| **P12-28** | `test_28_vehicle_fitment_search_regression` | Vehicle search `Toyota Hilux Revo` | Fitment match score 70 | Fitment items returned | **PASS ✅** |
| **P12-29** | `test_29_public_demo_search_regression` | Unauthenticated public demo search | Max 3 teaser items, zero leaks | 3 teaser items | **PASS ✅** |

---

## 2. Suite 2: Phase 11 Commercial MVP & GTM (`scratch/test_phase11_commercial_mvp_and_gtm.py`)

| Test ID | Method Name | Objective & Assertions | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **P11-01** | `test_01_public_coverage_stats_api` | Public data statistics counter | Aggregate counts returned | Accurate counts | **PASS ✅** |
| **P11-02** | `test_02_public_demo_search_teaser` | Live demo teaser search | Max 3 results returned | Teaser limited to 3 | **PASS ✅** |
| **P11-03** | `test_03_public_demo_search_short_query` | Demo search with short/blank string | Graceful empty list `[]` | Empty list `[]` | **PASS ✅** |
| **P11-04** | `test_04_inbound_enterprise_lead_capture` | Sales inquiry lead submission | CRM lead created in `LEAD` stage | Lead created | **PASS ✅** |
| **P11-05** | `test_05_self_service_trial_registration_success` | 14-day trial self-registration | Provisions user, org, and 14d trial | Tenant provisioned | **PASS ✅** |
| **P11-06** | `test_06_trial_registration_duplicate_email_rejected` | Registering existing email | HTTP 400 rejection | HTTP 400 | **PASS ✅** |
| **P11-07** | `test_07_trial_registration_missing_fields_validation` | Submitting missing required fields | HTTP 422 / 400 validation error | Validation rejected | **PASS ✅** |
| **P11-08** | `test_08_trial_entitlements_provisioned` | Entitlements for new trial tenant | Default whitelisted brands & categories | Entitlements created | **PASS ✅** |
| **P11-09** | `test_09_trial_initial_usage_records_seeded` | Initial monthly usage meter | 0 usage recorded for current month | 0 searches used | **PASS ✅** |
| **P11-10** | `test_10_trial_crm_lead_auto_created` | CRM pipeline auto-logging | Lead logged in `TRIAL` stage | Lead in TRIAL stage | **PASS ✅** |
| **P11-11** | `test_11_trial_commercial_audit_log_recorded` | Commercial audit trail | `TRIAL_SIGNUP` event logged | Audit log verified | **PASS ✅** |
| **P11-12** | `test_12_tenant_isolation_new_trial` | Tenant data cross-access check | Isolated from other tenant invoices | Isolated | **PASS ✅** |
| **P11-13** | `test_13_trial_search_entitlement_active` | Search permissions for trial tenant | Allowed to search whitelisted brands | Active search | **PASS ✅** |
| **P11-14** | `test_14_trial_search_usage_increment` | Usage meter tracking | `searches_used` incremented by 1 | Incremented | **PASS ✅** |
| **P11-15** | `test_15_annual_billing_discount_calculation` | Annual plan pricing calculation | 20% annual discount + 7% VAT | Math verified | **PASS ✅** |
| **P11-16** | `test_16_promotional_coupon_validation_commercial20` | Coupon `COMMERCIAL20` validation | Validates and deducts 20% | Coupon applied | **PASS ✅** |
| **P11-17** | `test_17_promotional_coupon_launch50` | Coupon `LAUNCH50` validation | Validates and deducts 50% | Coupon applied | **PASS ✅** |
| **P11-18** | `test_18_trial_to_paid_checkout_intent` | Payment gateway checkout intent | Generates idempotent intent | Intent created | **PASS ✅** |
| **P11-19** | `test_19_full_search_consistency_under_commercial_layer`| Search integrity under trial session | Consistent with master catalog | 100% consistent | **PASS ✅** |
| **P11-20** | `test_20_public_demo_search_vehicle_fitment` | Vehicle query in demo search | Returns matching vehicle models | Teaser fitment OK | **PASS ✅** |

---

## 3. Suite 3: Phase 6 System Owner Command Center (`scratch/test_phase6_owner_command_center.py`)

| Test ID | Method Name | Objective & Assertions | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| **P6-01** | `test_01_overview_kpis_calculation` | Executive Overview KPIs | MRR, ARR, ARPU, active orgs calculated | MRR: ฿27,810 | **PASS ✅** |
| **P6-02** | `test_02_revenue_analytics_and_daily_trend` | Real-time revenue analytics | Gross, Net, 7% VAT, payment methods | Gross: ฿21,379 | **PASS ✅** |
| **P6-03** | `test_03_customers_analytics_and_crm_funnel` | Customer analytics & CRM funnel | Conversion funnel from Lead to Paid | Conversion calculated | **PASS ✅** |
| **P6-04** | `test_04_customer_health_score_engine` | Composite Health Score (0–100) | Healthy: 100/100, At-Risk: 30/100 | Scores generated | **PASS ✅** |
| **P6-05** | `test_05_customer_360_profile_detail` | Detailed Customer 360 profile | Profile for Siam Auto Supply Co., Ltd. | Complete 360 view | **PASS ✅** |
| **P6-06** | `test_06_subscriptions_and_renewal_pipeline`| Renewal pipeline tracking | 7/14/30-day renewal pipeline | Pipeline tracked | **PASS ✅** |
| **P6-07** | `test_07_automotive_usage_and_search_intelligence`| Search BI & success rate % | Success rate %, top brands queried | Success rate: 71.5% | **PASS ✅** |
| **P6-08** | `test_08_zero_result_searches_intelligence` | Zero-result search demand extraction | Extracts catalog gaps for purchasing team | Top zero queries | **PASS ✅** |
| **P6-09** | `test_09_proactive_upgrade_opportunities` | Upgrade opportunity detector | Identifies orgs exceeding 80% quota | Upgrade list created | **PASS ✅** |
| **P6-10** | `test_10_explainable_churn_risk_detection` | Churn risk detection | Identifies at-risk accounts with reasons | Churn reasons logged | **PASS ✅** |
| **P6-11** | `test_11_plans_and_addons_performance` | Commercial plan performance | ARPU and distribution per tier | Plan metrics OK | **PASS ✅** |
| **P6-12** | `test_12_actionable_owner_alerts_lifecycle` | Real-time owner alerts lifecycle | Create, verify, and dismiss alert | Alert dismissed | **PASS ✅** |
| **P6-13** | `test_13_secure_report_export_csv_and_json` | Operational report export | CSV & JSON for all 4 report types | Reports generated | **PASS ✅** |
| **P6-14** | `test_14_owner_api_endpoints_via_http` | Owner REST API endpoints | HTTP 200 over TestClient | All endpoints 200 | **PASS ✅** |
| **P6-15** | `test_15_owner_rbac_isolation` | Non-operator role (STAFF) access | HTTP 403 Forbidden | HTTP 403 Forbidden | **PASS ✅** |
| **P6-16** | `test_16_superadmin_vs_owner_separation` | Super Admin vs Owner separation | Strict boundary enforcement | Separation verified | **PASS ✅** |

---

## 4. Reconciled Summary

- **Total Test Suites**: 3
- **Total Scenarios**: **65**
- **Passed**: **65 (100%)**
- **Failed**: **0**
- **Errors**: **0**
