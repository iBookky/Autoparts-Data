-- 003_rbac_and_crm_pipeline.sql
-- Additive migration for 5-Tier User Architecture, Granular RBAC, CRM Pipeline, and Typed Cross-References

-- 1. Granular Roles Catalog
CREATE TABLE IF NOT EXISTS roles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    portal_access TEXT NOT NULL, -- /owner, /super-admin, /admin, /staff, /app
    tier_level INTEGER NOT NULL, -- 1=Owner, 2=SuperAdmin, 3=Admin, 4=Staff, 5=Customer
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 2. Permissions Catalog
CREATE TABLE IF NOT EXISTS permissions (
    id TEXT PRIMARY KEY,
    module TEXT NOT NULL, -- CRM, BILLING, CATALOG, SYSTEM, SEARCH, API, AI, ROLES
    name TEXT NOT NULL,
    description TEXT
);

-- 3. Role Permissions Mapping
CREATE TABLE IF NOT EXISTS role_permissions (
    role_id TEXT NOT NULL,
    permission_id TEXT NOT NULL,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(id) ON DELETE CASCADE
);

-- 4. User Assigned Roles & Scopes
CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL,
    role_id TEXT NOT NULL,
    scope_type TEXT NOT NULL DEFAULT 'GLOBAL', -- GLOBAL, ASSIGNED_CUSTOMERS, ASSIGNED_CATEGORIES, TENANT_ONLY
    scope_value TEXT,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);

-- 5. Customer & Lead Pipeline (CRM)
CREATE TABLE IF NOT EXISTS customer_leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    contact_person TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    assigned_staff_id INTEGER,
    pipeline_stage TEXT NOT NULL CHECK (pipeline_stage IN ('LEAD', 'CONTACTED', 'DEMO', 'TRIAL', 'PROPOSAL', 'SUBSCRIBED', 'ACTIVE', 'CHURNED')) DEFAULT 'LEAD',
    interested_plan_id TEXT DEFAULT 'professional',
    interested_brands TEXT, -- JSON array e.g. ["TOYOTA", "HONDA"]
    interested_categories TEXT, -- JSON array e.g. ["ระบบเบรก", "ระบบช่วงล่าง"]
    expected_mrr INTEGER DEFAULT 2990,
    notes TEXT,
    next_follow_up_date DATE,
    org_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_staff_id) REFERENCES users(id),
    FOREIGN KEY (org_id) REFERENCES organizations(id)
);

-- 6. Typed Cross-Reference Relationships
CREATE TABLE IF NOT EXISTS cross_reference_relations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_brand TEXT NOT NULL,
    source_part_number TEXT NOT NULL,
    target_brand TEXT NOT NULL,
    target_part_number TEXT NOT NULL,
    relation_type TEXT NOT NULL CHECK (relation_type IN ('EQUIVALENT', 'REPLACEMENT', 'CROSS_REFERENCE', 'SUPERSEDES', 'ALTERNATIVE')) DEFAULT 'EQUIVALENT',
    confidence_score REAL DEFAULT 1.0,
    verification_status TEXT CHECK (verification_status IN ('VERIFIED', 'REVIEWED', 'AI_MATCHED', 'UNVERIFIED')) DEFAULT 'VERIFIED',
    notes TEXT,
    verified_by TEXT DEFAULT 'System Master',
    verified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_brand, source_part_number, target_brand, target_part_number, relation_type)
);

-- 7. Payment Transactions & Receipts
CREATE TABLE IF NOT EXISTS payment_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER NOT NULL,
    org_id INTEGER NOT NULL,
    transaction_ref TEXT UNIQUE NOT NULL,
    payment_method TEXT NOT NULL, -- CREDIT_CARD, PROMPTPAY, BANK_TRANSFER
    amount INTEGER NOT NULL,
    currency TEXT DEFAULT 'THB',
    status TEXT NOT NULL CHECK (status IN ('SUCCESS', 'PENDING', 'FAILED', 'REFUNDED')) DEFAULT 'SUCCESS',
    gateway_response TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (org_id) REFERENCES organizations(id)
);

-- 8. Platform Audit Logs
CREATE TABLE IF NOT EXISTS platform_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    username TEXT,
    user_role TEXT,
    action TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    target_id TEXT,
    before_state TEXT,
    after_state TEXT,
    ip_address TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_leads_stage ON customer_leads(pipeline_stage);
CREATE INDEX IF NOT EXISTS idx_xref_source ON cross_reference_relations(source_brand, source_part_number);
CREATE INDEX IF NOT EXISTS idx_xref_target ON cross_reference_relations(target_brand, target_part_number);
CREATE INDEX IF NOT EXISTS idx_audit_user ON platform_audit_logs(user_id, created_at);

