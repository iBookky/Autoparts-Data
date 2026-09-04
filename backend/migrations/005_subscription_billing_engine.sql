-- 005_subscription_billing_engine.sql
-- Additive, non-destructive migration for Commercial Subscription, Plans, Add-ons & Billing Engine

-- 1. Plan Versions (Preserving historical pricing and parameters)
CREATE TABLE IF NOT EXISTS plan_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT NOT NULL, -- starter, professional, business, enterprise
    version_number INTEGER NOT NULL DEFAULT 1,
    name TEXT NOT NULL,
    description TEXT,
    billing_interval TEXT NOT NULL CHECK (billing_interval IN ('MONTHLY', 'YEARLY', 'QUARTERLY', 'CUSTOM')),
    base_price INTEGER NOT NULL, -- In currency minor/base units (e.g. THB)
    currency TEXT NOT NULL DEFAULT 'THB',
    max_brands INTEGER NOT NULL DEFAULT 1, -- -1 for unlimited
    max_categories INTEGER NOT NULL DEFAULT 3, -- -1 for unlimited
    max_users INTEGER NOT NULL DEFAULT 1,
    monthly_search_quota INTEGER NOT NULL DEFAULT 1000,
    api_quota INTEGER NOT NULL DEFAULT 0,
    export_quota INTEGER NOT NULL DEFAULT 0,
    ai_quota INTEGER NOT NULL DEFAULT 0,
    trial_period_days INTEGER NOT NULL DEFAULT 0,
    is_current INTEGER NOT NULL DEFAULT 1,
    status TEXT NOT NULL CHECK (status IN ('DRAFT', 'ACTIVE', 'ARCHIVED')) DEFAULT 'ACTIVE',
    effective_from DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans(id),
    UNIQUE (plan_id, version_number, billing_interval)
);

-- 2. Plan Features Mapping
CREATE TABLE IF NOT EXISTS plan_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT NOT NULL,
    feature_code TEXT NOT NULL CHECK (feature_code IN ('SEARCH', 'VIN_SEARCH', 'VEHICLE_SEARCH', 'CROSS_REFERENCE', 'API', 'EXPORT', 'AI', 'SAVED_PARTS')),
    is_included INTEGER NOT NULL DEFAULT 1,
    limit_value INTEGER DEFAULT -1, -- -1 for unlimited
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans(id),
    UNIQUE (plan_id, feature_code)
);

-- 3. Plan Entitlement Whitelist Definitions
CREATE TABLE IF NOT EXISTS plan_entitlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plan_id TEXT NOT NULL,
    entitlement_type TEXT NOT NULL CHECK (entitlement_type IN ('BRAND', 'CATEGORY', 'FEATURE')),
    entitlement_value TEXT NOT NULL, -- e.g. 'Toyota', 'ระบบเบรก', '*'
    mode TEXT NOT NULL CHECK (mode IN ('INCLUDE', 'EXCLUDE')) DEFAULT 'INCLUDE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans(id),
    UNIQUE (plan_id, entitlement_type, entitlement_value)
);

-- 4. Commercial Add-ons Catalog
CREATE TABLE IF NOT EXISTS add_ons (
    id TEXT PRIMARY KEY, -- extra_searches_5k, extra_users_5, api_access_pack, ai_power_pack, extra_brands_5, extra_categories_5
    name TEXT NOT NULL,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    price_monthly INTEGER NOT NULL,
    price_yearly INTEGER NOT NULL,
    currency TEXT NOT NULL DEFAULT 'THB',
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'ARCHIVED')) DEFAULT 'ACTIVE',
    entitlement_type TEXT NOT NULL CHECK (entitlement_type IN ('SEARCH_QUOTA', 'USER_LIMIT', 'BRAND_ACCESS', 'CATEGORY_ACCESS', 'API_ACCESS', 'AI_POWER_PACK', 'EXPORT_PACK')),
    quota_increase INTEGER DEFAULT 0,
    user_increase INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. Add-on Plan Compatibility Matrix
