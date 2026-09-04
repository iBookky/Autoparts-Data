# Phase 8 Audit: API + Export Platform

**Date**: September 3, 2026  
**Status**: Pre-Implementation Discovery & Gap Analysis  

---

## 1. Executive Summary

Phase 8 introduces the **Customer API & Export Platform**, delivering secure programmatic REST API access (`/api/v1/*`) and asynchronous file export capabilities (`/app/exports`, `/admin/exports`) for paying B2B customers.

This audit evaluates the current state of API keys, search query endpoints, entitlement checks, usage tracking, file generation, rate limiting, and database models.

---

## 2. Current Architecture & System Inventory

### 2.1 Current API Subsystem Audit
1. **API Key Storage (`api_keys`)**:
   - `002_saas_commercial_layer.sql` defined `api_keys(id, org_id, name, key_prefix, key_hash, rate_limit_per_min, is_active, last_used_at, created_at)`.
   - Keys are SHA-256 hashed on creation (`create_api_key` in `backend/database.py`).
   - Plaintext secret is returned only once on generation (`ap_...`).
   - **Gaps**: Missing API scopes (`parts:read`, `vin:read`, `xref:read`, `vehicles:read`), expiration dates, environment tags (`LIVE` / `TEST`), and request counters per key.
2. **Current API Search & Endpoints**:
   - Web application currently communicates via `/api/saas/search/advanced` and `/api/parts/*`.
   - **Gaps**: No public versioned REST API (`/api/v1/*`) with standardized JSON envelope (`success`, `data`, `meta`, `error`, `request_id`).
3. **API Authentication & Authorization Middleware**:
   - Current endpoints authenticate via `x-username` header and JWT tokens.
   - **Gaps**: Missing `X-API-Key` / `Bearer ap_...` authentication handler that maps incoming raw keys to organization tenant context, validates active subscription status, checks API entitlement (`api_access_enabled`), checks rate limits, and deducts monthly API quota.

---

### 2.2 Current Export Subsystem Audit
1. **Current Export Endpoints**:
   - `POST /api/saas/export`: Synchronously streams a CSV of filtered parts.
   - `GET /api/owner/reports/export`: Synchronously streams owner financial reports.
2. **Gaps in Export Engine**:
   - Synchronous generation will timeout on large datasets (>5,000 rows).
   - Missing asynchronous export job queue (`export_jobs` table).
   - Missing secure download tokens with expiration TTL (24 hours).
   - Missing XLSX format support.
   - Missing data masking/DTO layer to prevent exposing internal verification notes, database IDs, or AI confidence scores.
   - Missing export quota enforcement (monthly export limits based on plan/add-ons).

---

### 2.3 Search Engine & Entitlement Integration
- **`EntitlementService`** ([`backend/services/entitlement_service.py`](file:///Users/ibookky/Autoparts/backend/services/entitlement_service.py)):
  - Validates brand whitelists, category whitelists, subscription status, and search quotas.
  - Generates commercial lock responses (`BRAND_LOCKED`, `CATEGORY_LOCKED`, `QUOTA_EXCEEDED`, `SUBSCRIPTION_INACTIVE`).
  - **Ready for direct reuse** by the API controller layer to ensure 100% search consistency between Web UI and REST API.
- **`advanced_search_parts`** ([`backend/database.py`](file:///Users/ibookky/Autoparts/backend/database.py)):
  - Normalized part number search, OEM code matching, vehicle fitment lookup, and multi-tier relevance scoring (100 = Exact OEM, 95 = Exact SKU, 80 = Normalized partial, 70 = Vehicle fitment).
  - **Ready for direct reuse** by `/api/v1/search`.

---

### 2.4 Usage Records Integration
- **`usage_records` table**:
  - Contains `api_calls_used`, `exports_used`, `searches_used`, `vin_lookups_used`, `ai_credits_used` per `(org_id, period_month)`.
  - Database helpers exist for recording search usage; need dedicated atomic helpers for `record_api_call_usage` and `record_export_usage`.

---

## 3. Security Risks Identified

1. **Mass Data Scraping / Extraction via API**: Without rate limits and pagination caps, malicious API clients could enumerate and dump the entire master catalog.
2. **Entitlement Bypass**: An API caller could attempt to query unentitled categories or brands directly without going through UI dropdown restrictions.
3. **Storage Exposure**: Export files stored on disk could be accessed directly without tenant authentication if predictable URLs are used.
4. **Internal Field Leakage**: Internal supplier codes, AI prompts, or verification notes could inadvertently be leaked in API JSON responses or CSV exports.
