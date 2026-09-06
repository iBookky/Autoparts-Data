-- PostgreSQL Migration: 005_subscription_billing_engine.sql

CREATE TABLE IF NOT EXISTS plan_versions (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(100) NOT NULL REFERENCES plans(id),
    version_number INTEGER NOT NULL DEFAULT 1,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    billing_interval VARCHAR(50) NOT NULL CHECK (billing_interval IN ('MONTHLY', 'YEARLY', 'QUARTERLY', 'CUSTOM')),
    base_price INTEGER NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'THB',
    max_brands INTEGER NOT NULL DEFAULT 1,
    max_categories INTEGER NOT NULL DEFAULT 3,
    max_users INTEGER NOT NULL DEFAULT 1,
    monthly_search_quota INTEGER NOT NULL DEFAULT 1000,
    api_quota INTEGER NOT NULL DEFAULT 0,
    export_quota INTEGER NOT NULL DEFAULT 0,
    ai_quota INTEGER NOT NULL DEFAULT 0,
    trial_period_days INTEGER NOT NULL DEFAULT 0,
    is_current INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL CHECK (status IN ('DRAFT', 'ACTIVE', 'ARCHIVED')) DEFAULT 'ACTIVE',
    effective_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (plan_id, version_number, billing_interval)
);

CREATE TABLE IF NOT EXISTS plan_features (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(100) NOT NULL REFERENCES plans(id),
    feature_code VARCHAR(100) NOT NULL CHECK (feature_code IN ('SEARCH', 'VIN_SEARCH', 'VEHICLE_SEARCH', 'CROSS_REFERENCE', 'API', 'EXPORT', 'AI', 'SAVED_PARTS')),
    is_included INTEGER NOT NULL DEFAULT 1,
    limit_value INTEGER DEFAULT -1,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (plan_id, feature_code)
);

CREATE TABLE IF NOT EXISTS plan_entitlements (
    id SERIAL PRIMARY KEY,
    plan_id VARCHAR(100) NOT NULL REFERENCES plans(id),
    entitlement_type VARCHAR(50) NOT NULL CHECK (entitlement_type IN ('BRAND', 'CATEGORY', 'FEATURE')),
    entitlement_value VARCHAR(255) NOT NULL,
    mode VARCHAR(50) NOT NULL CHECK (mode IN ('INCLUDE', 'EXCLUDE')) DEFAULT 'INCLUDE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (plan_id, entitlement_type, entitlement_value)
);

CREATE TABLE IF NOT EXISTS add_ons (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    code VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    price_monthly INTEGER NOT NULL,
    price_yearly INTEGER,
    currency VARCHAR(10) NOT NULL DEFAULT 'THB',
    add_on_type VARCHAR(50) NOT NULL CHECK (add_on_type IN ('QUOTA', 'FEATURE', 'SEATS', 'PACK')),
    quota_delta INTEGER DEFAULT 0,
    feature_code VARCHAR(100),
    status VARCHAR(50) NOT NULL CHECK (status IN ('ACTIVE', 'ARCHIVED')) DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS add_on_plan_compatibility (
    id SERIAL PRIMARY KEY,
    add_on_id VARCHAR(100) NOT NULL REFERENCES add_ons(id),
    plan_id VARCHAR(100) NOT NULL REFERENCES plans(id),
    availability VARCHAR(50) NOT NULL CHECK (availability IN ('INCLUDED', 'ADDON_AVAILABLE', 'NOT_SUPPORTED')) DEFAULT 'ADDON_AVAILABLE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (add_on_id, plan_id)
);

CREATE TABLE IF NOT EXISTS subscription_items (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('PLAN', 'ADDON', 'ONE_OFF')),
    item_code VARCHAR(100) NOT NULL,
    item_name VARCHAR(150) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price INTEGER NOT NULL,
    total_price INTEGER NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'THB',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS subscription_entitlements_snapshot (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    snapshot_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    plan_version_id INTEGER,
    max_brands INTEGER NOT NULL,
    max_categories INTEGER NOT NULL,
    max_users INTEGER NOT NULL,
    monthly_search_quota INTEGER NOT NULL,
    api_enabled INTEGER NOT NULL DEFAULT 0,
    export_enabled INTEGER NOT NULL DEFAULT 0,
    ai_enabled INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coupons (
    id VARCHAR(100) PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    discount_type VARCHAR(50) NOT NULL CHECK (discount_type IN ('PERCENTAGE', 'FIXED_AMOUNT')),
    discount_value INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'THB',
    max_redemptions INTEGER DEFAULT -1,
    redemptions_count INTEGER DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1,
    valid_from TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    valid_until TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    subscription_id INTEGER,
    amount INTEGER NOT NULL,
    vat_amount INTEGER NOT NULL DEFAULT 0,
    total_amount INTEGER NOT NULL,
    currency VARCHAR(10) NOT NULL DEFAULT 'THB',
    status VARCHAR(50) NOT NULL CHECK (status IN ('DRAFT', 'OPEN', 'PENDING', 'PAID', 'VOID', 'OVERDUE', 'REFUNDED')) DEFAULT 'OPEN',
    payment_method VARCHAR(100),
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('BASE_PLAN', 'ADDON', 'DISCOUNT', 'VAT', 'PRORATION', 'TAX')),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_amount INTEGER NOT NULL,
    total_amount INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS coupon_redemptions (
    id SERIAL PRIMARY KEY,
    coupon_id VARCHAR(100) NOT NULL REFERENCES coupons(id),
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    invoice_id INTEGER REFERENCES invoices(id),
    discount_amount INTEGER NOT NULL,
    redeemed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS commercial_audit_logs (
    id SERIAL PRIMARY KEY,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    actor_user_id INTEGER,
    actor_username VARCHAR(150),
    action VARCHAR(150) NOT NULL,
    target_type VARCHAR(100) NOT NULL,
    target_id VARCHAR(100),
    before_state TEXT,
    after_state TEXT,
    details TEXT,
    ip_address VARCHAR(100) DEFAULT '127.0.0.1',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