-- ================= SEED INITIAL RBAC & CRM DATA =================

-- Seed Roles
INSERT OR IGNORE INTO roles (id, name, portal_access, tier_level, description) VALUES
('owner', 'System Owner', '/owner', 1, 'Highest business authority. Controls MRR, CRM pipeline, pricing, plans, add-ons, and policies.'),
('super_admin', 'Super Admin', '/super-admin', 2, 'Technical platform & data authority. Controls search engine, scrapers, AI skills, and health.'),
('admin', 'Operations Admin', '/admin', 3, 'Daily business operations. Manages customer organizations, subscriptions, invoices, and support.'),
('staff_sales', 'Sales Staff', '/staff', 4, 'Sales specialist. Manages leads, pipeline, demos, and trial onboarding.'),
('staff_data', 'Data Staff', '/staff', 4, 'Automotive data specialist. Reviews scraped queue, verifies fitment, and cross-references.'),
('staff_cs', 'Customer Success', '/staff', 4, 'Customer success manager. Monitors usage health, renewals, and onboarding.'),
('staff_support', 'Support Staff', '/staff', 4, 'Technical support specialist. Resolves customer inquiries and tickets.'),
('customer_owner', 'Customer Owner', '/app', 5, 'External organization owner. Manages organization subscription and user seats.'),
('customer_member', 'Customer Member', '/app', 5, 'External organization member. Accesses parts search and cross-reference.');

-- Seed Standard Permissions
INSERT OR IGNORE INTO permissions (id, module, name, description) VALUES
('mrr.view', 'BILLING', 'View MRR & Revenue Analytics', 'Access business revenue and financial command center metrics'),
('pricing.manage', 'BILLING', 'Manage Plans & Pricing', 'Edit subscription plan pricing and commercial add-ons'),
('pipeline.manage', 'CRM', 'Manage Lead CRM Pipeline', 'Move leads through stages from Lead to Subscribed'),
('customer.manage', 'CRM', 'Manage Customer Orgs', 'Create and modify customer organization details'),
('subscription.manage', 'BILLING', 'Manage Subscriptions', 'Upgrade, downgrade, cancel, and adjust subscription items'),
('master_parts.manage', 'CATALOG', 'Manage Master Automotive Data', 'Directly edit, publish, and delete master parts database'),
('temp_parts.review', 'CATALOG', 'Review Scraped Parts Queue', 'Approve, edit, or reject scraped raw parts'),
('ai.config.manage', 'AI', 'Configure AI Models & Skills', 'Toggle domain skills and modify AI API keys'),
('scraper.manage', 'SYSTEM', 'Run & Configure Web Scrapers', 'Trigger external catalog scraping'),
('parts.search', 'SEARCH', 'Execute Parts Search', 'Search automotive parts catalog'),
('api.use', 'API', 'Access REST API', 'Make programmatic REST API calls'),
('export.use', 'SEARCH', 'Export Parts Data', 'Download CSV/Excel parts reports');

-- Map Default Permissions to Roles
INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES
-- Owner: Everything
('owner', 'mrr.view'), ('owner', 'pricing.manage'), ('owner', 'pipeline.manage'),
('owner', 'customer.manage'), ('owner', 'subscription.manage'), ('owner', 'parts.search'),
-- Super Admin: Platform & Data
('super_admin', 'master_parts.manage'), ('super_admin', 'temp_parts.review'),
('super_admin', 'ai.config.manage'), ('super_admin', 'scraper.manage'), ('super_admin', 'parts.search'),
-- Admin: Operations
('admin', 'customer.manage'), ('admin', 'pipeline.manage'), ('admin', 'subscription.manage'),
('admin', 'temp_parts.review'), ('admin', 'parts.search'),
-- Staff Sales
('staff_sales', 'pipeline.manage'), ('staff_sales', 'parts.search'),
-- Staff Data
('staff_data', 'temp_parts.review'), ('staff_data', 'parts.search'),
-- Customer
('customer_owner', 'parts.search'), ('customer_owner', 'api.use'), ('customer_owner', 'export.use'),
('customer_member', 'parts.search');

-- Link Users to Roles
INSERT OR IGNORE INTO user_roles (user_id, role_id, scope_type)
SELECT id, 'owner', 'GLOBAL' FROM users WHERE username = 'owner';

INSERT OR IGNORE INTO user_roles (user_id, role_id, scope_type)
SELECT id, 'super_admin', 'GLOBAL' FROM users WHERE username = 'superadmin';
