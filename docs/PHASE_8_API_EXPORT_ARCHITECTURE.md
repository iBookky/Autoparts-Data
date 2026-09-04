# Phase 8 Architecture: Customer API & Secure Export Platform

**Date**: September 3, 2026  
**Status**: Architecture Specification  

---

## 1. System Request Lifecycle

```
                                  [API Request: GET /api/v1/search]
                                                  │
                                                  ▼
                                     [ApiAuthenticationService]
                                     • Extract Bearer / X-API-Key
                                     • SHA-256 Hash Lookup in `api_keys`
                                     • Validate Key Status & Expiry
                                                  │
                                                  ▼
                                     [ApiAuthorizationService]
                                     • Verify Organization & Subscription Status
                                     • Check API Entitlement (`api_access_enabled`)
                                     • Check Key Scopes (`parts:read`, `vin:read`, etc.)
                                     • Enforce In-Memory / DB Rate Limit (Req/min)
                                     • Validate Monthly API Quota (`api_calls_used`)
                                                  │
                                                  ▼
                                        [EntitlementService]
                                     • Enforce Brand Whitelist
                                     • Enforce Category Whitelist
                                                  │
                                                  ▼
                                   [advanced_search_parts Engine]
                                     • Normalization (strip dashes/spaces)
                                     • Multi-Tier Ranking (OEM, SKU, Fitment)
                                                  │
                                                  ▼
                                         [ApiDtoTransformer]
                                     • Mask internal IDs & supplier notes
                                     • Public JSON envelope (`success`, `data`, `meta`)
                                                  │
                                                  ▼
                                         [ApiUsageTracker]
                                     • Atomically increment `api_calls_used`
                                     • Record API request log in `api_request_logs`
                                     • Append `X-Request-ID`, `X-RateLimit-*` headers
```

---

## 2. API Key Management Architecture

1. **Key Generation**:
   - Live Keys: `ap_live_<32_random_bytes>` (e.g. `ap_live_a8f9c4...`)
   - Test Keys: `ap_test_<32_random_bytes>`
   - Display Prefix: `ap_live_a8f9...`
   - Stored Hash: `SHA256(raw_key)`
   - Raw Secret: Returned **strictly once** upon creation.
2. **Granular Scopes**:
   - `parts:read`: Search and retrieve automotive parts catalog.
   - `vin:read`: Decode vehicle VINs to Year/Make/Model specs.
   - `cross_reference:read`: Access OE equivalent and replacement mappings.
   - `vehicles:read`: Access vehicle brands, models, and year applications.
   - `categories:read`: Access automotive systems and categories.
3. **Lifecycle Operations**:
   - `Create Key`: Assign name, scopes, environment, optional IP allowlist.
   - `Revoke Key`: Instantly mark `is_active = 0`.
   - `Rotate Key`: Generate new secret, set old secret to expire in 48 hours for zero-downtime migration.

---

## 3. Asynchronous Export Platform Architecture

```
User triggers Export
        ↓
[ExportAuthorizationService]
• Validate `export_enabled` entitlement
• Check monthly export quota (`exports_used` < limit)
• Enforce Brand/Category whitelists
        ↓
[ExportJobService]
• Create `export_jobs` record (`status = 'PROCESSING'`)
• Generate sanitized CSV or XLSX dataset
• Store file in secure local storage (`exports/org_<id>/<uuid>.<format>`)
• Generate single-use signed download token with 24-hour TTL
• Mark `status = 'COMPLETED'` and increment `exports_used`
        ↓
User downloads via:
`GET /api/v1/exports/download?token=<signed_token>`
```

---

## 4. Rate Limiting & Quota Management

1. **Rate Limiting**:
   - Sliding-window in-memory and database tracker per API key.
   - Headers returned on every request:
     - `X-RateLimit-Limit: 120`
     - `X-RateLimit-Remaining: 119`
     - `X-RateLimit-Reset: 1725336000`
   - When exceeded: `HTTP 429 Too Many Requests` with retry-after header.
2. **Monthly Billing Quota**:
   - Standard Plan Quotas:
     - Starter: API Disabled
     - Professional: 25,000 API calls/month, 10 exports/month
     - Business: 100,000 API calls/month, 50 exports/month
     - Enterprise: Custom / Unlimited
   - Quota exhaustion returns structured commercial error: `QUOTA_EXCEEDED` with upgrade recommendations.

---

## 5. Public Identifier & DTO Layer

To prevent internal database leakage:
- Internal autoincrement integer IDs (`master_parts.id = 224`) are mapped to public format `part_01JXXXX` or preserved via public part codes (`brand:part_number`).
- All internal fields (`created_by`, `scraper_job_id`, `raw_html`, `supplier_id`) are stripped before serialization.
