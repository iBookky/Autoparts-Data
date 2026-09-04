# Phase 12 — Cross-Reference Root Cause Analysis & Recovery Plan

**Objective**: Comprehensive diagnostic trace, error reproduction, root cause categorization, and verified recovery strategy for the Cross-Reference engine.

---

## 1. Reproduction Matrix & Failure Trace

We tested 5 primary entry points into the Cross-Reference subsystem:

| Test Entry Point | Input Tested | Expected Outcome | Actual Outcome | HTTP Code / Client State | Error Classification |
|---|---|---|---|---|---|
| **1. Cross-Ref Omnibar** | `04465-0K360` | Display TRW, BOSCH, AISIN, BREMBO equivalents | **Uncaught TypeError** in browser console | HTTP 200 (Backend) / UI Crashed | **Client Schema Mismatch** |
| **2. Search Result → Drawer** | Click Part #1 (`514937`) | Tab "Cross Ref" shows count & relations | Tab showed `Cross Ref (0)` | HTTP 200 / Empty `[]` | **Server Property Mismatch** |
| **3. Direct API Call** | `GET /api/parts/cross-reference-matrix?part_number=04465-0K360` | Return filtered relation records | Returned 4 valid relations | HTTP 200 | Backend Query OK |
| **4. Nav Item Click** | Click `Cross Reference` in sidebar | Render relation table | **Silent Failure** (No table rendered) | DOM Exception | **Nonexistent DOM Target** |
| **5. Empty Search Query** | `XYZ-999-NOT-FOUND` | Display polite empty state message | Empty table with `No cross-reference relationship found` | HTTP 200 | Handled gracefully |

---

## 2. Root Cause Breakdown (Categorized)

### Root Cause A: Client-Side Property Mismatch (`r.source_part` vs `r.source_part_number`)
- **File**: `index.html` (Lines 4338–4340)
- **Defective Code**:
  ```javascript
  const matchedRelations = relations.filter(r => 
      r.source_part.replace(/[\s\-_.\/]+/g, '').toUpperCase() === cleanCode || 
      r.target_part.replace(/[\s\-_.\/]+/g, '').toUpperCase() === cleanCode
  );
  ```
- **Analysis**: The database table `cross_reference_relations` defines columns `source_part_number` and `target_part_number`. When the client accessed `r.source_part`, it evaluated to `undefined`, and invoking `.replace(...)` triggered a fatal runtime exception:
  `TypeError: Cannot read properties of undefined (reading 'replace')`.
  This terminated execution before the table could render.

---

### Root Cause B: Server-Side Property Mismatch in `get_product_detail`
- **File**: `main.py` (Lines 418–423)
- **Defective Code**:
  ```python
  for cr in cross_refs:
      if (oem and cr.get("source_part") == oem) or (sku and cr.get("source_part") == sku) or \
         (oem and cr.get("target_part") == oem) or (sku and cr.get("target_part") == sku):
          related_cross_refs.append(cr)
  ```
- **Analysis**: Because `cr` contains keys `source_part_number` and `target_part_number`, `cr.get("source_part")` always returned `None`. Consequently, `related_cross_refs` was always empty `[]`, leaving the Product Drawer Cross-Reference tab blank even when valid relations existed.

---

### Root Cause C: Nonexistent Target DOM Node in `loadCrossReferenceMatrix`
- **File**: `index.html` (Line 5676)
- **Defective Code**:
  ```javascript
  const container = document.getElementById('crossref-results-container');
  ```
- **Analysis**: The HTML markup defined `<tbody id="crossref-results-body">` inside `<table class="data-table">`, but `loadCrossReferenceMatrix()` searched for `#crossref-results-container`, failing silently without updating the view when users switched to the Cross Reference tab.

---

## 3. Verified Fix & Recovery Strategy

1. **Normalized Code Matching Function**:
   Create a resilient helper that checks both `source_part_number`/`target_part_number` and legacy aliases safely using optional chaining:
   ```javascript
   function normalizeCode(val) {
       return (val || '').toString().replace(/[\s\-_.\/]+/g, '').toUpperCase();
   }
   ```
2. **Unified Search & Matrix Rendering**:
   Update `executeCrossRefSearch()` and `loadCrossReferenceMatrix()` to safely render:
   - Match Quality Badge (`EQUIVALENT 100%`, `ALTERNATIVE 95%`, `REPLACEMENT 90%`)
   - Source Brand & Part Number
   - Target Brand & OEM Interchange
   - Vehicle Application Fitment
   - Verification Status (`VERIFIED`)
   - Empty state: `"No verified cross-reference relations found for '[query]'. Try searching another OEM or aftermarket number."`

3. **Backend Relation Resolver in `main.py`**:
   Update `get_product_detail` to compare with normalized part numbers:
   ```python
   for cr in cross_refs:
       src = normalize_part_number(cr.get("source_part_number") or cr.get("source_part"))
       tgt = normalize_part_number(cr.get("target_part_number") or cr.get("target_part"))
       if (norm_oem and norm_oem in (src, tgt)) or (norm_sku and norm_sku in (src, tgt)):
           related_cross_refs.append(cr)
   ```
