# Phase 11: Commercial Funnel, Pricing & Growth Loops

**Date**: September 3, 2026  
**Status**: Commercial Funnel Specification  

---

## 1. Commercial Pricing Tier Matrix

| Dimension | Starter (เริ่มต้น) | Professional (มืออาชีพ - แนะนำ) | Business (องค์กรธุรกิจ) | Enterprise (คัสตอม) |
| :--- | :---: | :---: | :---: | :---: |
| **Monthly Price** | ฿1,490 / เดือน | ฿3,990 / เดือน | ฿8,990 / เดือน | ติดต่อฝ่ายขาย |
| **Annual Price (2 mos free)** | ฿14,900 / ปี (฿1,241/ด.) | ฿39,900 / ปี (฿3,325/ด.) | ฿89,900 / ปี (฿7,491/ด.) | ติดต่อฝ่ายขาย |
| **Search Quota** | 1,000 ครั้ง / เดือน | 5,000 ครั้ง / เดือน | 20,000 ครั้ง / เดือน | ไม่จำกัด (Custom) |
| **Allowed Car Brands** | 2 ยี่ห้อ | 5 ยี่ห้อ | ทุกยี่ห้อ (ไม่จำกัด) | ทุกยี่ห้อ (ไม่จำกัด) |
| **Allowed Categories** | 2 หมวดหมู่ | 5 หมวดหมู่ | ทุกหมวดหมู่ (ไม่จำกัด) | ทุกหมวดหมู่ (ไม่จำกัด) |
| **User Seats** | 1 ผู้ใช้งาน | 3 ผู้ใช้งาน | 10 ผู้ใช้งาน | ไม่จำกัด |
| **VIN Decoder** | ❌ | ✅ (100 คัน/ด.) | ✅ (500 คัน/ด.) | ✅ ไม่จำกัด |
| **REST API Access** | ❌ | ❌ (Add-on ได้) | ✅ (10,000 calls) | ✅ Dedicated Rate Limit |
| **Data Export (CSV/XLSX)**| ❌ | ❌ (Add-on ได้) | ✅ (50 exports/ด.) | ✅ Unlimited |
| **AI Parts Intelligence**| ❌ | ✅ (รวมในแพ็กเกจ) | ✅ (รวมในแพ็กเกจ) | ✅ Priority Processing |

---

## 2. In-App Growth & Conversion Triggers

1. **Quota Threshold Alerts (80% / 100%)**:
   - Soft banner at 80% usage: *"คุณใช้โควตาค้นหาไปแล้ว 80% อัปเกรดเป็น Professional เพื่อการค้นหาต่อเนื่อง"*
   - Hard lock at 100%: 1-Click upgrade with instant activation and prorated billing.
2. **Locked Brand / Category Preview**:
   - When a user searches for an unentitled brand (e.g. `ISUZU` on a Toyota-only Starter plan), the system displays 1 blurred match with an instant *"ปลดล็อกแบรนด์ ISUZU (฿490/ด.)"* add-on CTA.
3. **Promotional Coupons**:
   - `COMMERCIAL20`: 20% discount on first 3 months.
   - `LAUNCH50`: 50% discount on annual plan checkout.
