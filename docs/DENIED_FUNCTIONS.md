# Permanent Customer Deny List & Security Invariants

**Generated:** 2026-09-04 19:35:46

## 1. Architectural Policy

The platform enforces a zero-tolerance policy against automotive dataset extraction, catalog scraping, tenant data leakage, and role escalation.

## 2. Permanent Deny Inventory

| Denied Function | Prohibited Roles | Threat / Risk Model | Backend Enforcement Mechanism | Verification Status |
| :--- | :--- | :--- | :--- | :--- |
| **Automotive Data CSV Export** | All Customer Roles (`CUSTOMER_OWNER`, `CUSTOMER_MANAGER`, `CUSTOMER_STAFF`) | Intellectual Property Theft & Bulk Resale | `/api/saas/export` rejects customer roles with `HTTP 403 Forbidden` | **VERIFIED ENFORCED** |
| **Automotive Data Excel/JSON Export** | All Customer Roles | Catalog Extraction & Exfiltration | No customer export endpoints exist; UI export buttons removed | **VERIFIED ENFORCED** |
| **Direct Database / SQL Execution** | All Customer Roles, All Staff Roles, System Owner | Complete Data Compromise & Schema Corruption | No raw SQL endpoint exists; SQLite connection parameterization | **VERIFIED ENFORCED** |
| **Web Scraper & Crawler Controls** | All Customer Roles, Admin, Staff | IP Rate Limiting & Bot Ingestion Abuse | `/api/admin/scrape-url` guarded by `require_super_admin` | **VERIFIED ENFORCED** |
| **Master Catalog Modification** | All Customer Roles, Admin, Staff | Unverified Part Corruption | Master parts updates restricted strictly to `SUPER_ADMIN` | **VERIFIED ENFORCED** |
| **Cross-Tenant Data Access** | All Customer Roles | Cross-Organization Information Disclosure | Queries strictly scoped by `organization_members.org_id` | **VERIFIED ENFORCED** |
| **Client Role Switching** | All Customer Roles | Horizontal & Vertical Privilege Escalation | Role switchers eliminated from UI; Token/Session resolution | **VERIFIED ENFORCED** |
| **AI API Key Pool Configuration** | All Customer Roles, Staff, System Owner | LLM Secret Leakage & API Cost Overrun | AI API keys isolated in `/api/superadmin/ai-keys` | **VERIFIED ENFORCED** |
| **AI Catalog Dump / Extraction** | All Customer Roles | Vector / Prompt-based Scrape Attack | Pagination limited to 50 items/call, rate limits active | **VERIFIED ENFORCED** |

## 3. Commercial Audit of Historical Export Products

- In `add_ons` table: `export_pack` is permanently marked `status = 'ARCHIVED'`.
- In `plan_features` table: `EXPORT` feature is disabled (`is_enabled = 0`) across all 4 tiers (`STARTER`, `PROFESSIONAL`, `BUSINESS`, `ENTERPRISE`).
- Historical financial records remain intact for accounting integrity without granting active permissions.
