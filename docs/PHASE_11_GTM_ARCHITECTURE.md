# Phase 11: Commercial MVP & Go-To-Market (GTM) Architecture

**Date**: September 3, 2026  
**Status**: Commercial Architecture Specification  

---

## 1. Executive Summary

Phase 11 transforms the AutoParts Cross-Ref platform from a "technically ready SaaS" into a **"commercially sellable, high-converting B2B SaaS platform"**.

In strict compliance with the architecture rules:
- **Zero modification to core automotive search, billing state machine, or data tables.**
- Sits seamlessly on top of Phase 1–10 services (`EntitlementService`, `SubscriptionStateMachine`, `PaymentGateway`, `OwnerAnalyticsService`).

---

## 2. Commercial Funnel & Conversion Architecture

```
                                [PUBLIC TRAFFIC]
                                       │
                                       ▼
                       [Public Marketing Landing Page]
                       • Live Interactive Demo Search
                       • Segment Solutions (Garages, Retail, Insurance, Fleet)
                       • Interactive Pricing Calculator (Monthly/Annual)
                       • Social Proof & Live Coverage Counters
                                       │
                     ┌─────────────────┴─────────────────┐
                     ▼                                   ▼
        [14-Day Free Trial Signup]               [Enterprise Contact Sales]
        • Auto-provision Organization            • Auto-create CRM Lead
        • Auto-create User & Owner Role          • Pipeline Stage: 'NEW' / 'QUALIFIED'
        • Auto-provision 14-day TRIAL sub        • Instant Staff Notification
        • Instant Auto-Login                             │
                     │                                   ▼
                     ▼                         [Sales Staff Workflow]
           [FTUX Onboarding Wizard]            • Follow-up call / Proposal
           1. Select Core Car Brands           • Custom Pricing / Add-ons
           2. Guided Sample Cross-Ref Search
           3. Invite Team / Generate API Key
                     │
                     ▼
           [Customer Portal Active]
           • Quota Metering & Alerts
           • 1-Click Self-Service Upgrades
           • Promo / Coupon Redemptions
```

---

## 3. Four Core B2B Target Personas

| Target Persona | Key Pain Point | Value Proposition | Targeted Plan |
| :--- | :--- | :--- | :--- |
| **Auto Repair Garages (อู่ซ่อมรถ)** | Slow quoting, inaccurate parts ordering, customer wait time | Instant OE-to-Aftermarket interchange across 8 brands in 5 seconds | Starter / Professional |
| **Parts Retailers & Wholesalers (ร้านอะไหล่)** | Dead stock, lost sales due to missing cross-references | Complete catalog coverage, VIN decoding, multi-brand equivalents | Professional / Business |
| **Insurance Assessors (บริษัทประกัน/เคลม)** | Inconsistent repair cost estimates, disputed parts pricing | Standardized OE code mapping, verified aftermarket alternatives | Business / Enterprise |
| **Fleet Operators (ฟลีทรถยนต์)** | High maintenance costs, fragmented parts procurement | Bulk part lookup, CSV export, API integration for ERP/Fleet software | Business / Enterprise |

---

## 4. Self-Service Trial & Provisioning Pipeline (`register_trial_tenant`)

```python
async def register_trial_tenant(data: TrialSignupRequest) -> Dict[str, Any]:
    # 1. Validate email uniqueness
    # 2. Create organization (e.g. "Siam Auto Service Co., Ltd.")
    # 3. Create user with salted password & assign org_role = "OWNER"
    # 4. Provision 14-day trial subscription on selected plan (e.g. 'professional')
    # 5. Seed monthly usage record (5,000 searches, 100 VIN lookups)
    # 6. Capture CRM lead in pipeline with stage = 'TRIAL'
    # 7. Generate session authentication token
```
