-- SQL Migration script to initialize master_parts, temp_parts, users, and meta settings tables.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('OWNER', 'SUPER_ADMIN', 'ADMIN', 'STAFF', 'CUSTOMER', 'CUSTOMER_OWNER', 'CUSTOMER_MANAGER', 'CUSTOMER_STAFF', 'SYSTEM_OWNER')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS master_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT,
    part_number TEXT,
    oem_number TEXT,
    product_name_th TEXT,
    product_name_en TEXT,
    category TEXT,
    car_brand TEXT,
    car_model TEXT,
    year_start TEXT,
    year_end TEXT,
    engine TEXT,
    fuel TEXT,
    transmission TEXT,
    description TEXT,
    cost_unit TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(brand, part_number, oem_number, car_brand, car_model)
);

CREATE TABLE IF NOT EXISTS temp_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    brand TEXT,
    part_number TEXT,
    oem_number TEXT,
    product_name_th TEXT,
    product_name_en TEXT,
    category TEXT,
    car_brand TEXT,
    car_model TEXT,
    year_start TEXT,
    year_end TEXT,
    engine TEXT,
    fuel TEXT,
    transmission TEXT,
    description TEXT,
    cost_unit TEXT,
    notes TEXT,
    source_type TEXT CHECK (source_type IN ('SCRAPE_DAILY', 'ON_DEMAND', 'EXCEL_IMPORT')),
    status TEXT CHECK (status IN ('PENDING', 'PENDING_URGENT', 'APPROVED', 'REJECTED')) DEFAULT 'PENDING',
    staff_note TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Meta dropdown tables
CREATE TABLE IF NOT EXISTS meta_aftermarket_brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS meta_car_brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS meta_car_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    car_brand TEXT NOT NULL,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS meta_car_years (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS meta_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    name_en TEXT
);

-- Predefined AI models catalog for instant 1-click switching
CREATE TABLE IF NOT EXISTS meta_ai_models (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT UNIQUE NOT NULL,
    provider TEXT NOT NULL,
    description TEXT,
    is_preset INTEGER DEFAULT 1
);

-- Agent Skills Configuration
CREATE TABLE IF NOT EXISTS agent_skills_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_key TEXT UNIQUE NOT NULL,
    skill_name TEXT NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1
);

-- AI keys and dynamic usage tracking
CREATE TABLE IF NOT EXISTS ai_keys_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT UNIQUE NOT NULL,
    api_key TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_usage_stats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    usage_date TEXT NOT NULL,
    call_count INTEGER DEFAULT 1,
    tokens_used INTEGER DEFAULT 0,
    UNIQUE(model_name, usage_date)
);

-- Index for searching and sorting
CREATE INDEX IF NOT EXISTS idx_master_search ON master_parts(part_number, oem_number, car_brand, car_model);
CREATE INDEX IF NOT EXISTS idx_temp_status ON temp_parts(status, created_at);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Seed default users:
INSERT OR IGNORE INTO users (username, password, role) VALUES 
('owner', '43a0d17178a9d26c9e0fe9a74b0b45e38d32f27aed887a008a54bf6e033bf7b9', 'SUPER_ADMIN'),
('superadmin', 'e34f92a20532a873cb3184398070b4b82a8fa29cf48572c203dc5f0fa6158231', 'SUPER_ADMIN'),
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'ADMIN'),
('staff', '10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6', 'STAFF');

-- Seed Aftermarket Brands
INSERT OR IGNORE INTO meta_aftermarket_brands (name) VALUES 
('TRW'), ('BOSCH'), ('AISIN'), ('KYB'), ('LUCAS'), ('DENSO'), ('BREMBO'), ('GSP');

-- Seed Car Brands
INSERT OR IGNORE INTO meta_car_brands (name) VALUES 
('HONDA'), ('TOYOTA'), ('ISUZU'), ('NISSAN'), ('MAZDA'), ('FORD'), ('MITSUBISHI');

