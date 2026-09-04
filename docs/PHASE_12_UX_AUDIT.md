# Phase 12 — User Experience Simplification Audit

**Core Philosophy**: "A user should understand how to use the system within 30 seconds."  
The customer's primary job is **FIND THE RIGHT PART**. The customer portal must eliminate administrative clutter and prioritize **Search → Results → Product Detail → Cross Reference**.

---

## 1. Current State vs Target Simplified State

```
[CURRENT CLUTTERED SIDEBAR - 11 ITEMS]
├── Platform
│   ├── Search
│   ├── Data Coverage
│   ├── Cross Reference
│   ├── Favorites
│   └── Search History
├── Developer & Usage
│   ├── API & Docs
│   └── Usage & Limits
└── Organization
    ├── Subscription
    ├── Team & Roles
    ├── Invoices
    └── Settings

                ⬇️ SIMPLIFIED WORKSPACE ⬇️

[PHASE 12 SIMPLIFIED CUSTOMER NAVIGATION - 4 CLEAR TABS]
├── 🔍 Search (Home)      -> Single dominant search bar + quick category chips
├── 🔀 Cross Reference    -> Direct OEM ↔ Aftermarket comparison
├── ⭐ Saved              -> Unified Bookmarks & Search History
└── 👤 Account            -> Simple Organization profile & subscription badge
```

---

## 2. Customer Home Experience (30-Second Rule)

### Design Elements:
1. **Single Dominant Omnibar**:
   - Centered prominently with placeholder: `"Search OEM Code, SKU, 17-digit VIN, or part name..."`
   - Automatically detects query type:
     - 17 alphanumeric chars $\rightarrow$ VIN Decoding
     - Standard dash pattern (e.g. `04465-0K360`) $\rightarrow$ OEM Search
     - Aftermarket alphanumeric (e.g. `GDB3534UT`) $\rightarrow$ SKU Cross-Reference
     - Text (e.g. `Brake pad Hilux`) $\rightarrow$ Vehicle Fitment Search
2. **Progressive Disclosure**:
   - Default: Clean, instant single-input search.
   - Optional: Small toggle `"Advanced Search (Filters)"` that expands Brand / Model / Year / Category dropdowns only when requested.
3. **High-Value Search Cards**:
   - Clean card layout highlighting:
     - **Part Number & Brand**
     - **OEM Interchange**
     - **Vehicle Compatibility**
     - **Verification Status (`VERIFIED`)**
     - **Cross-Reference Quick Badge**
4. **Product Detail Drawer**:
   - Visual Specs tab, OE Interchange tab, and Cross-Reference tab with 1-click comparison.
