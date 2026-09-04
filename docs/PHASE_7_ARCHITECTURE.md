# Phase 7 Architecture: Admin & Staff Operations Layer

**Date**: September 3, 2026  
**Status**: Architecture Specification  

---

## 1. Five-Tier System Authority Hierarchy

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           SYSTEM OWNER (/owner)                                 │
│  Commercial & Revenue Authority (MRR/ARR/ARPU, Pricing, Churn, High-level BI)  │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────┴────────────────────────────────────────┐
│                        SUPER ADMIN (/super-admin)                               │
│  Technical & Platform Authority (Infra, DB, Crawlers, Core Scrapers, AI Engine) │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────┴────────────────────────────────────────┐
│                            ADMIN (/admin)                                       │
│  Customer Operations Center (Customer 360, Leads, Trials, Renewals, Billing,    │
│  Support Tickets, Staff Task Assignments, Operational Reports)                  │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────┴────────────────────────────────────────┐
│                            STAFF (/staff)                                       │
│  Job-Specific Operational Workspaces:                                           │
│  • Sales Staff           • Customer Success Staff   • Billing Staff             │
│  • Support Staff         • Data Staff               • AI Staff                  │
│  • API Staff                                                                    │
└────────────────────────────────────────┬────────────────────────────────────────┘
                                         │
┌────────────────────────────────────────┴────────────────────────────────────────┐
│                           CUSTOMER (/app)                                       │
│  B2B Automotive Parts Search, Cross-References, Favorites, Org Team Management  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Operational Workspaces Architecture

### 2.1 Admin Workspace (`/admin`) — "Customer Operations Center"
A unified operations workspace focused on answering **"What needs attention today?"**:
1. **Today's Action Dashboard**:
   - New Leads, Expiring Trials, Upcoming Renewals, Failed Payments, Open Support Tickets, Unassigned Customers, Overdue Tasks.
2. **Customer Operations (`/admin/customers`)**:
   - Searchable, filterable organization table (Status, Plan, Health Score, Assigned Staff, Last Activity).
3. **Customer 360 Operational Profile (`/admin/customers/:id`)**:
   - Profile metadata, Subscription status & MRR, Entitlement Lock visualizer, Quota meters, Team roster, Activity timeline, Private internal notes.
4. **Lead & Pipeline Operations (`/admin/leads`)**:
   - CRM stages (`LEAD` $\rightarrow$ `CONTACTED` $\rightarrow$ `DEMO` $\rightarrow$ `TRIAL` $\rightarrow$ `PROPOSAL` $\rightarrow$ `SUBSCRIBED`), next follow-up dates, assigned salesperson.
5. **Trial Management (`/admin/trials`)**:
   - Active trial accounts, days remaining indicator, trial usage meters, trial extension workflow with mandatory audit reason logging.
6. **Proposal Generator & Tracker (`/admin/proposals`)**:
   - Proposal creation linked to `BillingCalculator`, status lifecycle (`DRAFT`, `SENT`, `VIEWED`, `ACCEPTED`, `REJECTED`, `EXPIRED`, `CANCELLED`).
7. **Subscription Operations (`/admin/subscriptions`)**:
   - Lifecycle operations (Upgrade, Downgrade, Extend Trial, Cancel, Reactivate, Suspend, Resume) routed via `SubscriptionStateMachine`.
8. **Renewal Center (`/admin/renewals`)**:
   - Operational buckets: Overdue, Due Today, Due This Week, Due This Month, Upcoming.
9. **Operational Billing (`/admin/billing`)**:
   - Failed payments queue, past-due invoices, corporate bank transfer verification, refund request processing.
10. **Support Center (`/admin/support`)**:
    - Ticket lifecycle (`OPEN`, `IN_PROGRESS`, `WAITING_CUSTOMER`, `RESOLVED`, `CLOSED`), SLA priority (`LOW`, `NORMAL`, `HIGH`, `URGENT`), category routing (`SEARCH`, `BILLING`, `DATA`, `API`, `AI`, `TECHNICAL`).
11. **Staff Task Center (`/admin/tasks`)**:
    - Task creation, assignment, priority, due date, status (`TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`), filtered queues (My Tasks, Unassigned, Overdue).
12. **Operational Reports (`/admin/reports`)**:
    - Customer acquisition, trial conversion, renewal pipeline, support SLA, staff workload.

---

### 2.2 Specialized Staff Workspaces (`/staff`)
Dynamic UI adapts strictly according to the logged-in staff member's operational sub-role:

1. **Sales Staff (`staff_sales`)**:
   - Leads queue, Trial requests, Proposal builder, Assigned tasks, Outreach activity log.
2. **Customer Success Staff (`staff_cs`)**:
   - Customer accounts, Trial onboarding, Renewal pipeline, Health scores & at-risk signals, Account check-in tasks.
