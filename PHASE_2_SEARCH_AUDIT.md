# Phase 2 Search Engine & Entitlement Audit (`PHASE_2_SEARCH_AUDIT.md`)

This document provides a comprehensive technical audit of the **AutoParts Cross-Ref Search Engine** prior to implementing the **Phase 2 Entitlement Whitelist & Query Protection Layer**.

---

## 1. Current Architecture

The search system is built around a **Python FastAPI backend** querying an **embedded SQLite 3 database (WAL mode)**, supplemented by asynchronous external web scrapers (`scraper.py`, `backend/web_scraper.py`) and an optional AI cross-reference engine.

```
[Customer Search Request] 
      │
      ▼
[FastAPI Route: /api/parts/search] ─── (Header: x-username, x-user-role)
      │
      ▼
[database.py: advanced_search_parts()]
      │
      ├─► [VIN Decoder (Helper if Make/Model omitted)]
      ├─► [SQL Query: master_parts (APPROVED)]
      └─► [SQL Query: temp_parts (PENDING_URGENT < 48h)]
      │
      ▼
[Response Enrichment] ──► Attaches Quality Badges (VERIFIED, REVIEWED, AI_MATCHED)
      │
      ▼
[Usage Tracking] ──► database.py: record_search_usage()
      │
      ▼
[JSON Response returned to Frontend SPA]
```

---

## 2. Existing Search Flow

1. **Client Request:** The user enters input in the Omnibar or structured filter inputs (`car_brand`, `car_model`, `car_year`, `category`, `oem_code`, `oem_name`, `aftermarket_brand`, `aftermarket_part`, `vin`).
2. **VIN Helper Extraction:** If `vin` is provided and vehicle specifications (`car_brand`, `car_model`, `car_year`) are blank, `decode_vin_wmi_specs()` and `get_model_from_vds()` decode the vehicle make, model, and year to populate search parameters.
3. **Dynamic WHERE Construction:** SQL clauses are concatenated with `AND` based on supplied parameters.
4. **Union Query Execution:** 
   - `master_parts` is queried for approved verified parts.
   - `temp_parts` is queried for recently scraped urgent pending parts (TTL < 48h).
5. **Quality Badge Enrichment:** Results are tagged as `VERIFIED`, `REVIEWED`, `AI_MATCHED`, or `UNVERIFIED`.
6. **Usage Counter:** Invokes `record_search_usage()` to increment `searches_used` in `usage_records`.
7. **Rendering:** Results are rendered in the hybrid table with clickable drawer triggers.

---

## 3. Search Endpoints

| Endpoint | Method | Purpose | Current Authorization |
| :--- | :--- | :--- | :--- |
| `/api/parts/search` | `GET` | Core parts search (multi-filter) | Public / Header optional |
| `/api/parts/decode-vin` | `GET` | Universal VIN decoding (NHTSA, ISO, VDS) | Public / Header optional |
| `/api/parts/cross-reference-matrix` | `GET` | Typed cross-reference matrix | Public / Header optional |
| `/api/parts/live-search` | `POST` | On-demand live worldwide scraping | Optional Auth Header |
| `/api/parts/ai-search` | `POST` | AI-assisted cross-reference search | Optional Auth Header |
| `/api/saas/data-coverage` | `GET` | Customer brand & category coverage | Tenant Context |
| `/api/saas/usage` | `GET` | Monthly search quota meters | Tenant Context |

---

## 4. Database Tables & Entities Involved

