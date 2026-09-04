# Phase 12 — Permanent Anti-Exfiltration & Data Protection Policy

**Objective**: Formal specification of the automotive catalog data protection policy and anti-exfiltration controls.

---

## 1. Core Policy Directives

1. **EXPORT_AUTOMOTIVE_DATA = DENY**:
   - Customer roles (`CUSTOMER_OWNER`, `CUSTOMER_MEMBER`, `STAFF`) must NEVER be able to export, download, or dump automotive master catalog data.
2. **Export is NOT a Commercial Product**:
   - Export is not a customer feature.
   - Export is not a premium feature.
   - Export is not an add-on.
   - Export is not a capacity booster.
   - Export is not a paid upgrade.
   - Export is not an API substitute.
3. **Server-Side Denial Contract**:
   - Calling `POST /api/saas/export` returns HTTP `403 Forbidden` with:
     ```json
     {
       "detail": "Automotive data export is not available for this account."
     }
     ```
4. **Historical Add-on Archival**:
   - Historical `export_pack` add-on rows in database are marked `status = 'ARCHIVED'` and cannot be assigned, purchased, or activated.
   - `plan_features` for `EXPORT` are permanently set to `is_included = 0`.
5. **Pagination & Query Clamping**:
   - All search queries enforce server-side `LIMIT 50` hard cap.
   - Response DTO strips sensitive supplier notes, cost prices, and scraper metadata.
   - AI search recommendations capped at $\le 5$ items.