-- Seed Car Models
INSERT OR IGNORE INTO meta_car_models (car_brand, name) VALUES 
('HONDA', 'Civic FB'),
('HONDA', 'Civic FC'),
('HONDA', 'Accord'),
('HONDA', 'City'),
('TOYOTA', 'Yaris'),
('TOYOTA', 'Hilux Revo'),
('TOYOTA', 'Vios'),
('TOYOTA', 'Corolla'),
('TOYOTA', 'Fortuner'),
('ISUZU', 'D-Max'),
('NISSAN', 'Navara'),
('MAZDA', 'Mazda 2'),
('FORD', 'Ranger'),
('FORD', 'Everest'),
('MITSUBISHI', 'Mirage'),
('MITSUBISHI', 'Triton');

-- Seed Car Years
INSERT OR IGNORE INTO meta_car_years (year) VALUES 
('2012'), ('2013'), ('2014'), ('2015'), ('2016'), ('2017'), ('2018'), ('2019'), ('2020'), ('2021'), ('2022'), ('2023'), ('2024'), ('2025'), ('2026');

-- Seed Categories
INSERT OR IGNORE INTO meta_categories (name, name_en) VALUES 
('ระบบเบรก', 'Brake System'),
('ระบบช่วงล่าง', 'Suspension'),
('กรองอากาศ / กรองน้ำมัน', 'Filters'),
('โช๊คอัพ', 'Shock Absorber'),
('สายพาน / ลูกรอก', 'Belts');

-- Seed Preset AI Models (Extensible in future)
INSERT OR IGNORE INTO meta_ai_models (model_name, provider, description, is_preset) VALUES 
('gemini-2.5-flash', 'Google', 'ความเร็วสูง แม่นยำ ประมวลผลรวดเร็ว (แนะนำ)', 1),
('gemini-2.5-pro', 'Google', 'ความฉลาดระดับสูงสุด การคิดวิเคราะห์เชิงลึก', 1),
('gemini-2.0-flash', 'Google', 'รุ่นเสถียร ประมวลผลแบบมัลติโมดัล', 1),
('gemini-1.5-pro', 'Google', 'บริบทขนาดใหญ่ รองรับงานเอกสารและแคตตาล็อกยาว', 1),
('gemini-1.5-flash', 'Google', 'โมเดลความเร็วสูงสำหรับงานทั่วไป', 1),
('claude-3-7-sonnet', 'Anthropic', 'โมเดลเหตุผลขั้นสูงสำหรับงานวิเคราะห์อะไหล่', 1),
('claude-3-5-sonnet', 'Anthropic', 'การประมวลผลโค้ดและข้อมูลโครงสร้างความแม่นยำสูง', 1),
('gpt-4o', 'OpenAI', 'โมเดลระดับเรือธง รอบด้าน ฉลาดรอบด้าน', 1),
('gpt-4o-mini', 'OpenAI', 'โมเดลขนาดกะทัดรัด ประหยัดและรวดเร็ว', 1),
('deepseek-chat', 'DeepSeek', 'DeepSeek-V3 ความสามารถสูงคุ้มค่า', 1),
('deepseek-reasoner', 'DeepSeek', 'DeepSeek-R1 โมเดลการคิดวิเคราะห์เชิงเหตุผล', 1);

-- Seed Agent Skills
INSERT OR IGNORE INTO agent_skills_config (skill_key, skill_name, description, is_active) VALUES 
('oem_cross_ref', 'OEM & Aftermarket Cross-Reference Specialist', 'ถอดรหัสความเทียบเคียงระหว่างรหัสแท้เดิม (OEM) และรหัสอะไหล่ทดแทนสากล (TRW, Aisin, Bosch, Brembo, Denso, KYB)', 1),
('fitment_auditor', 'Vehicle Generation & Chassis Fitment Auditor', 'ตรวจสอบรหัสตัวถัง (Chassis code), รหัสเครื่องยนต์ และปีการผลิต เพื่อป้องกันการจับคู่ผิดรุ่น 100%', 1),
('asean_market_naming', 'ASEAN / Thai Automotive Market Intelligence', 'เข้าใจชื่อทางการตลาดของรถยนต์ในประเทศไทยและภูมิภาคอาเซียน (เช่น Revo/Vigo, Altis, D-Max, Attrage)', 1),
('global_catalog_parser', 'Global Web Catalog & EPC Data Extraction', 'สกัดสเปกชิ้นส่วนจากหน้าเว็บและแคตตาล็อกระดับสากล', 1);
