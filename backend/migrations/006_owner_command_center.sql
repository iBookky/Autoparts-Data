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

-- 3. Initial Seed Alerts for Owner Command Center
INSERT OR IGNORE INTO owner_alerts (id, alert_type, severity, title, message, org_id, action_link) VALUES
(1, 'HIGH_QUOTA_USAGE', 'WARNING', 'Customer approaching search limit', 'Siam Auto Supply has used 4,850 of 5,000 searches (97%). Upgrade opportunity available.', 1, '#owner-sub-opps'),
(2, 'SUBSCRIPTION_EXPIRING', 'CRITICAL', 'Subscription renewing in 3 days', 'Bangkok Fleet Logistics subscription renews on 2026-09-06. Ensure payment method is active.', 1, '#owner-sub-subs'),
(3, 'CHURN_RISK', 'WARNING', 'Low activity detected for high-value account', 'Thonburi Parts Pro has 0 searches in the past 14 days.', 1, '#owner-sub-health');

-- 4. Initial Seed Search Logs with Real-world Automotive & Zero-result queries
INSERT INTO search_logs (org_id, user_id, search_query, search_type, results_count, created_at) VALUES
(1, 1, '04465-0K360 Toyota Hilux Brake Pad', 'OEM', 4, datetime('now', '-1 hours')),
(2, 1, 'GDB3534UT TRW Brake Pad', 'SKU', 2, datetime('now', '-2 hours')),
(3, 1, '1FMCU05G15KD20101 Ford Escape', 'VIN', 1, datetime('now', '-3 hours')),
(1, 1, 'Honda Civic 2020 Oil Filter', 'VEHICLE', 3, datetime('now', '-4 hours')),
(2, 1, '04465-MISSING-PROTOTYPE', 'OEM', 0, datetime('now', '-5 hours')),
(3, 1, 'Mazda CX-5 2.2D Spark Plug 2026', 'VEHICLE', 0, datetime('now', '-6 hours')),
(1, 1, 'ISUZU-DMAX-CLUTCH-999', 'SKU', 0, datetime('now', '-7 hours')),
(1, 1, 'Toyota Vios Air Filter 17801-0M020', 'OEM', 5, datetime('now', '-8 hours')),
(2, 1, 'Mitsubishi Triton 2.5 Shock Absorber', 'VEHICLE', 6, datetime('now', '-9 hours')),
(1, 1, 'Nissan Navara NP300 Brake Disc', 'VEHICLE', 3, datetime('now', '-10 hours'));
