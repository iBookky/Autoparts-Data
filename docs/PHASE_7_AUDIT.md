# Phase 7 Audit: Admin & Staff Operations Layer

**Date**: September 3, 2026  
**Status**: Pre-Implementation Discovery & Gap Analysis  

---

## 1. Executive Summary

Phase 7 focuses on building the **Admin & Staff Operations Center** for internal day-to-day operations. This audit establishes the current architectural baseline, catalogues existing database entities, maps available routes and UI layouts, identifies components ready for reuse, highlights functional gaps, and surfaces security risks.

---

## 2. Current Architecture & System Inventory

### 2.1 Database Entities (Current State)
The system currently maintains 32 tables across 6 migrations:
1. **Core Automotive & Catalog**: `master_parts`, `temp_parts`, `cross_reference_relations`, `meta_aftermarket_brands`, `meta_car_brands`, `meta_car_models`, `meta_car_years`, `meta_categories`.
2. **AI & Crawler Systems**: `meta_ai_models`, `agent_skills_config`, `ai_keys_config`, `ai_usage_stats`.
3. **Multi-Tenant Organizations & Users**: `organizations`, `organization_members`, `organization_invitations`, `users`, `user_roles`, `roles`, `permissions`, `role_permissions`.
4. **Commercial Subscriptions & Billing**: `plans`, `plan_versions`, `plan_features`, `plan_entitlements`, `add_ons`, `add_on_plan_compatibility`, `subscriptions`, `subscription_items`, `subscription_entitlements_snapshot`, `coupons`, `coupon_redemptions`, `invoices`, `invoice_items`, `payment_transactions`, `usage_records`, `api_keys`.
5. **CRM & Audit**: `customer_leads`, `search_logs`, `user_favorites`, `owner_alerts`, `commercial_audit_logs`, `organization_audit_logs`, `platform_audit_logs`.

---

## 3. Existing Admin vs Staff Functionality Audit

| Feature Area | Current Implementation | Reusability | Gaps / Missing Capabilities |
| :--- | :--- | :---: | :--- |
| **Admin Shell (`/admin`)** | Legacy parts queue review (`#admin-view`), metadata catalog options, and high-level SaaS metrics row. | 30% | Currently acts as a parts queue and settings panel rather than a comprehensive **Customer Operations Center**. Missing customer list, trial management, proposal generator, renewal queue, and support tickets. |
| **Staff Workspace (`/staff`)** | Basic 3-tab layout (`#staff-view` for Sales, Data, Support) with basic lead table and unverified parts review. | 40% | Single generic staff view without role-tailored workspaces for specialized roles (`SALES_STAFF`, `CUSTOMER_SUCCESS_STAFF`, `BILLING_STAFF`, `SUPPORT_STAFF`, `DATA_STAFF`, `AI_STAFF`, `API_STAFF`). |
| **CRM Leads & Pipeline** | `customer_leads` table (`LEAD` $\rightarrow$ `CONTACTED` $\rightarrow$ `DEMO` $\rightarrow$ `TRIAL` $\rightarrow$ `PROPOSAL` $\rightarrow$ `SUBSCRIBED`). Kanban board in `/owner`. | 85% | Fully operational backend; needs dedicated Admin & Staff views with next-action dates, activity history, and lead-to-trial conversion buttons. |
| **Customer 360 Operational View** | Modal `#modal-owner-customer-360` developed in Phase 6 for System Owner. | 80% | Can be adapted into an operational Admin Customer 360 view with internal notes, staff assignment, customer status toggle, and entitlement lock indicators. |
| **Billing Operations** | `SubscriptionStateMachine`, `BillingCalculator`, `PaymentGateway`, bank transfer verification (`POST /api/admin/invoices/{id}/verify-payment`). | 90% | Backend engine is 100% complete; requires dedicated operational views for failed payments, past due accounts, and refund request processing. |
| **Support & Tickets** | No dedicated ticket table. Support tab in Staff view was a UI placeholder. | 10% | Missing `support_tickets` table, SLA priority tracking, ticket status lifecycle (`OPEN`, `IN_PROGRESS`, `WAITING_CUSTOMER`, `RESOLVED`, `CLOSED`), and customer ticket history. |
| **Staff Task Management** | No formal operational tasks table. | 0% | Missing `staff_tasks` table, task assignment, due dates, priority, status lifecycle, and filtered views (My Tasks, Unassigned, Overdue). |
| **Internal Operational Notes** | Notes exist on `customer_leads`, but no centralized internal notes repository for organizations, tickets, and tasks. | 25% | Missing dedicated `internal_notes` entity strictly isolated from external customer view. |
| **Automotive Data Verification Queue** | `temp_parts` review workflow (`approve_temp_part`, `edit_temp_part`, `reject_temp_part`) and `cross_reference_relations`. | 90% | Fully functional; needs routing to Data Staff workspace with zero-result search linking. |
| **AI Review Queue** | `meta_ai_models`, `agent_skills_config`, `ai_usage_stats`. | 70% | Needs workflow where AI-generated cross-references are flagged as `AI_MATCHED` / `REVIEW_REQUIRED` before human approval. |
| **API Management & Support** | `api_keys` table with hashed keys and rate limits. | 80% | API key secret creation, revoking, rotating, and usage monitoring ready for API Staff workspace. |

---

## 4. Security & Isolation Risks Identified

1. **Unrestricted Admin Privileges**: The current `/admin` portal partially intermingles catalog metadata configuration with operator actions. Must ensure Admin cannot execute arbitrary SQL, edit production server configuration, or alter plan pricing without Owner permission.
2. **Staff Role Overlap**: If a generic staff user logs in, they currently see tabs for all roles. Must enforce backend middleware checking specific staff sub-roles (`SALES_STAFF`, `CUSTOMER_SUCCESS_STAFF`, `BILLING_STAFF`, `SUPPORT_STAFF`, `DATA_STAFF`, `AI_STAFF`, `API_STAFF`) and dynamically restrict returned endpoints.
3. **Internal Notes Leakage Risk**: Customer-facing APIs (`/api/saas/*`) must never expose `internal_notes` or private staff assignment data.
4. **Data Publishing Guardrails**: AI-generated cross-references and Scraper outputs must never be published straight to `VERIFIED` status without explicit Human Data Staff approval.
