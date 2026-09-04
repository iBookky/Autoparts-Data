# Phase 8: Secure Export Platform Specification

**Date**: September 3, 2026  
**Status**: Export Specification  

---

## 1. Export Types & Supported Formats

| Export Type | Supported Formats | Max Rows Per Job | Entitlement Required | Quota Deducted |
| :--- | :---: | :---: | :--- | :---: |
| **Search Results Export** | `CSV`, `XLSX` | 10,000 | `export_enabled = true` | 1 Export Job |
| **Cross-Reference Matrix** | `CSV`, `XLSX` | 25,000 | `export_enabled = true` + `cross_ref` | 1 Export Job |
| **Vehicle Applications List** | `CSV`, `XLSX` | 10,000 | `export_enabled = true` | 1 Export Job |
| **Customer Usage Audit** | `CSV`, `JSON` | 5,000 | `export_enabled = true` | 1 Export Job |

---

## 2. Export Data Masking & DTO Rules

To safeguard proprietary supplier data and internal operations, the following fields are strictly **excluded** from customer export files:
- ❌ Internal Database IDs (`id`, `org_id`, `created_by_user_id`)
- ❌ Raw Scraper URLs and Source Identifiers
- ❌ Internal Data Verification Notes
- ❌ AI Prompt Logs & Raw Embeddings
- ❌ Supplier Pricing & Cost Basis

**Included Public Fields**:
- ✅ Brand Name (Aftermarket)
- ✅ Part Number / SKU
- ✅ OEM Number
- ✅ Product Name (TH & EN)
- ✅ Category Name
- ✅ Vehicle Make, Model, Year Range
- ✅ Verification Status (`VERIFIED` / `REVIEWED`)
- ✅ Cross-Reference Equivalents & Type

---

## 3. Storage & Download Lifecycle

1. **Storage Location**: `exports/org_<id>/<job_uuid>.<format>`
2. **Download Token**: Cryptographically signed SHA-256 token linked to `export_jobs.id`.
3. **Expiration TTL**: 24 hours from creation (`expires_at = datetime('now', '+24 hours')`).
4. **Cleanup Worker**: Auto-deletes expired physical files after 48 hours while maintaining historical audit records in `export_jobs`.
