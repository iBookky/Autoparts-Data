// Centralized Bilingual i18n Translation Dictionary (Thai / English)
const I18N_DICTIONARY = {
    th: {
        // Meta & Document
        "meta.title": "AutoParts Cross-Ref | แพลตฟอร์มสืบค้นและเทียบรหัสอะไหล่รถยนต์อัจฉริยะ",

        // Landing Header & Navigation
        "landing.brand.tagline": "B2B Automotive Intelligence",
        "landing.nav.home": "หน้าแรก",
        "landing.nav.solutions": "โซลูชันธุรกิจ",
        "landing.nav.coverage": "ความครอบคลุมข้อมูล",
        "landing.nav.pricing": "ราคาและแพ็กเกจ",
        "landing.nav.demo": "ทดลองค้นหาจริง",
        "landing.nav.signin": "เข้าสู่ระบบ",
        "landing.nav.trial": "ทดลองใช้ฟรี 14 วัน",

        // Landing Hero Section
        "landing.hero.pill": "แพลตฟอร์มสืบค้นและเทียบรหัสอะไหล่รถยนต์อันดับ 1 ในไทย",
        "landing.hero.title": "เทียบเบอร์อะไหล่แท้ & อะไหล่ทดแทน <br><span class=\"gradient-text-hero\">แม่นยำ ทันที ไม่พลาดทุกโอกาสการขาย</span>",
        "landing.hero.desc": "ค้นหารหัส OEM, เบอร์เทียบ Aftermarket 8 แบรนด์ชั้นนำ, ถอดรหัส VIN และตรวจสอบความเข้ากันได้ของชิ้นส่วนรถยนต์กว่า 5,000+ รายการ สำหรับอู่ซ่อมรถ ร้านอะไหล่ บริษัทประกัน และฟลีทรถยนต์",
        "landing.hero.btnTrial": "เริ่มต้นทดลองใช้ฟรี 14 วัน",
        "landing.hero.btnDemo": "ทดลองค้นหาจริง (Live Demo)",

        // Landing Demo Search
        "landing.demo.title": "ทดลองค้นหาอะไหล่สดจากระบบ Master Database",
        "landing.demo.badge": "เชื่อมต่อฐานข้อมูลสด",
        "landing.demo.placeholder": "พิมพ์รหัส เช่น 04465-0K360, GDB3534UT, หรือ Hilux, Civic...",
        "landing.demo.searchBtn": "ค้นหา",
        "landing.demo.popular": "ตัวอย่างยอดนิยม:",
        "landing.demo.loading": "กำลังโหลดผลการค้นหาตัวอย่าง...",

        // Landing Coverage Stats
        "landing.coverage.title": "ฐานข้อมูลอะไหล่รถยนต์ที่ใหญ่และแม่นยำที่สุด",
        "landing.coverage.subtitle": "อัปเดตข้อมูลมาตรฐานสากล เชื่อมโยงรหัสอะไหล่แท้ศูนย์และอะไหล่เทียบทั่วโลก",
        "landing.stat.partsTitle": "รหัสอะไหล่ Master Database",
        "landing.stat.partsDesc": "ตรวจสอบ OE Fitment ครบถ้วน",
        "landing.stat.brandsTitle": "แบรนด์ Aftermarket ชั้นนำ",
        "landing.stat.brandsDesc": "TRW, BOSCH, AISIN, KYB ฯลฯ",
        "landing.stat.makesTitle": "ค่ายรถยนต์หลักในไทย",
        "landing.stat.makesDesc": "Toyota, Honda, Isuzu, Ford ฯลฯ",
        "landing.stat.accuracyTitle": "ความแม่นยำระดับ OE Standard",
        "landing.stat.accuracyDesc": "ระบบ AI Verification 4 ขั้นตอน",

        // Landing Solutions
        "landing.solutions.badge": "Tailored Solutions",
        "landing.solutions.title": "ออกแบบมาเพื่อตอบโจทย์ 4 ธุรกิจยานยนต์",
        "landing.solutions.subtitle": "เพิ่มกำไร ลดเวลาทำงาน และแก้ปัญหาอะไหล่ผิดเบอร์สำหรับองค์กรของคุณ",
        "landing.sol.garages.title": "อู่ซ่อมรถและศูนย์บริการ (Garages & Workshops)",
        "landing.sol.garages.desc": "ออกใบเสนอราคาเร็วขึ้น 3 เท่า เทียบเบอร์แท้กับเบอร์เทียบได้ทันที เลือกระดับราคาและยี่ห้อที่ลูกค้าต้องการได้ตรงสเปก ลดปัญหาลูกค้าปฏิเสธงานซ่อม",
        "landing.sol.garages.b1": "เทียบรหัส OE เป็น Aftermarket ภายใน 3 วินาที",
        "landing.sol.garages.b2": "เช็กตำแหน่งติดตั้ง หน้า-หลัง ซ้าย-ขวา ชัดเจน",
        "landing.sol.garages.b3": "ถอดรหัส VIN รู้รุ่นปีรถตรงจุด 100%",

        "landing.sol.retailers.title": "ร้านค้าและตัวแทนจำหน่ายอะไหล่ (Parts Retailers)",
        "landing.sol.retailers.desc": "ไม่พลาดทุกโอกาสการขาย เมื่อไม่มีอะไหล่แท้ในสต็อก แนะนำเบอร์ทดแทนที่มีในร้านได้ทันที ลดสต็อกจมและเพิ่มยอดหมุนเวียนสินค้า",
        "landing.sol.retailers.b1": "จับคู่รหัสข้ามแบรนด์ (TRW ↔ BOSCH ↔ AISIN)",
        "landing.sol.retailers.b2": "ค้นหาอะไหล่และเทียบเบอร์ได้สะดวกรวดเร็ว",
        "landing.sol.retailers.b3": "เชื่อมต่อระบบ ERP ผ่าน REST API อัตโนมัติ",

        "landing.sol.insurance.title": "บริษัทประกันภัยและประเมินเคลม (Insurance & Claims)",
        "landing.sol.insurance.desc": "ตรวจสอบราคาประเมินชิ้นส่วนอะไหล่แท้และอะไหล่เทียบมาตรฐาน มั่นใจในคุณภาพอะไหล่ ควบคุมต้นทุนค่าสินไหมได้อย่างเป็นธรรมและโปร่งใส",
        "landing.sol.insurance.b1": "ฐานข้อมูลมาตรฐาน OE Reference กลาง",
        "landing.sol.insurance.b2": "ระบบตรวจสอบความสัมพันธ์ชิ้นส่วนที่ผ่านการรับรอง",
        "landing.sol.insurance.b3": "รายงานตรวจสอบย้อนหลังและ Audit Trail",

        "landing.sol.fleet.title": "ผู้บริหารฟลีทรถยนต์ (Fleet Operations)",
        "landing.sol.fleet.desc": "บริหารต้นทุนการบำรุงรักษาเชิงป้องกัน (PM) ของฝูงบินรถยนต์ วางแผนจัดซื้ออะไหล่สิ้นเปลืองล็อตใหญ่ด้วยราคาที่ดีที่สุด",
        "landing.sol.fleet.b1": "ค้นหาอะไหล่ตามรุ่นปีรถยนต์ในฟลีทแบบกลุ่ม",
        "landing.sol.fleet.b2": "ลดต้นทุนอะไหล่สิ้นเปลืองลง 20-35%",
        "landing.sol.fleet.b3": "ทีม Support ดูแลประสานงานเฉพาะทาง",

        // Landing Pricing Section
        "landing.pricing.badge": "Pricing & Plans",
        "landing.pricing.title": "แพ็กเกจราคาที่คุ้มค่า คืนทุนตั้งแต่เดือนแรก",
        "landing.pricing.subtitle": "เลือกแพ็กเกจที่เหมาะกับขนาดธุรกิจของคุณ หรือทดลองใช้งานฟรี 14 วันก่อนตัดสินใจ",
        "landing.cycle.monthly": "ชำระรายเดือน",
        "landing.cycle.yearly": "ชำระรายปี",
        "landing.cycle.save20": "ประหยัด 20% (ฟรี 2 เดือน)",

        // Plan Cards
        "plan.popularRibbon": "⭐ แนะนำสำหรับธุรกิจ (POPULAR)",
        "plan.btn.trial": "ทดลองใช้ฟรี 14 วัน",
        "plan.btn.trialPro": "ทดลองใช้ฟรี 14 วัน (แนะนำ)",
        "plan.btn.contactSales": "ติดต่อเจ้าหน้าที่",
        "plan.contactSalesPrice": "ติดต่อฝ่ายขาย",

        "plan.starter.badge": "STARTER",
        "plan.starter.title": "สำหรับอู่ขนาดเล็ก",
        "plan.starter.desc": "เริ่มต้นเทียบเบอร์อะไหล่แท้-เทียบ",
        "plan.starter.f1": "ค้นหา <strong>1,000 ครั้ง</strong> / เดือน",
        "plan.starter.f2": "เลือกได้ <strong>2 ยี่ห้อรถ</strong>",
        "plan.starter.f3": "เลือกได้ <strong>2 หมวดหมู่</strong>",
        "plan.starter.f4": "<strong>1 บัญชีผู้ใช้</strong>",
        "plan.starter.f5": "ระบบบันทึกอะไหล่ (Saved Parts)",
        "plan.starter.f6": "ค้นหาและเทียบเบอร์อะไหล่แท้-เทียบ",

        "plan.pro.badge": "PROFESSIONAL",
        "plan.pro.title": "สำหรับอู่มาตรฐาน & ร้านอะไหล่",
        "plan.pro.desc": "ครบครันสำหรับงานซ่อมและการขายทุกวัน",
        "plan.pro.f1": "ค้นหา <strong>5,000 ครั้ง</strong> / เดือน",
        "plan.pro.f2": "เลือกได้ <strong>5 ยี่ห้อรถหลัก</strong>",
        "plan.pro.f3": "ครบทั้ง <strong>5 หมวดหมู่อะไหล่</strong>",
        "plan.pro.f4": "<strong>3 บัญชีผู้ใช้</strong> (ทีมงาน)",
        "plan.pro.f5": "ถอดรหัส VIN <strong>100 คัน/ด.</strong>",
        "plan.pro.f6": "<strong>AI Parts Search</strong> รวมในแพ็กเกจ",

        "plan.biz.badge": "BUSINESS",
        "plan.biz.title": "สำหรับตัวแทนจำหน่าย & ฟลีท",
        "plan.biz.desc": "ครอบคลุมทุกแบรนด์ พร้อมเชื่อมต่อระบบ",
        "plan.biz.f1": "ค้นหา <strong>20,000 ครั้ง</strong> / เดือน",
        "plan.biz.f2": "<strong>ทุกยี่ห้อรถยนต์</strong> (ไม่จำกัด)",
        "plan.biz.f3": "<strong>ทุกหมวดหมู่สินค้า</strong>",
        "plan.biz.f4": "<strong>10 บัญชีผู้ใช้</strong>",
        "plan.biz.f5": "REST API <strong>10,000 calls</strong>",
        "plan.biz.f6": "ระบบค้นหาแบบกลุ่ม & บุ๊กมาร์ก",

        "plan.ent.badge": "ENTERPRISE",
        "plan.ent.title": "สำหรับบริษัทประกัน & คอร์ปอเรท",
        "plan.ent.desc": "ปรับแต่งตามขนาดองค์กร พร้อม SLA 99.9%",
        "plan.ent.f1": "ค้นหา <strong>ไม่จำกัด (Unlimited)</strong>",
        "plan.ent.f2": "ผู้ใช้งาน <strong>ไม่จำกัด (Unlimited)</strong>",
        "plan.ent.f3": "Dedicated High-speed API",
        "plan.ent.f4": "Custom ERP / DMS Integration",
        "plan.ent.f5": "ออกใบกำกับภาษีเต็มรูปแบบ",
        "plan.ent.f6": "ผู้จัดการบัญชีดูแลส่วนตัว (Account Manager)",

        // Footer
        "footer.tagline": "ระบบสืบค้นและเทียบเคียงเบอร์อะไหล่ยานยนต์มาตรฐานระดับสากล",
        "footer.rights": "© 2026 AutoParts Intelligence Co., Ltd. สงวนลิขสิทธิ์ทุกประการ",
        "footer.home": "หน้าแรก",
        "footer.pricing": "ราคา",
        "footer.sales": "ติดต่อฝ่ายขาย",
        "footer.signin": "เข้าสู่ระบบ",

        // Auth & Modals
        "auth.title": "เข้าสู่ระบบแพลตฟอร์ม",
        "auth.subtitle": "ระบบสืบค้นและจับคู่รหัสอะไหล่รถยนต์ระดับองค์กร",
        "auth.username": "ชื่อผู้ใช้งาน (Username / Email)",
        "auth.password": "รหัสผ่าน (Password)",
        "auth.submit": "ลงชื่อเข้าใช้งานแพลตฟอร์ม",
        "auth.backLanding": "กลับสู่หน้าหลัก (Landing Page)",
        "auth.noAccount": "ยังไม่มีบัญชีใช้งาน?",
        "auth.startTrial": "สมัครทดลองใช้ฟรี 14 วัน",

        // App Shell & Navigation
        "app.name": "AutoParts",
        "app.tagline": "Cross-Ref SaaS",
        "nav.mainMenu": "Main Menu",
        "nav.search": "Search (ค้นหา)",
        "nav.crossref": "Cross Reference (เทียบเบอร์)",
        "nav.favorites": "Saved & Bookmarks (บันทึก)",
        "nav.account": "Account & Plan (บัญชี & แพ็กเกจ)",
        "nav.logout": "ออก",
        "nav.owner": "ศูนย์บัญชาการธุรกิจ (Command Center)",
        "nav.superadmin": "Platform & Data Center (ศูนย์ข้อมูลและระบบ)",
        "nav.admin": "ศูนย์ปฏิบัติการ (Operator Hub)",
        "nav.staff": "พื้นที่ทำงานเจ้าหน้าที่ (Staff Workspace)",
        "header.searches": "Searches:",
        "header.landingPage": "หน้าแรก",

        // View Titles (for top breadcrumb #current-view-title)
        "viewTitle.search-view": "ค้นหาอะไหล่รถยนต์ (Parts Search Dashboard)",
        "viewTitle.crossref-view": "เทียบเบอร์อะไหล่ OEM ↔ Aftermarket (Cross Reference)",
        "viewTitle.favorites-view": "รายการอะไหล่ที่บันทึกไว้ (Saved Parts & Bookmarks)",
        "viewTitle.subscription-view": "บัญชีและแพ็กเกจการใช้งาน (Account & Plan)",
        "viewTitle.coverage-view": "ความครอบคลุมของฐานข้อมูล (Data Coverage Matrix)",
        "viewTitle.history-view": "ประวัติการค้นหา (Search Activity History)",
        "viewTitle.api-view": "REST API & ระบบเชื่อมต่อสำหรับนักพัฒนา (Developer Hub)",
        "viewTitle.usage-view": "ปริมาณการใช้งานและโควตา (Usage & Limits)",
        "viewTitle.invoices-view": "ประวัติการชำระเงินและใบเสร็จ (Invoices & Billing)",
        "viewTitle.settings-view": "การตั้งค่าองค์กร (Organization Settings)",
        "viewTitle.owner-view": "ศูนย์บัญชาการผู้บริหารระบบ (Platform Owner Command Center)",
        "viewTitle.superadmin-view": "Platform & Data Center (ศูนย์ควบคุมข้อมูลและระบบ)",
        "viewTitle.admin-view": "ศูนย์ปฏิบัติการดูแลลูกค้า (Customer Operations Hub)",
        "viewTitle.staff-view": "พื้นที่จัดการงานเจ้าหน้าที่ (Staff Task Workspace)",

        // Search Dashboard
        "search.heroTitle": "ค้นหาอะไหล่ที่ถูกต้อง รวดเร็วและแม่นยำ",
        "search.heroSubtitle": "สืบค้นข้ามเบอร์แท้ OEM, รหัสสินค้า Aftermarket, เลขตัวถัง VIN 17 หลัก หรือระบุรุ่นรถยนต์",
        "search.placeholder": "พิมพ์เบอร์ OEM, รหัสสินค้า SKU, เลข VIN 17 หลัก หรือชื่ออะไหล่/รุ่นรถ...",
        "search.searchBtn": "ค้นหา",
        "search.quickFilters": "ตัวกรองด่วน:",
        "search.vinSearch": "ค้นหาด้วย VIN",
        "search.vehicleSearch": "ค้นหาตามรุ่นรถ",
        "search.oemSku": "เบอร์แท้ / SKU",
        "search.crossref": "เทียบเบอร์อะไหล่",
        "search.advFilters": "ตัวกรองค้นหาขั้นสูง",
        "search.advTitle": "กำหนดพารามิเตอร์การค้นหาแบบละเอียด",
        "search.resultsTitle": "ผลการค้นหารายการอะไหล่",
        "search.colStatus": "สถานะ",
        "search.colProductBrand": "แบรนด์สินค้า",
        "search.colSku": "รหัสสินค้า (SKU)",
        "search.colOem": "เบอร์แท้ (OEM Code)",
        "search.colProductName": "ชื่อรายการอะไหล่",
        "search.colCategory": "หมวดหมู่",
        "search.colVehicle": "รุ่นรถที่รองรับ",
        "search.colYear": "ปีรถยนต์",
        "search.colActions": "จัดการ",
        "search.viewSpecs": "ดูรายละเอียด",
        "search.noResults": "ไม่พบรายการอะไหล่ที่ตรงกับเงื่อนไข ระบุข้อมูลด้านบนเพื่อเริ่มค้นหา",

        // Advanced Search Form
        "adv.vinLabel": "เลขตัวถัง VIN 17 หลัก",
        "adv.vinPlaceholder": "เช่น 1FMCU9G97EUE...",
        "adv.carBrandLabel": "ยี่ห้อรถยนต์ (Make)",
        "adv.carModelYearLabel": "รุ่นและปีรถยนต์ (Model & Year)",
        "adv.categoryLabel": "หมวดหมู่อะไหล่",
        "adv.oemLabel": "เบอร์แท้ OEM",
        "adv.partNameLabel": "ชื่ออะไหล่ / คำค้นหา",
        "adv.aftermarketBrandLabel": "แบรนด์ผู้ผลิตอะไหล่",
        "adv.aftermarketPartLabel": "รหัสสินค้า Aftermarket SKU",
        "adv.clearBtn": "ล้างค่าค้นหา",
        "adv.submitBtn": "ค้นหาละเอียด",

        // Cross Reference Subsystem
        "crossref.heroTitle": "ศูนย์เทียบเบอร์อะไหล่ข้ามแบรนด์ (OEM ↔ Aftermarket)",
        "crossref.heroSubtitle": "ค้นหาและจับคู่เบอร์เทียบเคียงตรงรุ่น ทั้งเบอร์แท้ศูนย์และอะไหล่ทดแทนแบรนด์ชั้นนำ",
        "crossref.placeholder": "พิมพ์เบอร์แท้ OEM หรือรหัสสินค้า Aftermarket (เช่น 04465-0K360, GDB3534)...",
        "crossref.searchBtn": "เทียบเบอร์อะไหล่",
        "crossref.tableTitle": "ตารางความเชื่อมโยงความเทียบเคียงอะไหล่",
        "crossref.colMatch": "ความแม่นยำ",
        "crossref.colBrand": "แบรนด์",
        "crossref.colPartNum": "รหัสสินค้า",
        "crossref.colOemInterchange": "เบอร์แท้เทียบเคียง",
        "crossref.colProductName": "ชื่ออะไหล่",
        "crossref.colVehicle": "รุ่นรถที่รองรับ",
        "crossref.colAction": "จัดการ",
        "crossref.emptyMsg": "พิมพ์เบอร์แท้ OEM หรือรหัสสินค้าเพื่อดูผังเทียบเบอร์",

        // Product Detail Drawer
        "drawer.title": "รายละเอียดทางเทคนิคของอะไหล่",
        "drawer.saveBtn": "บันทึกรายการ",
        "drawer.copyBtn": "คัดลอกเบอร์",
        "drawer.graphBtn": "ดูแผนผังเทียบเบอร์",
        "drawer.aiBtn": "AI เทียบเบอร์",
        "drawer.tabOverview": "ภาพรวม (Overview)",
        "drawer.tabOem": "เบอร์แท้เทียบเคียง",
        "drawer.tabCross": "รายการเทียบเบอร์",
        "drawer.tabFitment": "รุ่นรถที่รองรับ",
        "drawer.tabQuality": "การรับรองมาตรฐาน",
        "drawer.noCrossRefs": "ไม่พบรายการเทียบเบอร์ที่ลงทะเบียนไว้",

        // Saved & History
        "fav.title": "รายการอะไหล่ที่บันทึกไว้ (Saved Parts)",
        "fav.subtitle": "เข้าถึงอะไหล่ที่คุณบันทึกไว้บ่อยๆ ได้อย่างรวดเร็ว",
        "fav.emptyMsg": "ยังไม่มีรายการอะไหล่ที่บันทึกไว้ กดไอคอน ⭐ บนรายการเพื่อบันทึก",

        "account.title": "บัญชี & แพ็กเกจการใช้งาน (Account & Plan)",
        "account.subtitle": "จัดการข้อมูลองค์กร แพ็กเกจสมาชิก โควตาการใช้งาน และทีมงานของคุณ",
        "account.planIncluded": "สิทธิประโยชน์ในแพ็กเกจของคุณ (Included in your plan)",
        "account.yourUsage": "การใช้งานและโควตาของคุณ (Your usage & quota)",
        "account.addons": "แพ็กเกจเสริม (Add-on Power Packs)",
        "account.team": "ข้อมูลบริษัทและทีมงาน (Company & Team)",
        "account.billingHistory": "ประวัติการชำระเงิน (Billing History)",
        "account.language": "ภาษาการใช้งาน (Language Preference)",

        // Theme & Preferences
        "theme.toggle": "สลับโหมดสว่าง / โหมดมืด (Day / Night)",
        "theme.light": "โหมดกลางวัน (สว่าง)",
        "theme.dark": "โหมดกลางคืน (มืด)",

        // Tax Invoice & Official Receipt
        "invoice.modalTitle": "ใบกำกับภาษี / ใบเสร็จรับเงิน (Official VAT Tax Invoice)",
        "invoice.seller": "ผู้ออกเอกสาร (Seller / Issuer)",
        "invoice.buyer": "ข้อมูลผู้ซื้อ / องค์กร (Customer / Buyer)",
        "invoice.invNo": "เลขที่เอกสาร",
        "invoice.date": "วันที่ออกเอกสาร",
        "invoice.period": "รอบระยะเวลาการใช้งาน",
        "invoice.subtotal": "มูลค่าก่อนภาษี (Subtotal)",
        "invoice.vat": "ภาษีมูลค่าเพิ่ม 7% (VAT 7%)",
        "invoice.grandTotal": "ยอดชำระสุทธิ (Grand Total)",
        "invoice.printBtn": "พิมพ์ / บันทึกเป็น PDF",
        "invoice.closeBtn": "ปิดหน้าต่าง"
    },
    en: {
        // Meta & Document
        "meta.title": "AutoParts Cross-Ref | Automotive Parts Data & Cross Reference SaaS Platform",

        // Landing Header & Navigation
        "landing.brand.tagline": "B2B Automotive Intelligence",
        "landing.nav.home": "Home",
        "landing.nav.solutions": "Solutions",
        "landing.nav.coverage": "Data Coverage",
        "landing.nav.pricing": "Pricing & Plans",
        "landing.nav.demo": "Live Demo",
        "landing.nav.signin": "Sign In",
        "landing.nav.trial": "Start Free Trial",

        // Landing Hero Section
        "landing.hero.pill": "#1 Automotive Parts Data & Cross-Reference Platform",
        "landing.hero.title": "Match OEM & Aftermarket Parts Instantly <br><span class=\"gradient-text-hero\">Accurate. Instant. Never Miss a Sale.</span>",
        "landing.hero.desc": "Search verified OEM codes, 8 leading aftermarket brands, 17-digit VIN decoding, and vehicle fitment across 5,000+ parts for repair shops, parts retailers, insurance, and fleet operations.",
        "landing.hero.btnTrial": "Start 14-Day Free Trial",
        "landing.hero.btnDemo": "Explore Live Demo",

        // Landing Demo Search
        "landing.demo.title": "Live Catalog Search against Master Database",
        "landing.demo.badge": "Live Connected",
        "landing.demo.placeholder": "Search OEM code, SKU, or model e.g. 04465-0K360, GDB3534UT, Hilux...",
        "landing.demo.searchBtn": "Search",
        "landing.demo.popular": "Popular Examples:",
        "landing.demo.loading": "Loading catalog preview...",

        // Landing Coverage Stats
        "landing.coverage.title": "The Most Accurate Automotive Data Matrix",
        "landing.coverage.subtitle": "Standardized OE specifications linking genuine parts and verified aftermarket cross-references.",
        "landing.stat.partsTitle": "Master Database Parts",
        "landing.stat.partsDesc": "Full OE Fitment Verification",
        "landing.stat.brandsTitle": "Leading Aftermarket Brands",
        "landing.stat.brandsDesc": "TRW, BOSCH, AISIN, KYB, etc.",
        "landing.stat.makesTitle": "Major Vehicle Makes",
        "landing.stat.makesDesc": "Toyota, Honda, Isuzu, Ford, etc.",
        "landing.stat.accuracyTitle": "OE Standard Accuracy",
        "landing.stat.accuracyDesc": "4-Stage AI Data Validation",

        // Landing Solutions
        "landing.solutions.badge": "Tailored Solutions",
        "landing.solutions.title": "Engineered for 4 Automotive Segments",
        "landing.solutions.subtitle": "Boost margins, eliminate incorrect parts ordering, and speed up turnaround times.",
        "landing.sol.garages.title": "Garages & Service Centers",
        "landing.sol.garages.desc": "Quote 3x faster by matching genuine OEM to trusted aftermarket alternatives in seconds. Offer customers price tiers that match their budget.",
        "landing.sol.garages.b1": "OEM to Aftermarket cross-reference in 3s",
        "landing.sol.garages.b2": "Clear Front/Rear & Left/Right fitment",
        "landing.sol.garages.b3": "17-Digit VIN decoding for precise specs",

        "landing.sol.retailers.title": "Parts Retailers & Distributors",
        "landing.sol.retailers.desc": "Never miss a sale. When genuine OEM parts are out of stock, instantly suggest high-quality in-stock equivalents to keep inventory moving.",
        "landing.sol.retailers.b1": "Cross-brand interchange (TRW ↔ BOSCH ↔ AISIN)",
        "landing.sol.retailers.b2": "Fast parts search & relation mapping",
        "landing.sol.retailers.b3": "ERP & POS sync via REST API",

        "landing.sol.insurance.title": "Insurance & Claims Adjusters",
        "landing.sol.insurance.desc": "Verify genuine OEM replacement standards vs certified aftermarket parts. Ensure repair quality while controlling claims payout fairly and transparently.",
        "landing.sol.insurance.b1": "Centralized OEM reference catalog",
        "landing.sol.insurance.b2": "Certified fitment & quality assurance",
        "landing.sol.insurance.b3": "Audit trail & claims history tracking",

        "landing.sol.fleet.title": "Fleet Managers & Logistics",
        "landing.sol.fleet.desc": "Control preventive maintenance (PM) costs across your vehicle fleet. Plan volume procurement with guaranteed fitment and competitive pricing.",
        "landing.sol.fleet.b1": "Batch model & year parts lookup",
        "landing.sol.fleet.b2": "Reduce wear-and-tear costs by 20-35%",
        "landing.sol.fleet.b3": "Dedicated technical support",

        // Landing Pricing Section
        "landing.pricing.badge": "Pricing & Plans",
        "landing.pricing.title": "Transparent & High-ROI Pricing Plans",
        "landing.pricing.subtitle": "Choose the plan that fits your business scale, or start with a 14-day free trial.",
        "landing.cycle.monthly": "Monthly Billing",
        "landing.cycle.yearly": "Yearly Billing",
        "landing.cycle.save20": "Save 20% (2 Months Free)",

        // Plan Cards
        "plan.popularRibbon": "⭐ RECOMMENDED FOR BUSINESS",
        "plan.btn.trial": "Start 14-Day Free Trial",
        "plan.btn.trialPro": "Start Free Trial (Recommended)",
        "plan.btn.contactSales": "Contact Sales",
        "plan.contactSalesPrice": "Contact Sales",

        "plan.starter.badge": "STARTER",
        "plan.starter.title": "For Small Garages",
        "plan.starter.desc": "Entry-level OEM & aftermarket cross-referencing",
        "plan.starter.f1": "<strong>1,000 Searches</strong> / month",
        "plan.starter.f2": "Choose <strong>2 Vehicle Brands</strong>",
        "plan.starter.f3": "Choose <strong>2 Categories</strong>",
        "plan.starter.f4": "<strong>1 User Account</strong>",
        "plan.starter.f5": "Saved Parts & Bookmarks",
        "plan.starter.f6": "OEM & Aftermarket Matching",

        "plan.pro.badge": "PROFESSIONAL",
        "plan.pro.title": "For Workshops & Retailers",
        "plan.pro.desc": "Complete suite for daily repairs and parts sales",
        "plan.pro.f1": "<strong>5,000 Searches</strong> / month",
        "plan.pro.f2": "Choose <strong>5 Vehicle Brands</strong>",
        "plan.pro.f3": "All <strong>5 Parts Categories</strong>",
        "plan.pro.f4": "<strong>3 User Accounts</strong> (Team)",
        "plan.pro.f5": "VIN Decoding <strong>100 cars/mo</strong>",
        "plan.pro.f6": "<strong>AI Parts Search</strong> Included",

        "plan.biz.badge": "BUSINESS",
        "plan.biz.title": "For Distributors & Fleets",
        "plan.biz.desc": "Full brand coverage and system integration",
        "plan.biz.f1": "<strong>20,000 Searches</strong> / month",
        "plan.biz.f2": "<strong>All Vehicle Brands</strong> (Unlimited)",
        "plan.biz.f3": "<strong>All Parts Categories</strong>",
        "plan.biz.f4": "<strong>10 User Accounts</strong>",
        "plan.biz.f5": "REST API <strong>10,000 calls</strong>",
        "plan.biz.f6": "Batch Search & Team Collaboration",

        "plan.ent.badge": "ENTERPRISE",
        "plan.ent.title": "For Insurance & Corporate",
        "plan.ent.desc": "Customized for enterprise scale with 99.9% SLA",
        "plan.ent.f1": "<strong>Unlimited Searches</strong>",
        "plan.ent.f2": "<strong>Unlimited Users</strong>",
        "plan.ent.f3": "Dedicated High-Speed API",
        "plan.ent.f4": "Custom ERP / DMS Integration",
        "plan.ent.f5": "Full Tax Invoice & Corporate Billing",
        "plan.ent.f6": "Dedicated Account Manager",

        // Footer
        "footer.tagline": "World-class automotive parts data and cross-reference platform.",
        "footer.rights": "© 2026 AutoParts Intelligence Co., Ltd. All Rights Reserved.",
        "footer.home": "Home",
        "footer.pricing": "Pricing",
        "footer.sales": "Contact Sales",
        "footer.signin": "Sign In",

        // Auth & Modals
        "auth.title": "Platform Sign In",
        "auth.subtitle": "Enterprise automotive parts catalog & interchange platform",
        "auth.username": "Username / Email",
        "auth.password": "Password",
        "auth.submit": "Sign In to Platform",
        "auth.backLanding": "Back to Home Page",
        "auth.noAccount": "Don't have an account?",
        "auth.startTrial": "Start 14-Day Free Trial",

        // App Shell & Navigation
        "app.name": "AutoParts",
        "app.tagline": "Cross-Ref SaaS",
        "nav.mainMenu": "Main Menu",
        "nav.search": "Search Parts",
        "nav.crossref": "Cross Reference",
        "nav.favorites": "Saved Parts",
        "nav.account": "Account & Plan",
        "nav.logout": "Log Out",
        "nav.owner": "Owner Command Center",
        "nav.superadmin": "Platform & Data Center",
        "nav.admin": "Operations Admin Hub",
        "nav.staff": "Staff Task Workspace",
        "header.searches": "Searches:",
        "header.landingPage": "Home",

        // View Titles (for top breadcrumb #current-view-title)
        "viewTitle.search-view": "Parts Search Dashboard",
        "viewTitle.crossref-view": "OEM ↔ Aftermarket Cross Reference",
        "viewTitle.favorites-view": "Saved Favorites & Bookmarks",
        "viewTitle.subscription-view": "Account & Subscription Management",
        "viewTitle.coverage-view": "Data Coverage Matrix",
        "viewTitle.history-view": "Search Audit History",
        "viewTitle.api-view": "REST API & Developer Hub",
        "viewTitle.usage-view": "Usage & Limits Dashboard",
        "viewTitle.invoices-view": "Invoices & Billing Receipts",
        "viewTitle.settings-view": "Organization Settings",
        "viewTitle.owner-view": "Platform Owner Command Center",
        "viewTitle.superadmin-view": "Platform & Data Control Center",
        "viewTitle.admin-view": "Customer Operations Hub",
        "viewTitle.staff-view": "Staff Task Workspace",

        // Search Dashboard
        "search.heroTitle": "Find the right part faster.",
        "search.heroSubtitle": "Search across verified OEM numbers, aftermarket SKUs, VIN or vehicle specifications.",
        "search.placeholder": "Search OEM code, SKU, 17-digit VIN, part name or vehicle model...",
        "search.searchBtn": "Search",
        "search.quickFilters": "QUICK FILTERS:",
        "search.vinSearch": "VIN Search",
        "search.vehicleSearch": "Vehicle Search",
        "search.oemSku": "OEM / SKU",
        "search.crossref": "Cross Reference",
        "search.advFilters": "Advanced Filters",
        "search.advTitle": "Structured Automotive Search Parameters",
        "search.resultsTitle": "Automotive Catalog Search Results",
        "search.colStatus": "Status",
        "search.colProductBrand": "Brand",
        "search.colSku": "SKU Part#",
        "search.colOem": "OEM Code",
        "search.colProductName": "Product Name",
        "search.colCategory": "Category",
        "search.colVehicle": "Vehicle Application",
        "search.colYear": "Year Fitment",
        "search.colActions": "Actions",
        "search.viewSpecs": "View Specs",
        "search.noResults": "No matching automotive parts found. Enter search criteria above.",

        // Advanced Search Form
        "adv.vinLabel": "17-Digit VIN Number",
        "adv.vinPlaceholder": "e.g. 1FMCU9G97EUE...",
        "adv.carBrandLabel": "Vehicle Brand (Make)",
        "adv.carModelYearLabel": "Vehicle Model & Year",
        "adv.categoryLabel": "Category System",
        "adv.oemLabel": "Primary OEM Code",
        "adv.partNameLabel": "Part Name / Keyword",
        "adv.aftermarketBrandLabel": "Aftermarket Brand",
        "adv.aftermarketPartLabel": "Aftermarket SKU",
        "adv.clearBtn": "Reset",
        "adv.submitBtn": "Filter",

        // Cross Reference Subsystem
        "crossref.heroTitle": "Automotive Cross-Reference & Interchange Matrix",
        "crossref.heroSubtitle": "Resolve verified equivalencies between original equipment manufacturers (OEM) and leading aftermarket brands.",
        "crossref.placeholder": "Search OEM code or aftermarket SKU (e.g. 04465-0K360, GDB3534)...",
        "crossref.searchBtn": "Cross Reference",
        "crossref.tableTitle": "Relational Interchange & Cross-Reference Matrix",
        "crossref.colMatch": "Match Quality",
        "crossref.colBrand": "Brand",
        "crossref.colPartNum": "Part Number",
        "crossref.colOemInterchange": "OEM Interchange",
        "crossref.colProductName": "Product Name",
        "crossref.colVehicle": "Vehicle Application",
        "crossref.colAction": "Action",
        "crossref.emptyMsg": "Enter an OEM or Aftermarket part number to view cross-reference mapping.",

        // Product Detail Drawer
        "drawer.title": "Technical Part Specifications",
        "drawer.saveBtn": "Save Part",
        "drawer.copyBtn": "Copy Part#",
        "drawer.graphBtn": "View Relation Graph",
        "drawer.aiBtn": "AI Match",
        "drawer.tabOverview": "Overview",
        "drawer.tabOem": "OEM References",
        "drawer.tabCross": "Cross Ref",
        "drawer.tabFitment": "Vehicle Fitment",
        "drawer.tabQuality": "Data Quality",
        "drawer.noCrossRefs": "No verified cross references found.",

        // Saved & History
        "fav.title": "Saved Parts & Bookmarks",
        "fav.subtitle": "Quickly access your frequently referenced automotive parts and interchanges.",
        "fav.emptyMsg": "No saved parts bookmarked yet. Click the ⭐ icon on any part to save it.",

        // Account & Subscription
        "account.title": "Account & Subscription Management",
        "account.subtitle": "Manage company profile, subscription plan, monthly quota, and team members.",
        "account.planIncluded": "Included in your plan",
        "account.yourUsage": "Your usage & quota",
        "account.addons": "Add-on Power Packs",
        "account.team": "Company & Team",
        "account.billingHistory": "Billing History",
        "account.language": "Language Preference",

        // Theme & Preferences
        "theme.toggle": "Toggle Day / Night Mode",
        "theme.light": "Light Mode (Day)",
        "theme.dark": "Dark Mode (Night)",

        // Tax Invoice & Official Receipt
        "invoice.modalTitle": "Official VAT Tax Invoice & Receipt",
        "invoice.seller": "Issuer (Seller)",
        "invoice.buyer": "Customer (Buyer)",
        "invoice.invNo": "Tax Invoice #",
        "invoice.date": "Issue Date",
        "invoice.period": "Billing Period",
        "invoice.subtotal": "Subtotal (Before VAT)",
        "invoice.vat": "Value Added Tax (VAT 7%)",
        "invoice.grandTotal": "Grand Total (THB)",
        "invoice.printBtn": "Print / Download PDF",
        "invoice.closeBtn": "Close"
    }
};

