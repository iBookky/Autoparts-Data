# Phase 12 — Demonstration & User Flow Test Guide

**Objective**: Step-by-step walkthrough script for evaluating the simplified UX, recovered Cross-Reference engine, and data protection controls on the live application.

---

## 1. User Journey 1: Customer Instant Search (The 30-Second Rule)

1. Navigate to `http://localhost:8000/`.
2. Observe the clean, focused customer workspace with the prominent **Omni Search Bar**.
3. **Step 1 — Search OEM Code**:
   - Type `04465-0K360` into the search box and press `Enter`.
   - Results instantly load showing **Toyota Hilux Revo Brake Pads** with green `VERIFIED` status badge.
4. **Step 2 — Open Product Detail Specs**:
   - Click `View Specs` on the search result row.
   - The Product Detail Drawer slides out.
   - Switch to the **Cross Ref** tab: Notice the relation count badge `Cross Ref (4)` accurately lists **TRW**, **BOSCH**, **AISIN**, and **BREMBO** aftermarket alternatives.
   - Click `Pivot / Compare` on the TRW row to view the comparison immediately.

---

## 2. User Journey 2: OEM ↔ Aftermarket Cross-Reference Lookup

1. Click **Cross Reference (เทียบเบอร์)** in the left sidebar navigation.
2. Notice the clean relation matrix table loaded automatically.
3. In the input box, enter `GDB3534UT` (TRW Aftermarket Brake Pad SKU).
4. Click `Cross Reference` or press `Enter`:
   - System instantly returns the bidirectional match linking `GDB3534UT` $\leftrightarrow$ Toyota OEM `04465-0K360` with **100% Equivalent Match Quality**.
5. Test a non-existent part number (e.g. `XYZ-999-NOT-FOUND`):
   - System displays a clean, polite empty state:
     `"No verified cross-reference relationships found in catalog for 'XYZ-999-NOT-FOUND'."` (Zero 500 errors).

---

## 3. User Journey 3: Automotive Data Protection & Anti-Exfiltration Verification

1. In the search results toolbar, notice that the "Export CSV" button has been removed from customer view.
2. Attempting to execute an unauthorized bulk export via API:
   - Requesting `POST /api/saas/export` with a customer role returns HTTP `403 Forbidden` with the security message:
     `"Forbidden: Automotive catalog data export is disabled for customer accounts. Please use the search interface to look up individual parts."`
3. Broad queries (e.g. searching all Toyota parts) are strictly capped at `50 items`, preventing automated bulk database dumping.

---

## 4. User Journey 4: Simplified 4-Tab Navigation Experience

1. **Tab 1: Search (ค้นหา)** — Dominant search bar with progressive disclosure for advanced filters.
2. **Tab 2: Cross Reference (เทียบเบอร์)** — Rapid interchange lookup and comparison matrix.
3. **Tab 3: Saved & Bookmarks (บันทึก)** — Direct access to bookmarked parts and recent searches.
4. **Tab 4: Account & Plan (บัญชี & แพ็กเกจ)** — Organization subscription status, usage meter, and tier upgrades.
