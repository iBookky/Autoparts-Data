# Phase 7: Granular Role & Permission Matrix

**Date**: September 3, 2026  
**Status**: Authorization Specification  

---

## 1. Role Definitions & Portals

| Role ID | Role Name | Portal | Scope / Responsibility |
| :--- | :--- | :---: | :--- |
| `owner` | **System Owner** | `/owner` | Highest commercial and revenue authority. Controls MRR, pricing, policies. |
| `super_admin` | **Super Admin** | `/super-admin` | Technical & data authority. Infrastructure, raw DB, crawlers, AI config. |
| `admin` | **Operations Admin** | `/admin` | Customer operations center. Manages customer lifecycle, billing, tickets, tasks. |
| `staff_sales` | **Sales Staff** | `/staff` | Leads, trials, demos, proposals, sales task execution. |
| `staff_cs` | **Customer Success** | `/staff` | Onboarding, customer health, renewal check-ins, retention tasks. |
| `staff_billing` | **Billing Staff** | `/staff` | Invoices, payment confirmations, failed payment retries, refunds. |
| `staff_support` | **Support Staff** | `/staff` | Support tickets, customer search inquiries, technical troubleshooting. |
| `staff_data` | **Data Staff** | `/staff` | Zero-result analysis, parts review queue, fitment/cross-ref verification. |
| `staff_ai` | **AI Staff** | `/staff` | AI matching review queue, AI confidence validation, AI job monitoring. |
| `staff_api` | **API Staff** | `/staff` | API accounts, rate limits, token rotation, API troubleshooting. |
| `customer_owner` | **Customer Owner** | `/app` | External tenant admin. Manages team seats, views billing, upgrades plan. |
| `customer_member`| **Customer Staff** | `/app` | External tenant member. Parts search, VIN decoding, bookmarks. |

---

## 2. Action Permission Matrix

| Operational Action | Owner | Super Admin | Admin | Sales Staff | CS Staff | Billing Staff | Support Staff | Data Staff | AI Staff | API Staff | Customer |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **View MRR / Financial BI** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Manage Plans & Pricing** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Manage Infrastructure & DB** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **View Customer Organizations** | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ (Own Org Only) |
| **Edit Customer Org Details** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Own Org Only) |
| **Assign Customer to Staff** | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Manage CRM Leads** | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Extend Trial Period** | ✅ | ❌ | ✅ (Audited) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Create Commercial Proposal** | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Modify Subscriptions** | ✅ | ❌ | ✅ (Audited) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Upgrade/Cancel Own) |
| **Verify Bank Transfers** | ✅ | ❌ | ✅ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Manage Support Tickets** | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ (Create/View Own) |
| **Create & Assign Tasks** | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Add Internal Notes** | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Review Scraped Raw Parts** | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Review AI Match Queue** | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **Manage API Keys & Quotas** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ (Own Keys) |
| **Execute Automotive Search** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Entitlement Gated) |
| **Direct DB SQL Execution** | ❌ | ✅ (CLI only) | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
