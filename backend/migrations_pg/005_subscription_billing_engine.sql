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
    add_on_type VARCHAR(50) DEFAULT 'PACK',
    quota_delta INTEGER DEFAULT 0,
    feature_code VARCHAR(100),
    status VARCHAR(50) DEFAULT 'ACTIVE',
    entitlement_type VARCHAR(50),
    quota_increase INTEGER DEFAULT 0,
    user_increase INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS add_on_plan_compatibility (
    id SERIAL PRIMARY KEY,
    add_on_id VARCHAR(100) NOT NULL REFERENCES add_ons(id),
    plan_id VARCHAR(100) NOT NULL REFERENCES plans(id),
    availability VARCHAR(50) DEFAULT 'AVAILABLE',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (add_on_id, plan_id)
);

CREATE TABLE IF NOT EXISTS subscription_items (
    id SERIAL PRIMARY KEY,
    subscription_id INTEGER NOT NULL REFERENCES subscriptions(id) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL DEFAULT 'PLAN',
    item_code VARCHAR(100) NOT NULL,
    item_name VARCHAR(150) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price INTEGER DEFAULT 0,
    total_price INTEGER DEFAULT 0,
    billing_interval VARCHAR(50) DEFAULT 'MONTHLY',
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
    vin_search_enabled INTEGER DEFAULT 0,
    api_access_enabled INTEGER DEFAULT 0,
    export_enabled INTEGER DEFAULT 0,
    ai_search_enabled INTEGER DEFAULT 0,
    api_enabled INTEGER DEFAULT 0,
    ai_enabled INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    discount_type VARCHAR(50) NOT NULL DEFAULT 'PERCENT',
    discount_value INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'THB',
    min_purchase INTEGER DEFAULT 0,
    max_discount INTEGER DEFAULT 0,
    usage_limit INTEGER DEFAULT -1,
    used_count INTEGER DEFAULT 0,
    per_org_limit INTEGER DEFAULT 1,
    applicable_plans TEXT,
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
    status VARCHAR(50) DEFAULT 'OPEN',
    payment_method VARCHAR(100),
    period_start TIMESTAMP WITH TIME ZONE,
    period_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    item_type VARCHAR(50) DEFAULT 'BASE_PLAN',
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_amount INTEGER DEFAULT 0,
    unit_price INTEGER DEFAULT 0,
    amount INTEGER DEFAULT 0,
    total_amount INTEGER DEFAULT 0
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
    org_id INTEGER REFERENCES organizations(id),
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

-- Seed Add-ons Catalog
INSERT INTO add_ons (id, name, code, description, price_monthly, price_yearly, entitlement_type, quota_increase, user_increase) VALUES
('extra_searches_5k', '+5,000 Search Credits Pack', 'EXTRA_SEARCH_5K', 'Add 5,000 monthly searches to your organization quota', 890, 8900, 'SEARCH_QUOTA', 5000, 0),
('extra_searches_20k', '+20,000 Search Credits Pack', 'EXTRA_SEARCH_20K', 'Add 20,000 monthly searches to your organization quota', 2490, 24900, 'SEARCH_QUOTA', 20000, 0),
('extra_users_5', '+5 Team Member Seats', 'EXTRA_USERS_5', 'Expand your team access with 5 additional staff/manager seats', 990, 9900, 'USER_LIMIT', 0, 5),
('extra_users_10', '+10 Team Member Seats', 'EXTRA_USERS_10', 'Expand your team access with 10 additional staff/manager seats', 1790, 17900, 'USER_LIMIT', 0, 10),
('api_access_pack', 'REST API Developer Pack', 'API_DEV_PACK', 'Enable secure REST API access with 5,000 monthly requests and API keys', 1490, 14900, 'API_ACCESS', 0, 0),
('ai_power_pack', 'AI Neural Match & Cross-Ref Pack', 'AI_POWER_PACK', 'Enhanced AI model search assistance, smart cross-reference & image lookup', 1990, 19900, 'AI_POWER_PACK', 0, 0),
('priority_support_pack', '24/7 Dedicated Priority Support', 'PRIORITY_SUPPORT', 'Dedicated technical account manager and expedited catalog lookup SLA', 990, 9900, 'SUPPORT_PACK', 0, 0)
ON CONFLICT (id) DO NOTHING;

-- Seed Add-on Plan Compatibility
INSERT INTO add_on_plan_compatibility (add_on_id, plan_id, availability) VALUES
('extra_searches_5k', 'starter', 'AVAILABLE'),
('extra_searches_20k', 'starter', 'NOT_AVAILABLE'),
('extra_users_5', 'starter', 'AVAILABLE'),
('extra_users_10', 'starter', 'NOT_AVAILABLE'),
('api_access_pack', 'starter', 'NOT_AVAILABLE'),
('ai_power_pack', 'starter', 'AVAILABLE'),
('priority_support_pack', 'starter', 'AVAILABLE'),
('extra_searches_5k', 'professional', 'AVAILABLE'),
('extra_searches_20k', 'professional', 'AVAILABLE'),
('extra_users_5', 'professional', 'AVAILABLE'),
('extra_users_10', 'professional', 'AVAILABLE'),
('api_access_pack', 'professional', 'AVAILABLE'),
('ai_power_pack', 'professional', 'AVAILABLE'),
('priority_support_pack', 'professional', 'AVAILABLE'),
('extra_searches_5k', 'business', 'AVAILABLE'),
('extra_searches_20k', 'business', 'AVAILABLE'),
('extra_users_5', 'business', 'AVAILABLE'),
('extra_users_10', 'business', 'AVAILABLE'),
('api_access_pack', 'business', 'AVAILABLE'),
('ai_power_pack', 'business', 'AVAILABLE'),
('priority_support_pack', 'business', 'AVAILABLE'),
('extra_searches_5k', 'enterprise', 'AVAILABLE'),
('extra_searches_20k', 'enterprise', 'AVAILABLE'),
('extra_users_5', 'enterprise', 'AVAILABLE'),
('extra_users_10', 'enterprise', 'AVAILABLE'),
('api_access_pack', 'enterprise', 'AVAILABLE'),
('ai_power_pack', 'enterprise', 'AVAILABLE'),
('priority_support_pack', 'enterprise', 'AVAILABLE')
ON CONFLICT (add_on_id, plan_id) DO NOTHING;


