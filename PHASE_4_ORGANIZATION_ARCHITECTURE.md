# Phase 4 Architecture: Organization, Customer Users, Roles & Permissions

This document specifies the technical architecture for the multi-tenant **Organization, Customer Users, Roles, Scopes, and Authorization** engine within the **AutoParts Cross-Ref SaaS Platform**.

---

## 1. Domain Separation: Platform Roles vs. Customer Roles

The platform enforces strict separation between platform-level operators and customer-side organization accounts:

```
┌─────────────────────────────────────────────────────────────┐
│                 PLATFORM ROLE DOMAIN                        │
│  (System SaaS Provider Operations & Infrastructure)        │
├─────────────────┬─────────────────┬─────────────────────────┤
│ SYSTEM_OWNER    │ Tier 1          │ /owner                  │
│ SUPER_ADMIN     │ Tier 2          │ /super-admin            │
│ ADMIN           │ Tier 3          │ /admin                  │
│ STAFF           │ Tier 4          │ /staff                  │
└─────────────────┴─────────────────┴─────────────────────────┘

                              ▲
                              │ STRICT RBAC BOUNDARY (No cross-domain privilege bleed)
                              ▼

┌─────────────────────────────────────────────────────────────┐
│                 CUSTOMER ROLE DOMAIN                        │
│  (Business Tenant Workspace & Automotive Parts Users)       │
├─────────────────┬─────────────────┬─────────────────────────┤
│ ORG_OWNER       │ Tier 5 (Owner)  │ /app                    │
│ ORG_MANAGER     │ Tier 5 (Mgr)    │ /app                    │
│ ORG_STAFF       │ Tier 5 (Staff)  │ /app                    │
└─────────────────┴─────────────────┴─────────────────────────┘
```

> [!IMPORTANT]
> A customer user (`ORG_OWNER`, `ORG_MANAGER`, or `ORG_STAFF`) can never receive platform permissions or access `/owner`, `/super-admin`, `/admin`, or `/staff` routes.

---

## 2. Multi-Tenant Relational Data Model

All customer-owned entities are strictly scoped by `organization_id`:

```
                           ┌───────────────────────────┐
                           │       organizations       │
                           │ ───────────────────────── │
                           │ id (PK)                   │
                           │ name, legal_name, tax_id  │
                           │ business_type, email      │
                           │ phone, address, website   │
                           │ contact_person, plan_tier │
                           └─────────────┬─────────────┘
                                         │
        ┌───────────────────┬────────────┴────────────┬───────────────────┐
        │                   │                         │                   │
        ▼                   ▼                         ▼                   ▼
┌──────────────┐    ┌──────────────┐          ┌──────────────┐    ┌──────────────┐
│subscriptions │    │ entitlements │          │ usage_records│    │organization_ │
│ (Plan, MRR)  │    │(Brand/Cat OK)│          │(Quota Meters)│    │ invitations  │
└──────────────┘    └──────────────┘          └──────────────┘    └──────────────┘
        ▲                                                                 │
        │                                                                 │
        └───────────────────────────┐                                     │
                                    │                                     ▼
┌──────────────┐    ┌───────────────┴──────────┐                  ┌──────────────┐
│    users     │───▶│   organization_members   │◀─────────────────│organization_ │
│ (Auth & ID)  │    │ ──────────────────────── │                  │  audit_logs  │
└──────────────┘    │ user_id, org_id          │                  └──────────────┘
                    │ org_role (OWNER/MGR/STF) │
                    │ status (ACTIVE/SUSPENDED)│
                    └──────────────────────────┘
```

---

## 3. The 7-Step Authorization Evaluation Pipeline

Every incoming request is evaluated through the sequential pipeline:

```
[Request] ──▶ [1. Authentication] (Verify username/token)
                 │
                 ▼
              [2. Membership Check] (Active in organization_members? status != SUSPENDED)
                 │
                 ▼
              [3. Granular Permission Check] (Has 'search.use' / 'users.invite'?)
                 │
                 ▼
              [4. Scope Evaluation] (OWN vs. ORGANIZATION vs. GLOBAL)
                 │
                 ▼
              [5. Subscription Status] (Subscription ACTIVE or TRIALING?)
                 │
                 ▼
              [6. Entitlement Whitelist] (Brand & Category included in plan?)
                 │
                 ▼
              [7. Quota Consumption] (searches_used < searches_quota?)
                 │
                 ▼
              [EXECUTE OPERATION]
```

---

## 4. Key Security Protections Implemented

1. **Last Owner Protection**:
   - An organization cannot downgrade, suspend, or remove its final remaining `OWNER`. At least one active Owner must exist at all times.
2. **Privilege Escalation Guard**:
   - Customer Staff and Managers cannot alter roles, suspend accounts, or assign platform roles (`SUPER_ADMIN`, `ADMIN`).
3. **Cross-Tenant Boundary Isolation**:
   - All organization queries (`/api/saas/organization`, `/members`, `/invitations`, `/audit`, `/favorites`, `/history`) strictly derive `org_id` from authenticated server context, preventing IDOR (Insecure Direct Object Reference) vulnerabilities.
4. **Instant Access Revocation on Suspension**:
   - Suspended or disabled members immediately receive `{ "locked": true, "reason": "MEMBER_SUSPENDED" }` across all parts search, VIN decoding, and export endpoints.
5. **Auditing of Sensitive Actions**:
   - All profile updates, user invitations, role changes, status modifications, and member removals are immutably logged to `organization_audit_logs`.
