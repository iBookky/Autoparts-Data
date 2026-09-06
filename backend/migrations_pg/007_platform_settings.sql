-- 007_platform_settings.sql (PostgreSQL)
-- Platform settings, Homepage CMS, SEO, Owner Business Profile, and Invoice Customization

ALTER TABLE meta_categories ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '';

CREATE TABLE IF NOT EXISTS platform_settings (
    id INT PRIMARY KEY DEFAULT 1,
    -- Branding & Homepage CMS
    site_title VARCHAR(255) DEFAULT 'AutoParts Cross-Ref - B2B Automotive Intelligence',
    logo_url TEXT DEFAULT '',
    favicon_url TEXT DEFAULT '',
    hero_badge VARCHAR(255) DEFAULT 'แพลตฟอร์มสืบค้นและเทียบรหัสอะไหล่รถยนต์อันดับ 1 ในไทย',
    hero_title VARCHAR(255) DEFAULT 'เทียบเบอร์อะไหล่แท้ & อะไหล่ทดแทน',
    hero_subtitle TEXT DEFAULT 'ค้นหาข้ามแบรนด์ แม่นยำ รวดเร็ว พร้อมเชื่อมต่อระบบ AI และสต็อกสินค้าอัจฉริยะ',
    hero_bg_style VARCHAR(50) DEFAULT 'gradient', -- gradient, solid, dark, custom
    hero_bg_gradient TEXT DEFAULT 'radial-gradient(circle at 50% 0%, rgba(37, 99, 235, 0.15) 0%, rgba(15, 23, 42, 0.95) 75%)',
    hero_bg_color VARCHAR(50) DEFAULT '#0B132B',
    
    -- SEO Metadata
    seo_meta_title VARCHAR(255) DEFAULT 'AutoParts Cross-Ref | ระบบเทียบเบอร์อะไหล่และค้นหาด้วย VIN',
    seo_meta_description TEXT DEFAULT 'แพลตฟอร์มค้นหาและเทียบเคียงรหัสอะไหล่แท้และอะไหล่ทดแทน (OEM & Aftermarket) ที่ใหญ่ที่สุดในประเทศไทย รองรับการค้นหาด้วยเลขตัวถัง VIN 17 หลัก',
    seo_meta_keywords TEXT DEFAULT 'อะไหล่รถยนต์, เทียบเบอร์อะไหล่, OEM parts, Aftermarket, VIN decoder, เบอร์อะไหล่, รถยนต์',
    seo_og_image_url TEXT DEFAULT '',
    
    -- Contact & Social
    contact_email VARCHAR(255) DEFAULT 'contact@autoparts-crossref.com',
    contact_phone VARCHAR(50) DEFAULT '02-123-4567',
    contact_line VARCHAR(100) DEFAULT '@autoparts',
    footer_copyright VARCHAR(255) DEFAULT '© 2026 AutoParts Cross-Ref. All rights reserved.',
    
    -- Platform Owner & Tax Profile
    owner_company_name_th VARCHAR(255) DEFAULT 'บริษัท ออโต้เซนทริค ดิจิทัล โซลูชันส์ จำกัด',
    owner_company_name_en VARCHAR(255) DEFAULT 'AUTOCENTRIC DIGITAL SOLUTIONS CO., LTD.',
    owner_tax_id VARCHAR(50) DEFAULT '0105566099881',
    owner_branch_name VARCHAR(100) DEFAULT 'สำนักงานใหญ่ (Head Office)',
    owner_address_th TEXT DEFAULT '888/99 อาคารสยามทาวเวอร์ ชั้น 18 ถนนสุขุมวิท แขวงคลองเตย เขตคลองเตย กรุงเทพมหานคร 10110',
    owner_address_en TEXT DEFAULT '888/99 Siam Tower 18th Fl., Sukhumvit Rd., Khlong Toei, Bangkok 10110 Thailand',
    owner_phone VARCHAR(50) DEFAULT '02-123-4567',
    owner_email VARCHAR(255) DEFAULT 'billing@autoparts-crossref.com',
    owner_website VARCHAR(255) DEFAULT 'https://parts.autocentric.net',
    owner_logo_url TEXT DEFAULT '',
    owner_signature_url TEXT DEFAULT '',
    owner_stamp_url TEXT DEFAULT '',
    owner_bank_name VARCHAR(255) DEFAULT 'ธนาคารกสิกรไทย (KBANK)',
    owner_bank_account_name VARCHAR(255) DEFAULT 'บจก. ออโต้เซนทริค ดิจิทัล โซลูชันส์',
    owner_bank_account_number VARCHAR(100) DEFAULT '098-7-65432-1',
    owner_promptpay_id VARCHAR(50) DEFAULT '0105566099881',
    
    -- Invoice & Tax Configuration
    invoice_prefix VARCHAR(50) DEFAULT 'INV-',
    tax_invoice_prefix VARCHAR(50) DEFAULT 'TAX-',
    receipt_prefix VARCHAR(50) DEFAULT 'REC-',
    invoice_due_days INT DEFAULT 7,
    vat_percentage DECIMAL(5,2) DEFAULT 7.0,
    vat_included SMALLINT DEFAULT 0, -- 0 = excluded, 1 = included
    wht_percentage DECIMAL(5,2) DEFAULT 3.0,
    invoice_footer_notes TEXT DEFAULT 'เอกสารนี้ออกโดยระบบอิเล็กทรอนิกส์อัตโนมัติและถือเป็นหลักฐานการชำระเงินที่ถูกต้องตามกฎหมาย',
    invoice_terms_conditions TEXT DEFAULT 'กรุณาชำระเงินภายในระยะเวลาที่กำหนด หากเกินกำหนดระบบจะระงับการเข้าถึงบริการชั่วคราว',
    invoice_theme_color VARCHAR(50) DEFAULT '#2563EB',
    
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO platform_settings (id) VALUES (1) ON CONFLICT (id) DO NOTHING;
