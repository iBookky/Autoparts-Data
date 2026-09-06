-- PostgreSQL Migration: 001_init_schema.sql
-- Initializes users, master_parts, temp_parts, and metadata tables

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('OWNER', 'SUPER_ADMIN', 'ADMIN', 'STAFF', 'CUSTOMER', 'CUSTOMER_OWNER', 'CUSTOMER_MANAGER', 'CUSTOMER_STAFF', 'SYSTEM_OWNER')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS master_parts (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(150),
    part_number VARCHAR(150),
    oem_number VARCHAR(150),
    product_name_th TEXT,
    product_name_en TEXT,
    category VARCHAR(150),
    car_brand VARCHAR(150),
    car_model VARCHAR(150),
    year_start VARCHAR(50),
    year_end VARCHAR(50),
    engine VARCHAR(150),
    fuel VARCHAR(100),
    transmission VARCHAR(100),
    description TEXT,
    cost_unit VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(brand, part_number, oem_number, car_brand, car_model)
);

CREATE TABLE IF NOT EXISTS temp_parts (
    id SERIAL PRIMARY KEY,
    brand VARCHAR(150),
    part_number VARCHAR(150),
    oem_number VARCHAR(150),
    product_name_th TEXT,
    product_name_en TEXT,
    category VARCHAR(150),
    car_brand VARCHAR(150),
    car_model VARCHAR(150),
    year_start VARCHAR(50),
    year_end VARCHAR(50),
    engine VARCHAR(150),
    fuel VARCHAR(100),
    transmission VARCHAR(100),
    description TEXT,
    cost_unit VARCHAR(100),
    notes TEXT,
    source_type VARCHAR(50) CHECK (source_type IN ('SCRAPE_DAILY', 'ON_DEMAND', 'EXCEL_IMPORT')),
    status VARCHAR(50) CHECK (status IN ('PENDING', 'PENDING_URGENT', 'APPROVED', 'REJECTED')) DEFAULT 'PENDING',
    staff_note TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meta_aftermarket_brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS meta_car_brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS meta_car_models (
    id SERIAL PRIMARY KEY,
    car_brand VARCHAR(150) NOT NULL,
    name VARCHAR(150) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS meta_car_years (
    id SERIAL PRIMARY KEY,
    year VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS meta_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE NOT NULL,
    name_en VARCHAR(150)
);

CREATE TABLE IF NOT EXISTS meta_ai_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(150) UNIQUE NOT NULL,
    provider VARCHAR(100) NOT NULL,
    description TEXT,
    is_preset INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 1,
    is_default INTEGER DEFAULT 0,
    cost_per_1k_tokens REAL DEFAULT 0.001
);

CREATE TABLE IF NOT EXISTS agent_skills_config (
    id SERIAL PRIMARY KEY,
    skill_key VARCHAR(100) UNIQUE NOT NULL,
    skill_name VARCHAR(150) NOT NULL,
    description TEXT,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS ai_keys_config (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(150) UNIQUE NOT NULL,
    api_key TEXT NOT NULL,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_usage_stats (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(150) NOT NULL,
    usage_date VARCHAR(50) NOT NULL,
    call_count INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    UNIQUE(model_name, usage_date)
);
