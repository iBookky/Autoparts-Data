# Authoritative API Permission Matrix

**Generated:** 2026-09-04 19:35:46
**Total API Endpoints Audited:** 113

| # | Method | Path | Handler Endpoint | Required Role | Organization Scope | Subscription | Entitlement | Customer Allowed? | Customer Denied? | Extraction Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `POST` | `/api/auth/login` | `login` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 2 | `POST` | `/api/auth/register-trial` | `register_trial` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 3 | `POST` | `/api/public/leads/contact` | `public_contact_lead` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 4 | `GET` | `/api/public/coverage-stats` | `get_public_coverage_stats` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 5 | `GET` | `/api/public/demo-search` | `public_demo_search` | `PUBLIC` | Public / None | None | SEARCH_QUOTA | YES | NO | NONE |
| 6 | `GET` | `/api/admin/users` | `get_users` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 7 | `POST` | `/api/admin/users` | `create_user` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 8 | `DELETE` | `/api/admin/users/{user_id}` | `delete_user` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 9 | `GET` | `/api/parts/search` | `search_parts` | `AUTHENTICATED` | Public / None | ACTIVE | SEARCH_QUOTA | YES | NO | NONE |
| 10 | `GET` | `/api/parts/product/{part_id}` | `get_product_detail` | `AUTHENTICATED` | Public / None | ACTIVE | None | YES | NO | NONE |
| 11 | `POST` | `/api/parts/ai-search` | `ai_search` | `PUBLIC` | Public / None | None | AI_SEARCH (Tier: PRO+) | YES | NO | NONE |
| 12 | `POST` | `/api/parts/live-search` | `live_search` | `PUBLIC` | Public / None | None | SEARCH_QUOTA | YES | NO | NONE |
| 13 | `POST` | `/api/admin/scrape-url` | `admin_scrape_url` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 14 | `POST` | `/api/admin/save-scraped-preview` | `save_scraped_preview` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 15 | `GET` | `/api/parts/export-import-template` | `export_import_template` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | HIGH (Blocked) |
| 16 | `POST` | `/api/parts/import` | `import_parts` | `ADMIN` | Platform Global | ACTIVE | None | YES | NO | NONE |
| 17 | `GET` | `/api/admin/all-parts` | `admin_all_parts` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 18 | `GET` | `/api/admin/temp-parts` | `admin_get_temp_parts` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 19 | `POST` | `/api/parts/staff-note` | `add_staff_note` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 20 | `POST` | `/api/admin/review/{id}` | `admin_review_action` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 21 | `POST` | `/api/admin/master/review/{id}` | `admin_master_review_action` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 22 | `GET` | `/api/parts/decode-vin` | `decode_vin_endpoint` | `PUBLIC` | Public / None | None | VIN_LOOKUP (Tier: PRO+) | YES | NO | NONE |
| 23 | `GET` | `/api/metadata/aftermarket-brands` | `get_metadata_aftermarket_brands` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 24 | `GET` | `/api/metadata/car-brands` | `get_metadata_car_brands` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 25 | `GET` | `/api/metadata/car-models` | `get_metadata_car_models` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 26 | `GET` | `/api/metadata/car-years` | `get_metadata_car_years` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 27 | `GET` | `/api/metadata/categories` | `get_metadata_categories` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
| 28 | `GET` | `/api/metadata/ai-models` | `get_metadata_ai_models` | `PUBLIC` | Public / None | None | AI_SEARCH (Tier: PRO+) | YES | NO | NONE |
| 29 | `GET` | `/api/admin/agent-skills` | `get_metadata_agent_skills` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 30 | `POST` | `/api/admin/agent-skills/{key}/toggle` | `toggle_metadata_agent_skill` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 31 | `POST` | `/api/admin/metadata/aftermarket-brands` | `create_metadata_aftermarket_brand` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 32 | `POST` | `/api/admin/metadata/car-brands` | `create_metadata_car_brand` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 33 | `POST` | `/api/admin/metadata/car-models` | `create_metadata_car_model` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 34 | `POST` | `/api/admin/metadata/car-years` | `create_metadata_car_year` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 35 | `POST` | `/api/admin/metadata/categories` | `create_metadata_category` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 36 | `POST` | `/api/admin/metadata/ai-models` | `create_metadata_ai_model` | `ADMIN` | Platform Global | ACTIVE | AI_SEARCH (Tier: PRO+) | NO | YES (403) | NONE |
| 37 | `DELETE` | `/api/admin/metadata/aftermarket-brands/{id}` | `delete_metadata_aftermarket_brand` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 38 | `DELETE` | `/api/admin/metadata/car-brands/{id}` | `delete_metadata_car_brand` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 39 | `DELETE` | `/api/admin/metadata/car-models/{id}` | `delete_metadata_car_model` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 40 | `DELETE` | `/api/admin/metadata/car-years/{id}` | `delete_metadata_car_year` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 41 | `DELETE` | `/api/admin/metadata/categories/{id}` | `delete_metadata_category` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 42 | `DELETE` | `/api/admin/metadata/ai-models/{id}` | `delete_metadata_ai_model` | `ADMIN` | Platform Global | ACTIVE | AI_SEARCH (Tier: PRO+) | NO | YES (403) | NONE |
| 43 | `PUT` | `/api/admin/metadata/aftermarket-brands/{id}` | `update_metadata_aftermarket_brand` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 44 | `PUT` | `/api/admin/metadata/car-brands/{id}` | `update_metadata_car_brand` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 45 | `PUT` | `/api/admin/metadata/car-models/{id}` | `update_metadata_car_model` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 46 | `PUT` | `/api/admin/metadata/car-years/{id}` | `update_metadata_car_year` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 47 | `PUT` | `/api/admin/metadata/categories/{id}` | `update_metadata_category` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 48 | `GET` | `/api/superadmin/ai-keys` | `superadmin_get_ai_keys` | `SUPER_ADMIN` | Platform Global | ACTIVE | AI_SEARCH (Tier: PRO+) | NO | YES (403) | NONE |
| 49 | `POST` | `/api/superadmin/ai-keys` | `superadmin_save_ai_key` | `SUPER_ADMIN` | Platform Global | ACTIVE | AI_SEARCH (Tier: PRO+) | NO | YES (403) | NONE |
| 50 | `POST` | `/api/superadmin/ai-keys/{id}/activate` | `superadmin_activate_ai_key` | `SUPER_ADMIN` | Platform Global | ACTIVE | AI_SEARCH (Tier: PRO+) | NO | YES (403) | NONE |
| 51 | `DELETE` | `/api/superadmin/ai-keys/{id}` | `superadmin_delete_ai_key` | `SUPER_ADMIN` | Platform Global | ACTIVE | AI_SEARCH (Tier: PRO+) | NO | YES (403) | NONE |
| 52 | `GET` | `/api/superadmin/ai-usage` | `superadmin_get_ai_usage` | `SUPER_ADMIN` | Platform Global | ACTIVE | AI_SEARCH (Tier: PRO+) | NO | YES (403) | NONE |
| 53 | `GET` | `/api/saas/context` | `get_saas_context` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 54 | `GET` | `/api/saas/plans` | `get_saas_plans` | `PUBLIC` | Organization Scoped | None | None | YES | NO | LOW |
| 55 | `GET` | `/api/saas/plans/{plan_id}` | `get_saas_plan_by_id` | `PUBLIC` | Organization Scoped | None | None | YES | NO | LOW |
| 56 | `GET` | `/api/saas/add-ons` | `get_saas_addons` | `PUBLIC` | Organization Scoped | None | None | YES | NO | LOW |
| 57 | `POST` | `/api/saas/billing/calculate` | `calculate_saas_billing` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 58 | `POST` | `/api/saas/coupons/validate` | `validate_saas_coupon` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 59 | `GET` | `/api/saas/subscription` | `get_saas_subscription` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 60 | `POST` | `/api/saas/subscription/upgrade` | `upgrade_saas_subscription` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 61 | `POST` | `/api/saas/subscription/downgrade` | `downgrade_saas_subscription` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 62 | `POST` | `/api/saas/subscription/cancel` | `cancel_saas_subscription` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 63 | `POST` | `/api/saas/subscription/reactivate` | `reactivate_saas_subscription` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 64 | `POST` | `/api/saas/payments/charge` | `charge_payment` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 65 | `POST` | `/api/saas/webhooks/{provider}` | `handle_payment_webhook` | `PUBLIC` | Organization Scoped | None | None | YES | NO | LOW |
| 66 | `POST` | `/api/admin/invoices/{invoice_id}/verify-payment` | `verify_corporate_invoice_payment` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 67 | `GET` | `/api/saas/invoices/{invoice_id}` | `get_saas_invoice_detail` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 68 | `GET` | `/api/saas/data-coverage` | `get_saas_data_coverage` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 69 | `GET` | `/api/saas/usage` | `get_saas_usage` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 70 | `GET` | `/api/saas/favorites` | `get_saas_favorites` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 71 | `POST` | `/api/saas/favorites/toggle` | `toggle_saas_favorite` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 72 | `GET` | `/api/saas/history` | `get_saas_history` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 73 | `DELETE` | `/api/saas/history/{log_id}` | `delete_saas_history_item` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 74 | `GET` | `/api/saas/api-keys` | `get_saas_api_keys` | `AUTHENTICATED` | Organization Scoped | ACTIVE | API_ACCESS (Tier: BIZ+) | YES | NO | LOW |
| 75 | `POST` | `/api/saas/api-keys` | `create_saas_api_key` | `AUTHENTICATED` | Organization Scoped | ACTIVE | API_ACCESS (Tier: BIZ+) | YES | NO | LOW |
| 76 | `DELETE` | `/api/saas/api-keys/{key_id}` | `delete_saas_api_key` | `AUTHENTICATED` | Organization Scoped | ACTIVE | API_ACCESS (Tier: BIZ+) | YES | NO | LOW |
| 77 | `GET` | `/api/saas/invoices` | `get_saas_invoices` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 78 | `GET` | `/api/admin/saas/metrics` | `get_saas_metrics` | `ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | LOW |
| 79 | `POST` | `/api/saas/export` | `export_saas_parts` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | NO | YES (403) | HIGH (Blocked) |
| 80 | `GET` | `/api/saas/organization` | `get_saas_organization` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 81 | `PUT` | `/api/saas/organization` | `update_saas_organization` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 82 | `GET` | `/api/saas/organization/members` | `get_saas_org_members` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 83 | `POST` | `/api/saas/organization/invite` | `invite_saas_org_member` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 84 | `GET` | `/api/saas/organization/invitations` | `get_saas_org_invitations` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 85 | `DELETE` | `/api/saas/organization/invitations/{invitation_id}` | `revoke_saas_org_invitation` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 86 | `PUT` | `/api/saas/organization/members/{target_user_id}/role` | `update_saas_member_role` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 87 | `PUT` | `/api/saas/organization/members/{target_user_id}/status` | `update_saas_member_status` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 88 | `DELETE` | `/api/saas/organization/members/{target_user_id}` | `remove_saas_member` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 89 | `GET` | `/api/saas/organization/audit` | `get_saas_org_audit` | `AUTHENTICATED` | Organization Scoped | ACTIVE | None | YES | NO | LOW |
| 90 | `GET` | `/api/owner/overview` | `get_owner_overview_metrics` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 91 | `GET` | `/api/owner/metrics` | `get_owner_overview_metrics` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 92 | `GET` | `/api/owner/revenue` | `get_owner_revenue_analytics` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 93 | `GET` | `/api/owner/customers` | `get_owner_customers_analytics` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 94 | `GET` | `/api/owner/customers/{org_id}/360` | `get_owner_customer_360` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 95 | `GET` | `/api/owner/subscriptions` | `get_owner_subscriptions_analytics` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 96 | `GET` | `/api/owner/search-analytics` | `get_owner_automotive_usage_analytics` | `SYSTEM_OWNER` | Platform Global | ACTIVE | SEARCH_QUOTA | NO | YES (403) | NONE |
| 97 | `GET` | `/api/owner/usage` | `get_owner_automotive_usage_analytics` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 98 | `GET` | `/api/owner/opportunities` | `get_owner_opportunities_and_health` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 99 | `GET` | `/api/owner/plans-performance` | `get_owner_plans_performance` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 100 | `GET` | `/api/owner/alerts` | `get_owner_alerts_list` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 101 | `POST` | `/api/owner/alerts/{alert_id}/dismiss` | `dismiss_owner_alert_endpoint` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 102 | `GET` | `/api/owner/reports/export` | `export_owner_report` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | HIGH (Blocked) |
| 103 | `GET` | `/api/owner/pipeline` | `get_pipeline_leads` | `SYSTEM_OWNER, STAFF` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 104 | `POST` | `/api/owner/pipeline` | `create_pipeline_lead` | `SYSTEM_OWNER, STAFF` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 105 | `PUT` | `/api/owner/pipeline/{lead_id}/stage` | `update_pipeline_lead_stage` | `SYSTEM_OWNER, STAFF` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 106 | `GET` | `/api/owner/roles` | `get_roles_and_permissions` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 107 | `POST` | `/api/owner/roles/permission` | `update_permission_toggle` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 108 | `PUT` | `/api/owner/plans/{plan_id}` | `edit_plan_pricing` | `SYSTEM_OWNER` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 109 | `GET` | `/api/superadmin/system-health` | `get_system_health` | `SUPER_ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 110 | `GET` | `/api/superadmin/audit-logs` | `get_audit_trail` | `SUPER_ADMIN, ADMIN` | Platform Global | ACTIVE | None | NO | YES (403) | NONE |
| 111 | `GET` | `/api/parts/cross-reference-matrix` | `get_cross_ref_matrix` | `PUBLIC` | Public / None | None | CROSS_REFERENCE | YES | NO | NONE |
| 112 | `GET` | `/api/staff/tasks` | `get_staff_tasks` | `STAFF` | Platform Global | ACTIVE | None | YES | NO | NONE |
| 113 | `GET` | `/` | `get_index` | `PUBLIC` | Public / None | None | None | YES | NO | NONE |
