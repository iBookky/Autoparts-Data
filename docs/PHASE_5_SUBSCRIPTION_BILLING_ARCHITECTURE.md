# Phase 5: Commercial Subscription, Plans, Add-ons & Billing Architecture

## 1. Commercial Architecture Overview
The commercial layer is strictly **configuration-driven** and **versioned**, decoupling code from commercial product definitions.

```
CUSTOMER COMPANY
       ↓
ORGANIZATION TENANT
       ↓
SUBSCRIPTION (ACTIVE, TRIAL, PAST_DUE, GRACE_PERIOD, SUSPENDED, CANCELLED, EXPIRED)
       ↓
PLAN VERSION (Monthly / Yearly, Quotas, User Seats, Brand/Category Limits)
       ↓
ATTACHED COMMERCIAL ADD-ONS (+Searches, +Seats, API Pack, AI Power Pack, Export Pack)
       ↓
COUPONS & PROMO CODES (Percentage / Fixed discount with expiration & tenant guards)
       ↓
TAX ENGINE (Configurable 7% VAT)
       ↓
ITEMIZED INVOICES & IDEMPOTENT PAYMENT GATEWAY
       ↓
EFFECTIVE ENTITLEMENT SNAPSHOT
       ↓
REAL-TIME SEARCH & PARTS ACCESS ENFORCEMENT
```

---

## 2. Database Schema (Migration `005_subscription_billing_engine.sql`)

### 2.1 `plan_versions`
- `id`: Primary Key
- `plan_id`: Foreign Key referencing `plans(id)` (`starter`, `professional`, `business`, `enterprise`)
- `version_number`: Integer (e.g. `1`, `2`)
- `billing_interval`: `MONTHLY` | `YEARLY`
- `base_price`: Price in THB
- `currency`: Default `'THB'`
- `monthly_search_quota`: Integer quota (-1 = unlimited)
- `max_users`: User seat limit (-1 = unlimited)
- `max_brands`: Brand limit (-1 = unlimited)
- `max_categories`: Category limit (-1 = unlimited)
- `is_current_version`: Boolean flag (1 = active version for new signups)
- `status`: `ACTIVE` | `DEPRECATED` | `DRAFT`

### 2.2 `plan_features` & `plan_entitlements`
- Feature registry for `SEARCH`, `VIN_SEARCH`, `VEHICLE_SEARCH`, `CROSS_REFERENCE`, `API`, `EXPORT`, `AI`, `SAVED_PARTS`.
- Explicit category/brand whitelist mapping per plan version.

### 2.3 `add_ons` & `add_on_plan_compatibility`
- Standalone commercial add-ons (`extra_searches_5k`, `extra_searches_20k`, `extra_users_5`, `extra_users_10`, `api_access_pack`, `ai_power_pack`, `export_pack`).
- Plan compatibility matrix (`INCLUDED`, `AVAILABLE`, `NOT_AVAILABLE`).

### 2.4 `subscription_items` & `subscription_entitlements_snapshot`
- Itemized breakdown of base plan and attached add-ons per organization subscription.
- Point-in-time frozen snapshot of effective entitlements taken during each upgrade or renewal.

### 2.5 `coupons` & `coupon_redemptions`
- Percentage (`PERCENT`) and Fixed amount (`FIXED`) discount engine.
- Validation checks for validity dates, usage limit, minimum purchase subtotal, and single redemption per tenant.

### 2.6 `invoice_items` & `commercial_audit_logs`
- Itemized lines (`PLAN`, `ADD_ON`, `DISCOUNT`, `PRORATION_CREDIT`) with quantity and unit prices.
- Immutable commercial audit trail logging every price calculation, upgrade, state transition, and payment verification.

---

## 3. Calculation & Proration Flow (`BillingCalculator`)

```
1. Base Price     = PlanVersion.base_price(interval)
2. Add-ons Total  = SUM(AddOn.price(interval))
3. Subtotal       = Base Price + Add-ons Total
4. Coupon Disc    = Min(Subtotal, CalculatedDiscount(Subtotal, Coupon))
5. Net Subtotal   = Subtotal - Coupon Disc
6. Proration      = (NewSubtotal * DaysRemaining/TotalDays) - (OldSubtotal * DaysRemaining/TotalDays)
7. Taxable Base   = Prorated Net Subtotal (if upgrade midway) ELSE Net Subtotal
8. VAT 7%         = Round(Taxable Base * 0.07)
9. Total Payable  = Taxable Base + VAT 7%
```

---

## 4. Payment Gateway Abstraction & Idempotency
- **Supported Methods**: Credit/Debit Cards, PromptPay QR, Corporate Bank Transfer.
- **Idempotency Guard**: All charges accept an `idempotency_key`. Replayed charges or duplicate webhooks return the existing transaction record without duplicate billing or invoice generation.
- **Corporate Bank Transfer**: Generates official `OPEN` VAT invoice; Platform Admin verifies proof reference and marks invoice `PAID`.
