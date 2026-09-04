# Phase 7 Implementation Blueprint: Admin & Staff Operations Center

**Date**: September 3, 2026  
**Status**: Step-by-Step Blueprint  

---

## 1. Step-by-Step Implementation Increments

### Increment 7.1: Database Schema Migration (`007_admin_and_staff_operations.sql`)
- Create `support_tickets` table with category, priority, status, and SLA tracking.
- Create `staff_tasks` table with assignment, priority, due date, status, and entity relations.
- Create `commercial_proposals` table linked to `BillingCalculator` and status lifecycle.
- Create `internal_notes` table for strictly private internal operator notes.
- Add operational indexes and seed baseline support tickets, tasks, and proposals.

### Increment 7.2: Centralized Operational Services
- Build `AdminOperationsService` in `backend/services/admin_operations_service.py`:
  - `get_today_dashboard()`: Aggregates daily operational priorities (leads, expiring trials, due renewals, failed payments, open tickets, overdue tasks).
  - `get_customer_operations_list()`: Filterable, paginated customer organizations.
  - `get_customer_360_operational()`: Enhanced Customer 360 with internal notes, staff assignments, and entitlement locks.
  - `manage_trials()`: Trial extensions with mandatory reason audit logging.
  - `manage_proposals()`: Proposal generation from `BillingCalculator` with status tracking.
  - `manage_support_tickets()`: Ticket lifecycle and SLA escalation.
  - `manage_staff_tasks()`: Task assignment, priority, status changes, and filter queries.
  - `manage_internal_notes()`: Private notes authoring and retrieval.

### Increment 7.3: REST API Layer in `main.py`
- Expose `/api/admin/*` endpoints protected with `require_admin`.
- Expose `/api/staff/*` endpoints with granular sub-role permission checking.
- Audit all sensitive operational changes via `log_commercial_audit` and `log_audit_action`.

### Increment 7.4: Admin Customer Operations Center UI (`index.html`)
- Upgrade `#admin-view` into the **Customer Operations Center**:
  - Top "Today's Priorities" operational metrics ribbon.
  - 10 Operational sub-tabs: *Dashboard*, *Customers*, *Leads*, *Trials*, *Subscriptions*, *Renewals*, *Billing*, *Support*, *Staff Tasks*, *Reports*.
  - Modal drawers for Customer 360, Create Task, Create Proposal, Create Ticket, and Add Internal Note.

### Increment 7.5: Specialized Staff Workspaces (`index.html`)
- Upgrade `#staff-view` with dynamic role detection and tailored tab navigation:
  - *Sales Staff* workspace
  - *Customer Success Staff* workspace
  - *Billing Staff* workspace
  - *Support Staff* workspace
  - *Data Staff* workspace (with zero-result query review)
  - *AI Staff* workspace (with review queue)
  - *API Staff* workspace (with secret rotation)

### Increment 7.6: Automated Test Suite & Regression Verification
- Build `scratch/test_phase7_admin_and_staff_operations.py` covering 18 operational scenarios.
- Run full regression across all 7 phases target: **100+ tests passing with 100% success rate**.

---

## 2. Documentation Deliverables
- [`docs/PHASE_7_AUDIT.md`](file:///Users/ibookky/Autoparts/docs/PHASE_7_AUDIT.md)
- [`docs/PHASE_7_ARCHITECTURE.md`](file:///Users/ibookky/Autoparts/docs/PHASE_7_ARCHITECTURE.md)
- [`docs/PHASE_7_PERMISSION_MATRIX.md`](file:///Users/ibookky/Autoparts/docs/PHASE_7_PERMISSION_MATRIX.md)
- [`docs/PHASE_7_IMPLEMENTATION_PLAN.md`](file:///Users/ibookky/Autoparts/docs/PHASE_7_IMPLEMENTATION_PLAN.md)
- [`docs/PHASE_7_IMPLEMENTATION_REPORT.md`](file:///Users/ibookky/Autoparts/docs/PHASE_7_IMPLEMENTATION_REPORT.md) (post-implementation)
