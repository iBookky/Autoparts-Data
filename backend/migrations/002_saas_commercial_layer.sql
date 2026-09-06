-- 002_saas_commercial_layer.sql
-- Additive, non-destructive migration for B2B SaaS Data Platform

-- 1. Organizations (Tenants)
CREATE TABLE IF NOT EXISTS organizations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    plan_tier TEXT NOT NULL DEFAULT 'PROFESSIONAL', -- STARTER, PROFESSIONAL, BUSINESS, ENTERPRISE
    billing_email TEXT,
    tax_id TEXT,
    address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Organization Members (Users with Tenant Roles)
CREATE TABLE IF NOT EXISTS organization_members (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    org_role TEXT NOT NULL CHECK (org_role IN ('OWNER', 'ADMIN', 'MEMBER')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(org_id, user_id)
);

-- 3. Commercial Subscription Plans Catalog
CREATE TABLE IF NOT EXISTS plans (
    id TEXT PRIMARY KEY, -- starter, professional, business, enterprise
    name TEXT NOT NULL,
    price_monthly INTEGER NOT NULL, -- in THB
    max_brands INTEGER NOT NULL, -- -1 for unlimited
    max_categories INTEGER NOT NULL, -- -1 for unlimited
    max_users INTEGER NOT NULL,
    monthly_search_quota INTEGER NOT NULL,
    vin_search_enabled INTEGER DEFAULT 0,
    api_access_enabled INTEGER DEFAULT 0,
    export_enabled INTEGER DEFAULT 0,
    ai_search_enabled INTEGER DEFAULT 0
);

-- 4. Organization Subscriptions & Add-ons
CREATE TABLE IF NOT EXISTS subscriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL UNIQUE,
    plan_id TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('ACTIVE', 'TRIALING', 'PAST_DUE', 'CANCELED')) DEFAULT 'ACTIVE',
    billing_cycle TEXT NOT NULL DEFAULT 'MONTHLY',
    current_period_start DATETIME DEFAULT CURRENT_TIMESTAMP,
    current_period_end DATETIME NOT NULL,
    ai_power_pack INTEGER DEFAULT 0, -- +1990 THB add-on
    extra_searches INTEGER DEFAULT 0,
    extra_users INTEGER DEFAULT 0,
    extra_brands INTEGER DEFAULT 0,
    extra_categories INTEGER DEFAULT 0,
    FOREIGN KEY(org_id) REFERENCES organizations(id),
    FOREIGN KEY(plan_id) REFERENCES plans(id)
);

-- 5. Data Access Entitlements (Brand / Category whitelist per Org)
CREATE TABLE IF NOT EXISTS entitlements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    entitlement_type TEXT NOT NULL CHECK (entitlement_type IN ('BRAND', 'CATEGORY', 'FEATURE')),
    entitlement_value TEXT NOT NULL, -- e.g., 'TOYOTA', 'ระบบเบรก', 'API_ACCESS'
    is_granted INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(org_id) REFERENCES organizations(id),
    UNIQUE(org_id, entitlement_type, entitlement_value)
);

-- 6. Usage Tracking
CREATE TABLE IF NOT EXISTS usage_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    period_month TEXT NOT NULL, -- YYYY-MM
    searches_used INTEGER DEFAULT 0,
    vin_lookups_used INTEGER DEFAULT 0,
    api_calls_used INTEGER DEFAULT 0,
    exports_used INTEGER DEFAULT 0,
    ai_credits_used INTEGER DEFAULT 0,
    UNIQUE(org_id, period_month),
    FOREIGN KEY(org_id) REFERENCES organizations(id)
);

-- 7. Search & Audit Logs
CREATE TABLE IF NOT EXISTS search_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    user_id INTEGER,
    search_query TEXT,
    search_type TEXT, -- QUICK, ADVANCED, VIN, API, AI
    results_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 8. Customer Saved Favorites
CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    part_id INTEGER NOT NULL,
    part_source TEXT NOT NULL, -- MASTER, TEMP
    brand TEXT,
    part_number TEXT,
    oem_number TEXT,
    product_name TEXT,
    car_brand TEXT,
    car_model TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, part_id, part_source)
);

-- 9. Hashed API Keys
CREATE TABLE IF NOT EXISTS api_keys (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    key_prefix TEXT NOT NULL, -- first 8 chars for display
    key_hash TEXT NOT NULL UNIQUE, -- SHA-256 hash
    rate_limit_per_min INTEGER DEFAULT 60,
    is_active INTEGER DEFAULT 1,
    last_used_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(org_id) REFERENCES organizations(id)
);

