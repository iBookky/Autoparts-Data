# Phase 12 — Role Boundary & Authorization Architecture

**Objective**: Strict documentation of platform role boundaries, workspace authorization, and privilege escalation prevention.

---

## 1. 5-Tier Role & Workspace Architecture

| Role | Authorized Workspace | Scope & Permitted Operations | Role Switcher in UI |
|---|---|---|---|
| **CUSTOMER_OWNER** | `/app` (Customer Portal) | Search parts, view cross-references, save bookmarks, manage company subscription, billing, team seats. | **NONE (Removed)** |
| **CUSTOMER_MEMBER** | `/app` (Customer Portal) | Search parts, view cross-references, save bookmarks. | **NONE (Removed)** |
| **STAFF** | `/staff` (Staff Workspace) | Catalog ingestion review, part verification, task queue operations. | **NONE (Removed)** |
| **ADMIN** | `/admin` (Operations Hub) | Operations management, tenant support, part approvals, backup exports. | **NONE (Removed)** |
| **SUPER_ADMIN** | `/super-admin` (Platform Hub) | Database operations, global system health, platform metrics. | **NONE (Removed)** |
| **OWNER** | `/owner` (Command Center) | Executive financial BI, revenue analytics, MRR/ARR, churn intelligence. | **NONE (Removed)** |

---

## 2. Server-Side Enforcement Rules

1. **Zero Client-Side Role Determination**: User permissions are determined exclusively by server-side database lookup via session token and role context.
2. **Direct Route Protection**:
   - `GET /api/owner/*` $\rightarrow$ Enforced via `Depends(require_operator_or_admin)`
   - `GET /api/admin/*` $\rightarrow$ Enforced via `Depends(require_admin)`
   - `GET /api/staff/*` $\rightarrow$ Enforced via `Depends(require_staff)`
3. **Privilege Escalation Blocked**:
   - Registration hardcodes `users.role = 'STAFF'` and `org_role = 'OWNER'` (tenant level only).
   - Member role assignments are strictly constrained to `('OWNER', 'ADMIN', 'MEMBER')` within the tenant's own `org_id`.
   - Modifying header `x-user-role` on non-operator requests is validated against user tenant session in database.
