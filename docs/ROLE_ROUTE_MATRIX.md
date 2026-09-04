# Platform Role & Route Authorization Matrix

**Generated:** 2026-09-04 19:35:46

## 1. Architectural Guardrails

1. **Zero Client Role Switcher:** Role switchers and workspace switchers are permanently removed from the client interface.
2. **Context-Driven Navigation:** Effective workspace is derived strictly from authentication context.
3. **Workspace Isolation:**
   - `SYSTEM_OWNER` → `/owner`
   - `SUPER_ADMIN` → `/super-admin`
   - `ADMIN` → `/admin`
   - `STAFF` → `/staff`
   - `CUSTOMER` (Owner, Manager, Staff) → `/app`

## 2. Role-to-Route Authorization Table

| Target Role | Tier | Dedicated Workspace | Allowed Frontend Views | Prohibited Frontend Views | Backend Route Guard | DB Role Mapping |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `SYSTEM_OWNER` | 1 | `/owner` | `#owner-view`, `#search-view`, `#crossref-view` | `#superadmin-view`, `#admin-view`, `#staff-view` | `require_owner` | `owner` |
| `SUPER_ADMIN` | 2 | `/super-admin` | `#superadmin-view`, `#admin-view`, `#search-view`, `#crossref-view` | `#owner-view` (Commercial), `#staff-view` | `require_super_admin` | `super_admin` |
| `ADMIN` | 3 | `/admin` | `#admin-view`, `#admin-queue-view`, `#admin-meta-view`, `#search-view` | `#owner-view`, `#superadmin-view` (AI Keys/DB) | `require_admin` | `admin` |
| `STAFF_SALES` | 4 | `/staff` | `#staff-view` (Pipeline), `#search-view` | `#owner-view`, `#superadmin-view`, `#admin-view` | `require_staff` | `staff_sales` |
| `STAFF_DATA` | 4 | `/staff` | `#staff-view` (Queue Review), `#search-view` | `#owner-view`, `#superadmin-view`, `#admin-view` | `require_staff` | `staff_data` |
| `STAFF_CS` | 4 | `/staff` | `#staff-view` (Accounts Health), `#search-view` | `#owner-view`, `#superadmin-view`, `#admin-view` | `require_staff` | `staff_cs` |
| `STAFF_SUPPORT` | 4 | `/staff` | `#staff-view` (Tickets/Notes), `#search-view` | `#owner-view`, `#superadmin-view`, `#admin-view` | `require_staff` | `staff_support` |
| `CUSTOMER_OWNER` | 5 | `/app` | `#search-view`, `#crossref-view`, `#favorites-view`, `#history-view`, `#subscription-view`, `#invoices-view`, `#settings-view`, `#usage-view`, `#api-view` | `/owner`, `/super-admin`, `/admin`, `/staff` | `get_user_tenant_context` | `org_owner` |
| `CUSTOMER_MANAGER` | 5 | `/app` | `#search-view`, `#crossref-view`, `#favorites-view`, `#history-view`, `#invoices-view`, `#settings-view` (Team/Profile), `#usage-view` | `/owner`, `/super-admin`, `/admin`, `/staff`, `#api-view` | `get_user_tenant_context` | `org_manager` |
| `CUSTOMER_STAFF` | 5 | `/app` | `#search-view`, `#crossref-view`, `#favorites-view`, `#history-view`, `#usage-view` | `/owner`, `/super-admin`, `/admin`, `/staff`, `#settings-view`, `#subscription-view`, `#invoices-view`, `#api-view` | `get_user_tenant_context` | `org_staff` |
