-- PostgreSQL Migration: 003_rbac_and_crm_pipeline.sql

CREATE TABLE IF NOT EXISTS roles (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    portal_access VARCHAR(150) NOT NULL,
    tier_level INTEGER NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS permissions (
    id VARCHAR(100) PRIMARY KEY,
    module VARCHAR(100) NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role_id VARCHAR(100) NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id VARCHAR(100) NOT NULL REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE IF NOT EXISTS user_roles (
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id VARCHAR(100) NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    scope_type VARCHAR(100) NOT NULL DEFAULT 'GLOBAL',
    scope_value TEXT,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS customer_leads (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(100),
    assigned_staff_id INTEGER REFERENCES users(id),
    pipeline_stage VARCHAR(50) NOT NULL CHECK (pipeline_stage IN ('LEAD', 'CONTACTED', 'DEMO', 'TRIAL', 'PROPOSAL', 'SUBSCRIBED', 'ACTIVE', 'CHURNED')) DEFAULT 'LEAD',
    interested_plan_id VARCHAR(100) DEFAULT 'professional',
    interested_brands TEXT,
    interested_categories TEXT,
    expected_mrr INTEGER DEFAULT 2990,
    notes TEXT,
    next_follow_up_date DATE,
    org_id INTEGER REFERENCES organizations(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS cross_reference_relations (
    id SERIAL PRIMARY KEY,
    source_brand VARCHAR(150) NOT NULL,
    source_part_number VARCHAR(150) NOT NULL,
    target_brand VARCHAR(150) NOT NULL,
    target_part_number VARCHAR(150) NOT NULL,
    relation_type VARCHAR(50) NOT NULL CHECK (relation_type IN ('EQUIVALENT', 'DIRECT_REPLACEMENT', 'SUPERSEDES', 'ALTERNATIVE')) DEFAULT 'EQUIVALENT',
    confidence_score INTEGER DEFAULT 100,
    verification_status VARCHAR(50) NOT NULL CHECK (verification_status IN ('VERIFIED', 'REVIEWED', 'AI_MATCHED', 'UNVERIFIED')) DEFAULT 'VERIFIED',
    verified_by_user_id INTEGER REFERENCES users(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_brand, source_part_number, target_brand, target_part_number, relation_type)
);

CREATE TABLE IF NOT EXISTS payment_transactions (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER,
    org_id INTEGER NOT NULL REFERENCES organizations(id),
    transaction_ref VARCHAR(255) UNIQUE NOT NULL,
    payment_method VARCHAR(50) NOT NULL CHECK (payment_method IN ('PROMPTPAY_QR', 'CREDIT_CARD', 'BANK_TRANSFER')),
    amount INTEGER NOT NULL,
    currency VARCHAR(10) DEFAULT 'THB',
    status VARCHAR(50) NOT NULL CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED', 'EXPIRED', 'REFUNDED')) DEFAULT 'PENDING',
    payment_slip_url TEXT,
    gateway_response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS platform_audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    username VARCHAR(150),
    user_role VARCHAR(50),
    action VARCHAR(150) NOT NULL,
    target_resource VARCHAR(150),
    target_id VARCHAR(150),
    details TEXT,
    ip_address VARCHAR(100),
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