1. **`master_parts` (24+ production rows):** Verified automotive parts (`id`, `brand`, `part_number`, `oem_number`, `product_name_th`, `product_name_en`, `category`, `car_brand`, `car_model`, `year_start`, `year_end`, `engine_specs`, `price_thb`).
2. **`temp_parts`:** Scraped quarantine queue (`status` = `PENDING`, `PENDING_URGENT`, `APPROVED`, `REJECTED`).
3. **`meta_car_brands`, `meta_car_models`, `meta_car_years`, `meta_categories`, `meta_aftermarket_brands`:** Master lookup tables.
4. **`organizations`, `subscriptions`, `plans`:** Tenant subscription data.
5. **`entitlements`:** Database-driven whitelist rules (`org_id`, `entitlement_type`, `entitlement_value`, `is_granted`).
6. **`usage_records` & `search_logs`:** Quota meters and search audit history.
7. **`cross_reference_relations`:** Typed relationships (`EQUIVALENT`, `REPLACEMENT`, `CROSS_REFERENCE`, `SUPERSEDES`, `ALTERNATIVE`).

---

## 5. Existing Filters

* **Vehicle Brand:** `car_brand LIKE ?`
* **Vehicle Model:** `car_model LIKE ?`
* **Vehicle Year:** `(? BETWEEN year_start AND year_end OR year_start LIKE ? OR year_end LIKE ?)`
* **Category:** `category LIKE ?`
* **OEM Number:** `oem_number LIKE ?`
* **Product Name:** `(product_name_th LIKE ? OR product_name_en LIKE ?)`
* **Aftermarket Brand:** `brand = ?`
* **Aftermarket SKU:** `part_number LIKE ?`

---

## 6. Existing Ranking Logic

Currently, query matching returns rows based on SQL selection order (`master_parts` followed by `temp_parts`).
* **Master vs Temp:** `master_parts` results appear first (tagged `VERIFIED`).
* **No explicit scoring/ranking:** An exact match on OEM code currently shares equal sorting weight with a partial substring match.

---

## 7. Existing Authorization & Gaps

* **Current State:** 
  * Tenant context is identified via `x-username` header.
  * Quota usage is recorded after the search completes.
* **Gaps Identified:**
  1. No server-side gate rejects searches when `searches_used >= searches_quota` (HTTP 402).
  2. SQL queries do not filter by tenant `entitlements` before querying `master_parts`.
  3. Direct API requests (e.g. `GET /api/parts/search?car_brand=Ford`) by a tenant without Ford entitlement currently return data instead of a commercial locked response.

---

## 8. Existing Performance Analysis

* **Strengths:** 
  * Lightweight indexed SQLite database with WAL mode provides sub-15ms response times for local catalog queries.
* **Bottlenecks:**
  * Substring `LIKE '%query%'` patterns cannot leverage standard B-tree indexes for large datasets.
  * Lack of search normalization creates potential redundant searches (e.g. `90915-YZZD1` vs `90915YZZD1`).

---

## 9. Existing Security Risks

1. **Unauthorized Data Exposure:** If a customer on a Starter Plan (1 Brand only) queries a non-subscribed brand via direct API parameters, raw product data is currently returned.
2. **Quota Circumvention:** A customer exceeding their 5,000 search limit could continue making API calls because quota exhaustion does not block execution.
3. **Cross-Tenant Organization Leaks:** Organization ID could potentially be spoofed if not validated against session user ownership.

---

## 10. Recommended Improvements for Phase 2

1. **Centralized Entitlement & Quota Service (`EntitlementService`):**
   - Check `canSearch()`, `canAccessBrand()`, `canAccessCategory()`, and `canAccessProduct()` before executing SQL.
2. **Entitlement-Aware SQL Querying:**
   - Automatically inject tenant's authorized brand/category whitelist into SQL `WHERE` clauses.
3. **Search Normalization Layer:**
   - Normalize OEM and SKU strings (strip hyphens, spaces, uppercase) while preserving original values for display.
4. **Relevance Ranking & Scoring:**
   - Exact OEM (Score 100) $\rightarrow$ Exact SKU (Score 90) $\rightarrow$ Normalized Match (Score 80) $\rightarrow$ Vehicle Fitment (Score 70) $\rightarrow$ Partial Substring (Score 50).
5. **Commercial Locked-State Response:**
   - When querying locked brands/categories, return commercial upgrade prompts with pricing rather than leaking raw data.
6. **Comprehensive Security Test Matrix (13 Automated Security Tests).**
