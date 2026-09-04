# Phase 11: Commercial MVP & GTM Implementation Plan

**Date**: September 3, 2026  
**Status**: Step-by-Step Implementation Blueprint  

---

## 1. Incremental Execution Steps

### Increment 11.1: Backend Commercial & Self-Service Provisioning Endpoints (`main.py` & `database.py`)
- Implement `POST /api/auth/register-trial`:
  - Validates organization & email uniqueness.
  - Automatically provisions `organizations`, `users`, `organization_members` (Role: `OWNER`), 14-day `TRIAL` subscription on selected plan, `subscription_entitlements_snapshot`, and initial `usage_records`.
  - Automatically inserts lead into `customer_leads` with `pipeline_stage = 'TRIAL'`.
- Implement `POST /api/public/leads/contact`:
  - Captures public demo/sales contact inquiries and creates lead in `customer_leads` with `pipeline_stage = 'NEW'`.
- Implement `GET /api/public/coverage-stats`:
  - Returns live platform data coverage counters (total master parts, makes, models, aftermarket brands) for dynamic landing page social proof.

### Increment 11.2: Public Marketing Landing Page UI (`index.html`)
- Add `#public-landing-view` accessible before login:
  - **Sticky Header**: Logo, Solutions, Coverage, Pricing, Live Demo, "เข้าสู่ระบบ" and "ทดลองใช้ฟรี 14 วัน" CTAs.
  - **Hero Section**: Value proposition headline, subtitle, quick CTA buttons, and interactive Live Demo search box.
  - **Social Proof & Stats Bar**: Live counters (5,000+ Parts, 8 Aftermarket Brands, 7 Car Makes, 99.8% OE Accuracy).
  - **Segment Solutions Tabs**: Interactive cards for Garages, Retailers, Insurance, and Fleet.
  - **Interactive Pricing Matrix**: Starter, Professional (Best Value), Business, Enterprise with Monthly / Annual toggle (2 Months Free badge) and 1-click checkout/trial buttons.
  - **Enterprise Lead Modal**: Contact sales form with instant CRM pipeline integration.
  - **14-Day Free Trial Modal**: 1-minute self-service company signup with instant auto-login.

### Increment 11.3: First-Time User Experience (FTUX) Onboarding Wizard
- Onboarding modal automatically triggered for newly registered trial users on their first login:
  - Step 1: Select preferred vehicle brands (Toyota, Honda, Isuzu, etc.).
  - Step 2: Try guided sample search (`04465-0K360`).
  - Step 3: Team invite or API key setup.

### Increment 11.4: In-App Commercial Conversion Enhancements
- Quota notification banners (80% / 100%) with 1-click upgrade button.
- Promo / Coupon input field (`COMMERCIAL20`, `LAUNCH50`) in self-service checkout modal.

### Increment 11.5: 20-Scenario Automated Test Suite & Full Regression
- Build `scratch/test_phase11_commercial_mvp_and_gtm.py`:
  - Self-service trial signup end-to-end flow.
  - Public demo search teaser and coverage statistics.
  - CRM lead capture from public contact form.
  - FTUX onboarding preference persistence.
  - Coupon redemption and prorated discount calculations.
  - Multi-tenant boundary isolation between new trial organizations.
- Run full system regression across all 11 phases (**120+ automated tests passing with 100% success rate**).
