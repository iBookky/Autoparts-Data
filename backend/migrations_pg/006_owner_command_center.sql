-- PostgreSQL Migration: 006_owner_command_center.sql

CREATE TABLE IF NOT EXISTS owner_alerts (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('PAYMENT_FAILURE', 'SUBSCRIPTION_EXPIRING', 'HIGH_QUOTA_USAGE', 'CHURN_RISK', 'TRIAL_EXPIRING', 'SECURITY_ANOMALY')),
    severity VARCHAR(50) NOT NULL CHECK (severity IN ('CRITICAL', 'WARNING', 'INFO')) DEFAULT 'WARNING',
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    org_id INTEGER REFERENCES organizations(id),
    target_entity_type VARCHAR(100),
    target_entity_id VARCHAR(100),
    is_dismissed INTEGER DEFAULT 0,
    action_link TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    dismissed_at TIMESTAMP WITH TIME ZONE,
    dismissed_by_user_id INTEGER
);

CREATE INDEX IF NOT EXISTS idx_search_logs_perf ON search_logs(org_id, results_count, created_at);
CREATE INDEX IF NOT EXISTS idx_invoices_perf ON invoices(org_id, status, created_at);
CREATE INDEX IF NOT EXISTS idx_subs_perf ON subscriptions(status, current_period_end);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON owner_alerts(is_dismissed, severity, created_at);
