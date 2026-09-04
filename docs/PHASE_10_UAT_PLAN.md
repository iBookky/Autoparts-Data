# Phase 10: User Acceptance Testing (UAT) Plan & Scenarios

**Date**: September 3, 2026  
**Status**: UAT Specification  

---

## 1. UAT Role Matrices & Test Scenarios

### 1.1 Customer Tenant Journey (`customer_owner` & `customer_staff`)
- **UAT-C01 (Search Consistency)**: Search for OEM code `04465-0K360` returns verified brake pads (TRW GDB3534UT) with score 100.
- **UAT-C02 (VIN Decoding)**: Decoding VIN `1FMCU05G15KD20101` returns Ford Escape / Explorer specs.
- **UAT-C03 (Commercial Entitlement Gate)**: Searching for locked category `ระบบช่วงล่าง` on Starter plan returns commercial upgrade prompt instead of raw error.
- **UAT-C04 (Team & Seat Governance)**: Customer Owner promotes member to Manager; system blocks demoting last Owner.
- **UAT-C05 (Self-Service Upgrade)**: Upgrades subscription from Starter to Professional with 7% VAT and itemized invoice.

### 1.2 Operations Admin Journey (`admin`)
- **UAT-A01 (Today Priority Dashboard)**: View action items (expiring trials, pending bank transfers, overdue tasks).
- **UAT-A02 (Customer 360 Operational Profile)**: Inspect tenant usage, active add-ons, and add private internal note.
- **UAT-A03 (Bank Transfer Confirmation)**: Verifies corporate bank transfer for Invoice #165 and transitions subscription to ACTIVE.

### 1.3 Specialized Staff Workspaces (`staff_*`)
- **UAT-S01 (Sales Staff)**: Move lead from `DEMO` to `TRIAL` and set next action follow-up date.
- **UAT-S02 (Data Staff)**: Review zero-result search terms and approve scraped temp part to master catalog.
- **UAT-S03 (AI Staff)**: Review `AI_MATCHED` candidate and approve as `VERIFIED` with audit record.
- **UAT-S04 (API Staff)**: Rotate customer API key with 48-hour grace period for old key.

### 1.4 System Owner Journey (`owner`)
- **UAT-O01 (Executive BI)**: Real-time MRR, ARR, ARPU, gross revenue, Thai VAT 7%, and 30-day daily trend graph.
- **UAT-O02 (Secure Export)**: Download sanitized financial report in CSV/JSON with audit logging.