let currentLanguage = localStorage.getItem('autoparts_lang') || 'th';
let currentTheme = localStorage.getItem('autoparts_theme') || 'dark';

function initAppTheme() {
    currentTheme = localStorage.getItem('autoparts_theme') || 'dark';
    applyTheme(currentTheme);
}

function applyTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('autoparts_theme', theme);

    // Update icons: sun for light mode, moon for dark mode
    const isLight = theme === 'light';
    const iconClass = isLight ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
    const titleText = isLight ? t('theme.dark', 'Switch to Dark Mode') : t('theme.light', 'Switch to Light Mode');

    document.querySelectorAll('#theme-icon, #landing-theme-icon, .theme-toggle-icon').forEach(icon => {
        icon.className = iconClass;
        if (icon.parentElement) {
            icon.parentElement.title = titleText;
        }
    });

    const sidebarThemeLabel = document.getElementById('sidebar-theme-label');
    if (sidebarThemeLabel) {
        sidebarThemeLabel.textContent = isLight ? t('theme.light', 'Light Mode') : t('theme.dark', 'Dark Mode');
    }
}

function toggleAppTheme() {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
}

function setAppLanguage(lang) {
    if (!I18N_DICTIONARY[lang]) return;
    currentLanguage = lang;
    localStorage.setItem('autoparts_lang', lang);

    const dict = I18N_DICTIONARY[lang];

    // Update document title
    if (dict["meta.title"]) {
        document.title = dict["meta.title"];
    }

    // Update text elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (dict[key]) {
            if (dict[key].includes('<') && dict[key].includes('>')) {
                el.innerHTML = dict[key];
            } else {
                el.textContent = dict[key];
            }
        }
    });

    // Update placeholders with data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (dict[key]) {
            el.placeholder = dict[key];
        }
    });

    // Update HTML lang attribute
    document.documentElement.lang = lang;

    // Update active lang toggle pills (both in landing and in app header)
    document.querySelectorAll('.lang-btn-th, #lang-btn-th').forEach(btn => {
        btn.classList.toggle('active', lang === 'th');
    });
    document.querySelectorAll('.lang-btn-en, #lang-btn-en').forEach(btn => {
        btn.classList.toggle('active', lang === 'en');
    });

    // Update breadcrumb view title
    updateCurrentViewTitle();

    // Re-apply theme tooltip and labels in current language
    applyTheme(currentTheme);

    // Re-render landing billing cycle prices in the chosen language
    if (typeof setLandingBillingCycle === 'function' && typeof landingBillingCycle !== 'undefined') {
        setLandingBillingCycle(landingBillingCycle);
    }
}

function updateCurrentViewTitle() {
    const activeSection = document.querySelector('.view-section.active');
    const viewId = activeSection ? activeSection.id : 'search-view';
    const viewTitleKey = `viewTitle.${viewId}`;
    const titleEl = document.getElementById('current-view-title');
    if (titleEl) {
        titleEl.textContent = t(viewTitleKey, 'AutoParts Platform');
    }
}

function t(key, fallback = '') {
    const dict = I18N_DICTIONARY[currentLanguage] || I18N_DICTIONARY['th'];
    return dict[key] || fallback || key;
}

// Auto-initialize language and theme on DOM load
document.addEventListener('DOMContentLoaded', () => {
    initAppTheme();
    setAppLanguage(currentLanguage);
});
