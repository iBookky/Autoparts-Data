# Customer Portal Feature Matrix

**Generated:** 2026-09-04 19:35:46

## 1. Customer Roles Definition

- **`CUSTOMER_OWNER`**: Organization Administrator. Holds commercial billing authority, team seat allocations, API key management, and full automotive search.
- **`CUSTOMER_MANAGER`**: Team Manager. Manages users, invites team members, views usage, inspects tax receipts, and executes automotive cross-referencing.
- **`CUSTOMER_STAFF`**: Day-to-day Counter Specialist. Executes OEM, SKU, VIN lookups, fitment checks, and personal bookmarks. Zero access to billing or team settings.

## 2. Feature Entitlement Table

| Customer Feature | `CUSTOMER_OWNER` | `CUSTOMER_MANAGER` | `CUSTOMER_STAFF` | Entitlement Gate | Minimum Plan Required |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Quick & Advanced Search** | ALLOWED (100%) | ALLOWED (100%) | ALLOWED (100%) | `SEARCH_QUOTA` | STARTER |
| **OEM Code Lookup** | ALLOWED (100%) | ALLOWED (100%) | ALLOWED (100%) | `SEARCH_QUOTA` | STARTER |
| **SKU / Brand Search** | ALLOWED (100%) | ALLOWED (100%) | ALLOWED (100%) | `SEARCH_QUOTA` | STARTER |
| **VIN Decoder Engine** | ALLOWED | ALLOWED | ALLOWED | `VIN_SEARCH` | PROFESSIONAL |
| **Vehicle Fitment Filters** | ALLOWED | ALLOWED | ALLOWED | `VEHICLE_SEARCH` | STARTER |
| **Cross-Reference Matrix** | ALLOWED | ALLOWED | ALLOWED | `CROSS_REFERENCE` | STARTER |
| **Saved Parts Bookmarks** | ALLOWED | ALLOWED | ALLOWED | `SAVED_PARTS` | STARTER |
| **Personal Search History** | ALLOWED | ALLOWED | ALLOWED | User Session | STARTER |
| **Usage & Quota Meter** | ALLOWED | ALLOWED | ALLOWED | Meter Record | STARTER |
| **Team Member Roster** | ALLOWED | ALLOWED | **DENIED** | `users.view` | STARTER |
| **Invite Team Members** | ALLOWED | ALLOWED | **DENIED** | `users.invite` | STARTER |
| **Update Team Roles** | ALLOWED | **DENIED** | **DENIED** | `users.update_role` | STARTER |
| **Remove Member** | ALLOWED | **DENIED** | **DENIED** | `users.remove` | STARTER |
| **Update Org Profile (Tax ID)** | ALLOWED | **DENIED** | **DENIED** | `organization.update` | STARTER |
| **Subscription Management** | ALLOWED | **DENIED** | **DENIED** | `subscription.manage` | STARTER |
| **Plan Upgrades / Add-ons** | ALLOWED | **DENIED** | **DENIED** | `subscription.manage` | STARTER |
| **Invoices & Tax Receipts** | ALLOWED | ALLOWED | **DENIED** | `subscription.view` | STARTER |
| **Developer API Keys** | ALLOWED | **DENIED** | **DENIED** | `API_ACCESS` | BUSINESS |
| **Automotive Data Export** | **PERMANENT DENY** | **PERMANENT DENY** | **PERMANENT DENY** | N/A | **PROHIBITED** |
