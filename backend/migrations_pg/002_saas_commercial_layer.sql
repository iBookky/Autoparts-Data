-- PostgreSQL Migration: 002_saas_commercial_layer.sql

CREATE TABLE IF NOT EXISTS organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE NOT NULL,
    plan_tier VARCHAR(100) NOT NULL DEFAULT 'PROFESSIONAL',
    billing_email VARCHAR(255),
    tax_id VARCHAR(100),
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    legal_name TEXT,
    business_type VARCHAR(100),
    phone VARCHAR(100),
    website VARCHAR(255),
    contact_person VARCHAR(255),
    industry VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Thailand',
    timezone VARCHAR(100) DEFAULT 'Asia/Bangkok',
    currency VARCHAR(10) DEFAULT 'THB'
);

CREATE TABLE IF NOT EXISTS organization_members (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    org_role VARCHAR(50) NOT NULL CHECK (org_role IN ('OWNER', 'MANAGER', 'STAFF', 'ADMIN', 'MEMBER')),
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'INVITED', 'SUSPENDED', 'DISABLED')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_id, user_id)
);

CREATE TABLE IF NOT EXISTS plans (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    price_monthly INTEGER NOT NULL,
    max_brands INTEGER NOT NULL,
    max_categories INTEGER NOT NULL,
    max_users INTEGER NOT NULL,
    monthly_search_quota INTEGER NOT NULL,
    vin_search_enabled INTEGER DEFAULT 0,
    api_access_enabled INTEGER DEFAULT 0,
    export_enabled INTEGER DEFAULT 0,
    ai_search_enabled INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS subscriptions (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL UNIQUE REFERENCES organizations(id),
    plan_id VARCHAR(100) NOT NULL REFERENCES plans(id),
    plan_version_id INTEGER,
    status VARCHAR(50) NOT NULL CHECK (status IN ('TRIAL', 'TRIALING', 'ACTIVE', 'PAST_DUE', 'GRACE_PERIOD', 'SUSPENDED', 'CANCELLED', 'CANCELED', 'EXPIRED')) DEFAULT 'ACTIVE',
    billing_cycle VARCHAR(50) NOT NULL DEFAULT 'MONTHLY',
    billing_interval VARCHAR(50) NOT NULL DEFAULT 'MONTHLY',
    current_period_start TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    trial_end TIMESTAMP WITH TIME ZONE,
    next_billing_date TIMESTAMP WITH TIME ZONE,
    cancel_at_period_end INTEGER DEFAULT 0,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    grace_period_end TIMESTAMP WITH TIME ZONE,
    currency VARCHAR(10) NOT NULL DEFAULT 'THB',
    base_price INTEGER DEFAULT 0,
    discount_amount INTEGER DEFAULT 0,
    tax_amount INTEGER DEFAULT 0,
    total_amount INTEGER DEFAULT 0,
    ai_power_pack INTEGER DEFAULT 0,
    extra_searches INTEGER DEFAULT 0,
    extra_users INTEGER DEFAULT 0,
    extra_brands INTEGER DEFAULT 0,
    extra_categories INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS entitlements (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    entitlement_type VARCHAR(50) NOT NULL CHECK (entitlement_type IN ('BRAND', 'CATEGORY', 'FEATURE', 'EXPORT')),
    entitlement_value VARCHAR(255) NOT NULL,
    is_granted INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_id, entitlement_type, entitlement_value)
);

CREATE TABLE IF NOT EXISTS usage_records (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    period_month VARCHAR(50) NOT NULL,
    searches_used INTEGER DEFAULT 0,
    vin_lookups_used INTEGER DEFAULT 0,
    api_calls_used INTEGER DEFAULT 0,
    exports_used INTEGER DEFAULT 0,
    ai_credits_used INTEGER DEFAULT 0,
    UNIQUE(org_id, period_month)
);

CREATE TABLE IF NOT EXISTS search_logs (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL,
    user_id INTEGER,
    search_query TEXT,
    search_type VARCHAR(50),
    results_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS user_favorites (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    part_id INTEGER NOT NULL,
    part_source VARCHAR(50) DEFAULT 'MASTER',
    brand VARCHAR(150),
    part_number VARCHAR(150),
    oem_number VARCHAR(150),
    product_name TEXT,
    product_name_th TEXT,
    product_name_en TEXT,
    car_brand VARCHAR(150),
    car_model VARCHAR(150),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(org_id, user_id, part_id, part_source)
);

CREATE TABLE IF NOT EXISTS api_keys (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    name VARCHAR(150) NOT NULL,
    key_prefix VARCHAR(50) NOT NULL,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    rate_limit_per_min INTEGER DEFAULT 60,
    is_active INTEGER DEFAULT 1,
    last_used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'ACTIVE'
);

