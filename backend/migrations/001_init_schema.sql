-- SQL Migration script to initialize master_parts, temp_parts, users, and meta settings tables.

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('SUPER_ADMIN', 'ADMIN', 'STAFF')),
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
    UNIQUE(model_name, usage_date)
);

-- Index for searching and sorting
CREATE INDEX IF NOT EXISTS idx_master_search ON master_parts(part_number, oem_number, car_brand, car_model);
CREATE INDEX IF NOT EXISTS idx_temp_status ON temp_parts(status, created_at);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Seed default users:
-- superadmin / superadmin123 (SHA256: e34f92a20532a873cb3184398070b4b82a8fa29cf48572c203dc5f0fa6158231)
-- admin / admin123 (SHA256: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9)
-- staff / staff123 (SHA256: 10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6)
INSERT OR IGNORE INTO users (username, password, role) VALUES 
('superadmin', 'e34f92a20532a873cb3184398070b4b82a8fa29cf48572c203dc5f0fa6158231', 'SUPER_ADMIN'),
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'ADMIN'),
('staff', '10176e7b7b24d317acfcf8d2064cfd2f24e154f7b5a96603077d5ef813d6a6b6', 'STAFF');

-- Seed Aftermarket Brands
INSERT OR IGNORE INTO meta_aftermarket_brands (name) VALUES 
('TRW'), ('BOSCH'), ('AISIN'), ('KYB'), ('LUCAS'), ('DENSO'), ('BREMBO'), ('GSP');

-- Seed Car Brands
INSERT OR IGNORE INTO meta_car_brands (name) VALUES 
('HONDA'), ('TOYOTA'), ('ISUZU'), ('NISSAN'), ('MAZDA');

-- Seed Car Models
INSERT OR IGNORE INTO meta_car_models (car_brand, name) VALUES 
('HONDA', 'Civic FB'),
('HONDA', 'Civic FC'),
('HONDA', 'Accord'),
('TOYOTA', 'Yaris'),
('TOYOTA', 'Hilux Revo'),
('TOYOTA', 'Vios'),
('ISUZU', 'D-Max'),
('NISSAN', 'Navara'),
('MAZDA', 'Mazda 2');

-- Seed Car Years
INSERT OR IGNORE INTO meta_car_years (year) VALUES 
('2012'), ('2013'), ('2014'), ('2015'), ('2016'), ('2017'), ('2018'), ('2019'), ('2020'), ('2021'), ('2022'), ('2023'), ('2024'), ('2025'), ('2026');
