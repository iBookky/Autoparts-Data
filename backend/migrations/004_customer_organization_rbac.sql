-- 004_customer_organization_rbac.sql
-- Additive migration for Multi-Tenant Organization, Customer Users, Granular Customer Roles & Invitations

-- 1. Organization Invitations Table
CREATE TABLE IF NOT EXISTS organization_invitations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    email TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'STAFF' CHECK (role IN ('OWNER', 'MANAGER', 'STAFF')),
    invitation_token TEXT UNIQUE NOT NULL,
    status TEXT NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACCEPTED', 'EXPIRED', 'REVOKED')),
    expires_at DATETIME NOT NULL,
    created_by INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
);

-- 2. Organization Activity Audit Trail
CREATE TABLE IF NOT EXISTS organization_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    actor_user_id INTEGER NOT NULL,
    actor_username TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    action TEXT NOT NULL, -- INVITE_USER, CHANGE_ROLE, SUSPEND_USER, REACTIVATE_USER, REMOVE_USER, UPDATE_PROFILE, CREATE_API_KEY, REVOKE_API_KEY
    target_type TEXT NOT NULL, -- USER, INVITATION, ORGANIZATION, API_KEY
    target_id TEXT,
    before_state TEXT,
    after_state TEXT,
    ip_address TEXT DEFAULT '127.0.0.1',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organizations(id) ON DELETE CASCADE
);

-- 3. Seed Customer Domain Roles
INSERT OR IGNORE INTO roles (id, name, portal_access, tier_level, description) VALUES
('org_owner', 'Organization Owner', '/app', 5, 'Full administrative control over tenant team, subscription, API keys, and automotive parts data.'),
('org_manager', 'Organization Manager', '/app', 5, 'Manage organization team members, view usage analytics, and execute parts cross-references.'),
('org_staff', 'Organization Staff', '/app', 5, 'Standard search, VIN lookup, vehicle fitment, and bookmarking workspace.');

-- 4. Seed Customer Domain Permissions
INSERT OR IGNORE INTO permissions (id, module, name, description) VALUES
('organization.view', 'ORGANIZATION', 'View Organization Profile', 'View corporate profile and settings.'),
('organization.update', 'ORGANIZATION', 'Update Organization Profile', 'Edit corporate profile, tax id, address, and billing email.'),
('users.view', 'USERS', 'View Team Members', 'View list of organization users and invitation statuses.'),
('users.invite', 'USERS', 'Invite Team Members', 'Send invitation links to prospective team members.'),
('users.update_role', 'USERS', 'Change Team Member Role', 'Promote or modify roles for organization users.'),
('users.suspend', 'USERS', 'Suspend / Deactivate User', 'Temporarily suspend or disable an organization member.'),
('users.remove', 'USERS', 'Remove Member', 'Remove a user from organization membership.'),
('search.use', 'SEARCH', 'Execute Parts Search', 'Perform OEM, SKU, and keyword searches.'),
('search.vin', 'SEARCH', 'VIN Lookup Engine', 'Decode 17-digit VINs and estimate vehicle specifications.'),
('search.vehicle', 'SEARCH', 'Vehicle Fitment Search', 'Filter automotive parts by make, model, and year.'),
('search.cross_reference', 'SEARCH', 'Cross Reference Matrix', 'Access typed OE and aftermarket cross-reference relationships.'),
('parts.view', 'PARTS', 'View Product Details', 'Inspect full technical specifications and OE interchanges.'),
('parts.save', 'PARTS', 'Save & Bookmark Parts', 'Manage personal and organization saved favorites.'),
('subscription.view', 'BILLING', 'View Subscription & Invoices', 'View commercial subscription details and download tax receipts.'),
('subscription.manage', 'BILLING', 'Manage Subscription', 'Upgrade plans and add-on capacity packs.'),
('usage.view', 'BILLING', 'View Usage Analytics', 'Monitor search quotas and credit meters.'),
('api.view', 'API', 'View API Keys', 'Inspect active API credentials and rate limits.'),
('api.manage', 'API', 'Manage API Keys', 'Generate and revoke REST API keys.'),
('export.use', 'EXPORT', 'Export Catalog Data', 'Download filtered automotive parts data.'),
('audit.view', 'AUDIT', 'View Organization Audit Log', 'View chronological log of team activities.');

-- 5. Map Permissions to Customer Roles
-- Organization Owner: All Customer Permissions
INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES
('org_owner', 'organization.view'), ('org_owner', 'organization.update'),
('org_owner', 'users.view'), ('org_owner', 'users.invite'), ('org_owner', 'users.update_role'), ('org_owner', 'users.suspend'), ('org_owner', 'users.remove'),
('org_owner', 'search.use'), ('org_owner', 'search.vin'), ('org_owner', 'search.vehicle'), ('org_owner', 'search.cross_reference'),
('org_owner', 'parts.view'), ('org_owner', 'parts.save'),
('org_owner', 'subscription.view'), ('org_owner', 'subscription.manage'),
('org_owner', 'usage.view'),
('org_owner', 'api.view'), ('org_owner', 'api.manage'),
('org_owner', 'export.use'),
('org_owner', 'audit.view');

-- Organization Manager: Operations, Search, Usage, View & Invite Team
INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES
('org_manager', 'organization.view'),
('org_manager', 'users.view'), ('org_manager', 'users.invite'),
('org_manager', 'search.use'), ('org_manager', 'search.vin'), ('org_manager', 'search.vehicle'), ('org_manager', 'search.cross_reference'),
('org_manager', 'parts.view'), ('org_manager', 'parts.save'),
('org_manager', 'subscription.view'),
('org_manager', 'usage.view'),
('org_manager', 'api.view'),
('org_manager', 'export.use');

-- Organization Staff: Pure Search & Data Utilization
INSERT OR IGNORE INTO role_permissions (role_id, permission_id) VALUES
('org_staff', 'search.use'), ('org_staff', 'search.vin'), ('org_staff', 'search.vehicle'), ('org_staff', 'search.cross_reference'),
('org_staff', 'parts.view'), ('org_staff', 'parts.save');