3. **Billing Staff (`staff_billing`)**:
   - Invoices, Payment transactions, Failed payment retries, Bank transfer verification, Past-due account workflows.
4. **Support Staff (`staff_support`)**:
   - Support ticket queue, Customer inquiry responses, Search troubleshooting, Internal escalation notes.
5. **Data Staff (`staff_data`)**:
   - Zero-result search queue, Scraped parts verification queue (`temp_parts`), Cross-reference pairing verification, Data quality flags.
6. **AI Staff (`staff_ai`)**:
   - AI matching review queue (`AI_MATCHED` $\rightarrow$ `HUMAN_REVIEW` $\rightarrow$ `VERIFIED`), Confidence scores, AI model usage stats.
7. **API Staff (`staff_api`)**:
   - Customer API keys, Rate limits, Usage quotas, API error logs, Key revocation/rotation.

---

## 3. Database Extensions (`007_admin_and_staff_operations.sql`)

```sql
-- 1. Support Tickets
CREATE TABLE IF NOT EXISTS support_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_number TEXT UNIQUE NOT NULL,
    org_id INTEGER NOT NULL,
    customer_user_id INTEGER,
    subject TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('SEARCH', 'ACCOUNT', 'BILLING', 'SUBSCRIPTION', 'DATA', 'API', 'AI', 'TECHNICAL')),
    priority TEXT NOT NULL CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')) DEFAULT 'NORMAL',
    status TEXT NOT NULL CHECK (status IN ('OPEN', 'IN_PROGRESS', 'WAITING_CUSTOMER', 'RESOLVED', 'CLOSED')) DEFAULT 'OPEN',
    assigned_staff_id INTEGER,
    sla_due_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (org_id) REFERENCES organizations(id),
    FOREIGN KEY (customer_user_id) REFERENCES users(id),
    FOREIGN KEY (assigned_staff_id) REFERENCES users(id)
);

-- 2. Staff Operational Tasks
CREATE TABLE IF NOT EXISTS staff_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    task_type TEXT NOT NULL CHECK (task_type IN ('LEAD_FOLLOWUP', 'TRIAL_CHECKIN', 'RENEWAL_CALL', 'PAYMENT_CHASE', 'TICKET_INVESTIGATION', 'DATA_VERIFICATION', 'GENERAL')),
    priority TEXT NOT NULL CHECK (priority IN ('LOW', 'NORMAL', 'HIGH', 'URGENT')) DEFAULT 'NORMAL',
    status TEXT NOT NULL CHECK (status IN ('TODO', 'IN_PROGRESS', 'BLOCKED', 'DONE', 'CANCELLED')) DEFAULT 'TODO',
    assigned_to_user_id INTEGER,
    created_by_user_id INTEGER NOT NULL,
    related_org_id INTEGER,
    related_lead_id INTEGER,
    related_ticket_id INTEGER,
    due_date DATE,
    completed_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (assigned_to_user_id) REFERENCES users(id),
    FOREIGN KEY (created_by_user_id) REFERENCES users(id),
    FOREIGN KEY (related_org_id) REFERENCES organizations(id),
    FOREIGN KEY (related_lead_id) REFERENCES customer_leads(id),
    FOREIGN KEY (related_ticket_id) REFERENCES support_tickets(id)
);

-- 3. Commercial Proposals
CREATE TABLE IF NOT EXISTS commercial_proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_number TEXT UNIQUE NOT NULL,
    org_id INTEGER,
    lead_id INTEGER,
    plan_id TEXT NOT NULL,
    billing_interval TEXT NOT NULL DEFAULT 'MONTHLY',
    base_price INTEGER NOT NULL,
    addons_total INTEGER DEFAULT 0,
    discount_amount INTEGER DEFAULT 0,
    vat_amount INTEGER NOT NULL,
    total_amount INTEGER NOT NULL,
    valid_until DATE NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('DRAFT', 'SENT', 'VIEWED', 'ACCEPTED', 'REJECTED', 'EXPIRED', 'CANCELLED')) DEFAULT 'DRAFT',
    created_by_user_id INTEGER NOT NULL,
    custom_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organizations(id),
    FOREIGN KEY (lead_id) REFERENCES customer_leads(id),
    FOREIGN KEY (created_by_user_id) REFERENCES users(id)
);

-- 4. Centralized Internal Operational Notes
CREATE TABLE IF NOT EXISTS internal_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_entity_type TEXT NOT NULL CHECK (target_entity_type IN ('ORGANIZATION', 'LEAD', 'TICKET', 'TASK', 'SUBSCRIPTION')),
    target_entity_id TEXT NOT NULL,
    org_id INTEGER,
    author_user_id INTEGER NOT NULL,
    note_text TEXT NOT NULL,
    is_pinned INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organizations(id),
    FOREIGN KEY (author_user_id) REFERENCES users(id)
);
```