-- 10. Billing Invoices
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    org_id INTEGER NOT NULL,
    amount INTEGER NOT NULL, -- THB
    vat_amount INTEGER NOT NULL,
    total_amount INTEGER NOT NULL,
    status TEXT CHECK (status IN ('PAID', 'PENDING', 'VOID')) DEFAULT 'PAID',
    payment_method TEXT DEFAULT 'CREDIT_CARD', -- PROMPTPAY, CREDIT_CARD, BANK_TRANSFER
    period_start DATE,
    period_end DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(org_id) REFERENCES organizations(id)
);

-- Indexes for high performance
CREATE INDEX IF NOT EXISTS idx_org_slug ON organizations(slug);
CREATE INDEX IF NOT EXISTS idx_sub_org ON subscriptions(org_id);
CREATE INDEX IF NOT EXISTS idx_entitlements_lookup ON entitlements(org_id, entitlement_type, is_granted);
CREATE INDEX IF NOT EXISTS idx_usage_period ON usage_records(org_id, period_month);
CREATE INDEX IF NOT EXISTS idx_search_logs_org ON search_logs(org_id, created_at);
CREATE INDEX IF NOT EXISTS idx_api_keys_hash ON api_keys(key_hash, is_active);
CREATE INDEX IF NOT EXISTS idx_user_fav ON user_favorites(user_id, org_id);

-- ================= SEED INITIAL SAAS DATA =================

-- Seed Standard Plans
INSERT OR IGNORE INTO plans (id, name, price_monthly, max_brands, max_categories, max_users, monthly_search_quota, vin_search_enabled, api_access_enabled, export_enabled, ai_search_enabled) VALUES
('starter', 'STARTER', 1290, 1, 3, 1, 1000, 0, 0, 0, 0),
('professional', 'PROFESSIONAL', 2990, 5, 10, 5, 5000, 1, 0, 0, 1),
('business', 'BUSINESS', 5990, -1, -1, 20, 20000, 1, 1, 1, 1),
('enterprise', 'ENTERPRISE', 14900, -1, -1, 999, 100000, 1, 1, 1, 1);

-- Seed Default Organization
INSERT OR IGNORE INTO organizations (id, name, slug, plan_tier, billing_email, tax_id, address) VALUES
(1, 'Siam Auto Supply Co., Ltd.', 'siam-auto-supply', 'PROFESSIONAL', 'billing@siamauto.co.th', '0105558012345', '888 Rama 9 Rd, Bangkok 10310'),
(2, 'Apex Parts Distribution', 'apex-parts', 'BUSINESS', 'admin@apexparts.com', '0105561098765', '123 Sukhumvit Rd, Bangkok 10110');

-- Link default users to organization 1
INSERT OR IGNORE INTO organization_members (org_id, user_id, org_role)
SELECT 1, id, CASE WHEN role = 'SUPER_ADMIN' THEN 'OWNER' WHEN role = 'ADMIN' THEN 'ADMIN' ELSE 'MEMBER' END
FROM users;

-- Seed Default Subscriptions for Org 1 & Org 2
INSERT OR IGNORE INTO subscriptions (org_id, plan_id, status, billing_cycle, current_period_start, current_period_end, ai_power_pack, extra_searches) VALUES
(1, 'professional', 'ACTIVE', 'MONTHLY', datetime('now', '-15 days'), datetime('now', '+15 days'), 1, 0),
(2, 'business', 'ACTIVE', 'MONTHLY', datetime('now', '-5 days'), datetime('now', '+25 days'), 1, 5000);

-- Seed Initial Usage Records
INSERT OR IGNORE INTO usage_records (org_id, period_month, searches_used, vin_lookups_used, api_calls_used, exports_used, ai_credits_used) VALUES
(1, strftime('%Y-%m', 'now'), 1248, 86, 0, 2, 45),
(2, strftime('%Y-%m', 'now'), 4820, 310, 1280, 14, 180);

-- Seed Sample Invoices for Org 1
INSERT OR IGNORE INTO invoices (invoice_number, org_id, amount, vat_amount, total_amount, status, payment_method, period_start, period_end, created_at) VALUES
('INV-2026-0801', 1, 4980, 348, 5328, 'PAID', 'CREDIT_CARD', date('now', '-30 days'), date('now'), datetime('now', '-30 days')),
('INV-2026-0701', 1, 4980, 348, 5328, 'PAID', 'CREDIT_CARD', date('now', '-60 days'), date('now', '-30 days'), datetime('now', '-60 days'));
