-- =====================================================================
-- Migration 006: System Owner Business Command Center & Analytics Schema
-- =====================================================================

-- 1. Actionable Owner Business Alerts
CREATE TABLE IF NOT EXISTS owner_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    alert_type TEXT NOT NULL CHECK (alert_type IN ('PAYMENT_FAILURE', 'SUBSCRIPTION_EXPIRING', 'HIGH_QUOTA_USAGE', 'CHURN_RISK', 'TRIAL_EXPIRING', 'SECURITY_ANOMALY')),
    severity TEXT NOT NULL CHECK (severity IN ('CRITICAL', 'WARNING', 'INFO')) DEFAULT 'WARNING',
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    org_id INTEGER,
    target_entity_type TEXT,
    target_entity_id TEXT,
    is_dismissed INTEGER DEFAULT 0,
    action_link TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    dismissed_at DATETIME,
    dismissed_by_user_id INTEGER,
    FOREIGN KEY(org_id) REFERENCES organizations(id)
);

-- 2. Performance Aggregation Indexes for Owner Analytics
CREATE INDEX IF NOT EXISTS idx_search_logs_perf ON search_logs(org_id, results_count, created_at);
CREATE INDEX IF NOT EXISTS idx_invoices_perf ON invoices(org_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_subs_perf ON subscriptions(status, current_period_end);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON owner_alerts(is_dismissed, severity, created_at);