CREATE TABLE IF NOT EXISTS add_on_plan_compatibility (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    add_on_id TEXT NOT NULL,
    plan_id TEXT NOT NULL,
    availability TEXT NOT NULL CHECK (availability IN ('INCLUDED', 'AVAILABLE', 'NOT_AVAILABLE')) DEFAULT 'AVAILABLE',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (add_on_id) REFERENCES add_ons(id),
    FOREIGN KEY (plan_id) REFERENCES plans(id),
    UNIQUE (add_on_id, plan_id)
);

-- 6. Subscription Line Items (Base Plan + Attached Add-ons)
CREATE TABLE IF NOT EXISTS subscription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER NOT NULL,
    item_type TEXT NOT NULL CHECK (item_type IN ('PLAN', 'ADD_ON')),
    item_code TEXT NOT NULL, -- plan_id or add_on_id
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price INTEGER NOT NULL,
    billing_interval TEXT NOT NULL DEFAULT 'MONTHLY',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
);

-- 7. Subscription Entitlements Freeze / Snapshot
CREATE TABLE IF NOT EXISTS subscription_entitlements_snapshot (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscription_id INTEGER NOT NULL,
    snapshot_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    plan_version_id INTEGER NOT NULL,
    max_brands INTEGER NOT NULL,
    max_categories INTEGER NOT NULL,
    max_users INTEGER NOT NULL,
    monthly_search_quota INTEGER NOT NULL,
    vin_search_enabled INTEGER NOT NULL,
    api_access_enabled INTEGER NOT NULL,
    export_enabled INTEGER NOT NULL,
    ai_search_enabled INTEGER NOT NULL,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE
);

-- 8. Coupons & Discounts Engine
CREATE TABLE IF NOT EXISTS coupons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    description TEXT,
    discount_type TEXT NOT NULL CHECK (discount_type IN ('PERCENT', 'FIXED')),
    discount_value REAL NOT NULL, -- e.g. 10.0 for 10% or 500 for 500 THB
    currency TEXT NOT NULL DEFAULT 'THB',
    min_purchase INTEGER DEFAULT 0,
    max_discount INTEGER DEFAULT -1, -- -1 for no cap
    usage_limit INTEGER DEFAULT -1, -- -1 for unlimited
    used_count INTEGER DEFAULT 0,
    per_org_limit INTEGER DEFAULT 1,
    applicable_plans TEXT DEFAULT '*', -- '*' or comma-separated e.g. 'professional,business'
    valid_from DATETIME DEFAULT CURRENT_TIMESTAMP,
    valid_until DATETIME,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS coupon_redemptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    coupon_id INTEGER NOT NULL,
    org_id INTEGER NOT NULL,
    invoice_id INTEGER,
    discount_amount INTEGER NOT NULL,
    redeemed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (coupon_id) REFERENCES coupons(id),
    FOREIGN KEY (org_id) REFERENCES organizations(id),
    FOREIGN KEY (invoice_id) REFERENCES invoices(id)
);

-- 9. Invoice Line Items Breakdown
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    description TEXT NOT NULL,
    item_type TEXT NOT NULL CHECK (item_type IN ('PLAN', 'ADD_ON', 'PRORATION_CREDIT', 'PRORATION_CHARGE', 'DISCOUNT', 'TAX')),
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_price INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE
);

-- 10. Commercial Operations Audit Log
CREATE TABLE IF NOT EXISTS commercial_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER,
    actor_user_id INTEGER,
    actor_username TEXT NOT NULL,
    action TEXT NOT NULL, -- PLAN_CREATED, PLAN_VERSIONED, ADDON_CONFIGURED, COUPON_CREATED, SUB_UPGRADED, SUB_DOWNGRADED, SUB_CANCELLED, SUB_REACTIVATED, PAYMENT_PROCESSED, INVOICE_GENERATED
    target_type TEXT NOT NULL, -- PLAN, ADD_ON, COUPON, SUBSCRIPTION, INVOICE, PAYMENT
    target_id TEXT,
    before_state TEXT,
    after_state TEXT,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ================= SEED INITIAL DATA FOR PHASE 5 =================

