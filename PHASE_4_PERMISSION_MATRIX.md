# Phase 4 Customer Role & Permission Matrix

This document details the database-driven permission matrix and scope definitions across all Customer Organization Roles in the **AutoParts Cross-Ref SaaS Platform**.

---

## 1. Customer Roles Definition

| Role ID | Role Name | Tier | Portal | Summary Description |
| :--- | :--- | :---: | :---: | :--- |
| `org_owner` | **Organization Owner** | Tier 5 (Lead) | `/app` | Full control over team members, subscription billing, API keys, and corporate profile. |
| `org_manager` | **Organization Manager** | Tier 5 (Operator)| `/app` | Operational management, team viewing, inviting members, usage analytics, and parts search. |
| `org_staff` | **Organization Staff** | Tier 5 (Standard)| `/app` | Automotive parts search, VIN decoding, vehicle fitment, cross-references, and personal bookmarks. |

---

## 2. Granular Permission Matrix

| Permission ID | Module | Description | Scope | `org_owner` | `org_manager` | `org_staff` |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `organization.view` | ORGANIZATION | View corporate profile & tax details | ORGANIZATION | ✅ | ✅ | ❌ |
| `organization.update` | ORGANIZATION | Update legal name, address, tax ID | ORGANIZATION | ✅ | ❌ | ❌ |
| `users.view` | USERS | View organization member list | ORGANIZATION | ✅ | ✅ | ❌ |
| `users.invite` | USERS | Invite new members into team | ORGANIZATION | ✅ | ✅ | ❌ |
| `users.update_role` | USERS | Change roles of team members | ORGANIZATION | ✅ | ❌ | ❌ |
| `users.suspend` | USERS | Suspend or reactivate members | ORGANIZATION | ✅ | ❌ | ❌ |
| `users.remove` | USERS | Remove members from organization | ORGANIZATION | ✅ | ❌ | ❌ |
| `search.use` | SEARCH | Execute OEM, SKU & keyword search | ORGANIZATION | ✅ | ✅ | ✅ |
| `search.vin` | SEARCH | Universal VIN decoding engine | ORGANIZATION | ✅ | ✅ | ✅ |
| `search.vehicle` | SEARCH | Search by vehicle make, model, year | ORGANIZATION | ✅ | ✅ | ✅ |
| `search.cross_reference`| SEARCH | Access typed cross-reference relations | ORGANIZATION | ✅ | ✅ | ✅ |
| `parts.view` | PARTS | View full technical part specifications| ORGANIZATION | ✅ | ✅ | ✅ |
| `parts.save` | PARTS | Save parts to tenant bookmarks | OWN / ORG | ✅ | ✅ | ✅ |
| `subscription.view` | BILLING | View subscription status & invoices | ORGANIZATION | ✅ | ✅ | ❌ |
| `subscription.manage` | BILLING | Upgrade plans & purchase add-ons | ORGANIZATION | ✅ | ❌ | ❌ |
| `usage.view` | BILLING | View search quotas & credit meters | ORGANIZATION | ✅ | ✅ | ❌ |
| `api.view` | API | View active REST API credentials | ORGANIZATION | ✅ | ✅ | ❌ |
| `api.manage` | API | Generate & revoke REST API keys | ORGANIZATION | ✅ | ❌ | ❌ |
| `export.use` | EXPORT | Export parts catalog data to CSV | ORGANIZATION | ✅ | ✅ | ❌ |
| `audit.view` | AUDIT | View organization activity audit trail | ORGANIZATION | ✅ | ❌ | ❌ |

---

## 3. Scope Hierarchy

* **`OWN`**: Action applies strictly to resources owned by the individual authenticated user (e.g., personal favorites).
* **`ORGANIZATION`**: Action applies to all resources shared across the customer's organization tenant (e.g., shared search quota, team members).
* **`GLOBAL`**: Action applies across the entire multi-tenant platform (reserved exclusively for Platform System Owners and Admins).
