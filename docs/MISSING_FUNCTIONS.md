# Missing Functions & Implementation Gaps Audit

**Generated:** 2026-09-04 19:35:46

## 1. Audit Methodology

This audit contrasts **Documented Specifications** vs **Database Schema** vs **Backend Routes** vs **Frontend UI** to identify functional gaps.

## 2. Identified Functional Gaps

| Category | Documented Function | Database Support | Backend Route (`main.py`) | Frontend UI (`index.html`) | Gap Description | Priority / Recommendation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Security** | Internal Permission Audit UI | `permissions`, `role_permissions`, `roles` | Endpoints exist | **Missing UI in SuperAdmin** | SuperAdmin needs a dedicated interactive audit explorer tab | **HIGH** (Addressed in Step 20) |
| **Users** | User Invitation Acceptance Route | `organization_invitations` | `/api/saas/organization/invite` | UI exists for inviting | Dedicated public `/invite/accept?token=...` page not explicitly rendered | **MEDIUM** |
| **Billing** | Automated Payment Gateway Webhook | `payment_transactions` | `/api/saas/webhooks/{provider}` | N/A (Backend) | Webhook handler is simulated; live Stripe/PromptPay webhook signatures needed in Phase 13 | **LOW** |
| **Catalog** | Bulk Part Import Execution | `master_parts`, `temp_parts` | `/api/parts/import` | Import modal present | UI import button triggers template download, actual XLSX parser needs streaming | **MEDIUM** |