-- Seed Plan Versions
INSERT OR IGNORE INTO plan_versions (plan_id, version_number, name, description, billing_interval, base_price, currency, max_brands, max_categories, max_users, monthly_search_quota, api_quota, export_quota, ai_quota, trial_period_days, is_current, status) VALUES
('starter', 1, 'STARTER (Monthly)', 'For individual technicians & independent repair shops', 'MONTHLY', 1290, 'THB', 1, 3, 1, 1000, 0, 0, 0, 14, 1, 'ACTIVE'),
('starter', 1, 'STARTER (Yearly)', 'For individual technicians & independent repair shops (Save 2 months)', 'YEARLY', 12900, 'THB', 1, 3, 1, 1000, 0, 0, 0, 14, 1, 'ACTIVE'),

('professional', 1, 'PROFESSIONAL (Monthly)', 'For auto parts retailers & medium service centers', 'MONTHLY', 2990, 'THB', 5, 10, 5, 5000, 0, 0, 100, 14, 1, 'ACTIVE'),
('professional', 1, 'PROFESSIONAL (Yearly)', 'For auto parts retailers & medium service centers (Save 2 months)', 'YEARLY', 29900, 'THB', 5, 10, 5, 5000, 0, 0, 100, 14, 1, 'ACTIVE'),

('business', 1, 'BUSINESS (Monthly)', 'For wholesale distributors & multi-branch garage networks', 'MONTHLY', 5990, 'THB', -1, -1, 20, 20000, 5000, 500, 500, 0, 1, 'ACTIVE'),
('business', 1, 'BUSINESS (Yearly)', 'For wholesale distributors & multi-branch garage networks (Save 2 months)', 'YEARLY', 59900, 'THB', -1, -1, 20, 20000, 5000, 500, 500, 0, 1, 'ACTIVE'),

('enterprise', 1, 'ENTERPRISE (Monthly)', 'For insurance groups, major distributors & enterprise fleets', 'MONTHLY', 14900, 'THB', -1, -1, 999, 100000, 50000, 5000, 2500, 0, 1, 'ACTIVE'),
('enterprise', 1, 'ENTERPRISE (Yearly)', 'For insurance groups, major distributors & enterprise fleets', 'YEARLY', 149000, 'THB', -1, -1, 999, 100000, 50000, 5000, 2500, 0, 1, 'ACTIVE');

-- Seed Plan Features
INSERT OR IGNORE INTO plan_features (plan_id, feature_code, is_included, limit_value) VALUES
('starter', 'SEARCH', 1, 1000),
('starter', 'VIN_SEARCH', 0, 0),
('starter', 'VEHICLE_SEARCH', 1, -1),
('starter', 'CROSS_REFERENCE', 1, -1),
('starter', 'API', 0, 0),
('starter', 'EXPORT', 0, 0),
('starter', 'AI', 0, 0),
('starter', 'SAVED_PARTS', 1, 50),

('professional', 'SEARCH', 1, 5000),
('professional', 'VIN_SEARCH', 1, -1),
('professional', 'VEHICLE_SEARCH', 1, -1),
('professional', 'CROSS_REFERENCE', 1, -1),
('professional', 'API', 0, 0),
('professional', 'EXPORT', 0, 0),
('professional', 'AI', 1, 100),
('professional', 'SAVED_PARTS', 1, 250),

('business', 'SEARCH', 1, 20000),
('business', 'VIN_SEARCH', 1, -1),
('business', 'VEHICLE_SEARCH', 1, -1),
('business', 'CROSS_REFERENCE', 1, -1),
('business', 'API', 1, 5000),
('business', 'EXPORT', 1, 500),
('business', 'AI', 1, 500),
('business', 'SAVED_PARTS', 1, 1000),

('enterprise', 'SEARCH', 1, 100000),
('enterprise', 'VIN_SEARCH', 1, -1),
('enterprise', 'VEHICLE_SEARCH', 1, -1),
('enterprise', 'CROSS_REFERENCE', 1, -1),
('enterprise', 'API', 1, 50000),
('enterprise', 'EXPORT', 0, 0),
('enterprise', 'AI', 1, 2500),
('enterprise', 'SAVED_PARTS', 1, -1);

