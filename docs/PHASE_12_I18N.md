# Phase 12 — Centralized Internationalization (i18n) Report

**Objective**: Complete specification of the Thai & English bilingual architecture, centralized dictionary, and language switching lifecycle.

---

## 1. Architecture Overview

1. **Centralized Dictionary (`frontend/js/i18n.js`)**:
   - Contains structured JSON keys for `th` (default) and `en`.
   - Keys cover: Navigation, Omnibar Search, Advanced Filters, Search Results, Product Detail Drawer, Cross Reference Matrix, Saved Bookmarks, Account Management, Billing History, and Toasts.
2. **DOM Binding**:
   - `data-i18n="key"`: Automatically translates inner text content.
   - `data-i18n-placeholder="key"`: Automatically translates input placeholders.
3. **Persistence**:
   - Active language saved in `localStorage.getItem('autoparts_lang') || 'th'`.
   - Header toggle button (`TH | EN`) switches language dynamically without page reload.
4. **Bilingual Label Support**:
   - High-value terms use English (Thai) format where appropriate:
     - `Search (ค้นหาอะไหล่)`
     - `Cross Reference (เทียบเบอร์)`
     - `Saved (รายการบันทึก)`
     - `Account & Plan (บัญชี & แพ็กเกจ)`

---

## 2. Customer-Friendly Terminology Mapping

| Internal ERP Jargon | Thai Customer Label | English Customer Label |
|---|---|---|
| *Entitlements* | **สิทธิประโยชน์ในแพ็กเกจ** | **Included in your plan** |
| *Usage Records* | **การใช้งานและโควตาของคุณ** | **Your usage & quota** |
| *Subscription Items* | **แพ็กเกจเสริม** | **Add-on Power Packs** |
| *Organization Management* | **ข้อมูลบริษัทและทีมงาน** | **Company & Team** |
| *Interchange Matrix* | **ศูนย์เทียบเบอร์อะไหล่ข้ามแบรนด์** | **Cross-Reference Matrix** |
