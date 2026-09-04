# Phase 8 Implementation Blueprint: API + Export Platform

**Date**: September 3, 2026  
**Status**: Step-by-Step Blueprint  

---

## 1. Incremental Implementation Phases

### Increment 8.1: Database Schema Migration (`008_api_and_export_platform.sql`)
- Add `environment` (`LIVE`, `TEST`), `scopes` (JSON array), `expires_at`, `ip_allowlist` to `api_keys` table.
- Create `api_request_logs` table for tracking API response codes, latency, and endpoints.
- Create `export_jobs` table (`id`, `job_uuid`, `org_id`, `user_id`, `export_type`, `file_format`, `row_count`, `file_path`, `download_token`, `status`, `expires_at`).
- Seed sample API keys, logs, and export jobs.

### Increment 8.2: Centralized Services
- Build `backend/services/api_platform_service.py`:
  - `ApiAuthenticationService`: Extracts and verifies raw key hash against active tenant context.
  - `ApiAuthorizationService`: Validates key status, expiration, scopes, rate limit, quota, and IP allowlist.
  - `ApiSearchService`: Adapts `advanced_search_parts` with public DTO filtering and public ID generation.
  - `ApiUsageService`: Atomically increments `api_calls_used` and records request logs.
- Build `backend/services/export_platform_service.py`:
  - `ExportJobService`: Queues, processes, and serializes CSV and XLSX datasets.
  - `ExportStorageService`: Generates signed download tokens with 24-hour TTL and manages secure file downloads.

### Increment 8.3: REST API Controllers in `main.py`
- Public Customer API (`/api/v1/*`):
  - `GET /api/v1/search`
  - `GET /api/v1/parts/{id}`
  - `GET /api/v1/vin/{vin}`
  - `GET /api/v1/cross-reference`
  - `GET /api/v1/vehicles/brands` & `/api/v1/vehicles/models`
  - `GET /api/v1/categories`
  - `GET /api/v1/exports/download`
- Customer Portal Management (`/api/saas/*`):
  - `GET /api/saas/api/keys` & `POST /api/saas/api/keys` & `DELETE /api/saas/api/keys/{id}`
  - `POST /api/saas/api/keys/{id}/rotate`
  - `GET /api/saas/api/analytics`
  - `POST /api/saas/exports` & `GET /api/saas/exports`
- Admin & API Staff (`/api/admin/api/*`, `/api/admin/exports/*`):
  - Customer API accounts, rate limit overrides, export job monitoring.

### Increment 8.4: Customer UI & Documentation (`index.html`)
- Customer API Management view (`#customer-sub-api`):
  - Key generator modal with 1-time secret reveal.
  - Interactive API Documentation & Request Tester (`/app/api/docs`).
  - Real-time API Usage Meters & Rate Limit status.
- Customer Export Center (`#customer-sub-exports`):
  - Export trigger dialog with row estimation and quota impact.
  - Export history table with download links and expiration status.

### Increment 8.5: Automated Test Suite & Regression Verification
- Build `scratch/test_phase8_api_and_export_platform.py` covering 20 test scenarios:
  - Authentication (valid, invalid, revoked, expired)
  - Authorization (scope checks, subscription lock, rate limits, quotas)
  - Search consistency (OEM, SKU, VIN, Cross-Ref)
  - Entitlement enforcement (Brand lock, Category lock)
  - Export jobs, data masking, signed download tokens, expiration guards
  - Admin and API Staff operational endpoints
- Run full system regression across all 8 phases (**100+ automated test scenarios passing with 100% success rate**).