-- Seed Add-ons Catalog
INSERT OR IGNORE INTO add_ons (id, name, code, description, price_monthly, price_yearly, entitlement_type, quota_increase, user_increase) VALUES
('extra_searches_5k', '+5,000 Search Credits Pack', 'EXTRA_SEARCH_5K', 'Add 5,000 monthly searches to your organization quota', 890, 8900, 'SEARCH_QUOTA', 5000, 0),
('extra_searches_20k', '+20,000 Search Credits Pack', 'EXTRA_SEARCH_20K', 'Add 20,000 monthly searches to your organization quota', 2490, 24900, 'SEARCH_QUOTA', 20000, 0),
('extra_users_5', '+5 Team Member Seats', 'EXTRA_USERS_5', 'Expand your team access with 5 additional staff/manager seats', 990, 9900, 'USER_LIMIT', 0, 5),
('extra_users_10', '+10 Team Member Seats', 'EXTRA_USERS_10', 'Expand your team access with 10 additional staff/manager seats', 1790, 17900, 'USER_LIMIT', 0, 10),
('api_access_pack', 'REST API Developer Pack', 'API_DEV_PACK', 'Enable secure REST API access with 5,000 monthly requests and API keys', 1490, 14900, 'API_ACCESS', 0, 0),
('ai_power_pack', 'AI Neural Match & Cross-Ref Pack', 'AI_POWER_PACK', 'Enhanced AI model search assistance, smart cross-reference & image lookup', 1990, 19900, 'AI_POWER_PACK', 0, 0),
('priority_support_pack', '24/7 Dedicated Priority Support', 'PRIORITY_SUPPORT', 'Dedicated technical account manager and expedited catalog lookup SLA', 990, 9900, 'SUPPORT_PACK', 0, 0);

-- Seed Add-on Plan Compatibility
INSERT OR IGNORE INTO add_on_plan_compatibility (add_on_id, plan_id, availability) VALUES
-- Starter
('extra_searches_5k', 'starter', 'AVAILABLE'),
('extra_searches_20k', 'starter', 'NOT_AVAILABLE'),
('extra_users_5', 'starter', 'AVAILABLE'),
('extra_users_10', 'starter', 'NOT_AVAILABLE'),
('api_access_pack', 'starter', 'NOT_AVAILABLE'),
('ai_power_pack', 'starter', 'AVAILABLE'),
('priority_support_pack', 'starter', 'AVAILABLE'),

-- Professional
('extra_searches_5k', 'professional', 'AVAILABLE'),
('extra_searches_20k', 'professional', 'AVAILABLE'),
('extra_users_5', 'professional', 'AVAILABLE'),
('extra_users_10', 'professional', 'AVAILABLE'),
('api_access_pack', 'professional', 'AVAILABLE'),
('ai_power_pack', 'professional', 'AVAILABLE'),
('priority_support_pack', 'professional', 'AVAILABLE'),

-- Business
('extra_searches_5k', 'business', 'AVAILABLE'),
('extra_searches_20k', 'business', 'AVAILABLE'),
('extra_users_5', 'business', 'AVAILABLE'),
('extra_users_10', 'business', 'AVAILABLE'),
('api_access_pack', 'business', 'INCLUDED'),
('ai_power_pack', 'business', 'INCLUDED'),
('priority_support_pack', 'business', 'INCLUDED'),

-- Enterprise
('extra_searches_5k', 'enterprise', 'AVAILABLE'),
('extra_searches_20k', 'enterprise', 'AVAILABLE'),
('extra_users_5', 'enterprise', 'INCLUDED'),
('extra_users_10', 'enterprise', 'INCLUDED'),
('api_access_pack', 'enterprise', 'INCLUDED'),
('ai_power_pack', 'enterprise', 'INCLUDED'),
('priority_support_pack', 'enterprise', 'INCLUDED');

-- Seed Standard Sample Coupons
INSERT OR IGNORE INTO coupons (code, description, discount_type, discount_value, min_purchase, usage_limit, is_active) VALUES
('WELCOME10', '10% Discount on First Subscription Period', 'PERCENT', 10.0, 1000, 1000, 1),
('B2B500', '฿500 Instant Discount for Professional Plan', 'FIXED', 500.0, 2000, 500, 1),
('SUMMER2026', '15% Seasonal Discount on Yearly Subscriptions', 'PERCENT', 15.0, 5000, 200, 1),
('COMMERCIAL20', '20% Commercial Launch Discount', 'PERCENT', 20.0, 1000, 1000, 1),
('LAUNCH50', '50% Early Adopter Launch Special', 'PERCENT', 50.0, 1000, 500, 1);
