# Phase 6: Metric Definitions & Business Intelligence Handbook

This document provides the exact mathematical formulations, database lineage, and operational interpretation for all commercial metrics calculated in the **AutoParts Cross-Ref SaaS Platform — System Owner Business Command Center**.

---

## 1. Financial & Revenue Metrics

### 1.1 Monthly Recurring Revenue (MRR)
* **Definition**: The total normalized monthly subscription and recurring add-on revenue from all active customer accounts.
* **Database Sources**: `subscriptions s`, `plans p`, `subscription_items si`.
* **Mathematical Formula**:
  $$\text{MRR} = \sum_{s \in \text{Active Subs}} \left( \text{Monthly Base Price}(s) + \sum_{a \in \text{Recurring Add-ons}(s)} \text{Monthly Price}(a) \right)$$
* **Handling of Billing Intervals**:
  * Monthly Subscriptions: $\text{Base Price}$
  * Yearly Subscriptions: $\text{round}\left(\frac{\text{Base Price}}{12}\right)$
* **Active Status Criteria**: `status IN ('ACTIVE', 'GRACE_PERIOD', 'CANCELLED')` (Cancelled subscriptions that have not reached `current_period_end` are included until expiration).

---

### 1.2 Annual Recurring Revenue (ARR)
* **Definition**: The annualized projection of recurring revenue.
* **Mathematical Formula**:
  $$\text{ARR} = \text{MRR} \times 12$$

---

### 1.3 Average Revenue Per User/Tenant (ARPU)
* **Definition**: The average monthly recurring revenue generated per active paying organization.
* **Mathematical Formula**:
  $$\text{ARPU} = \frac{\text{Total MRR}}{\max(1, \text{Count of Active Paying Organizations})}$$

---

### 1.4 Gross & Net Realized Revenue
* **Gross Revenue**: Sum of all `total_amount` on invoices where `status = 'PAID'`.
* **Net Revenue**: Sum of all pre-tax `amount` on paid invoices minus discounts and refunds.
* **Tax Account (7% VAT)**: Sum of all `vat_amount` on paid invoices:
  $$\text{VAT Amount} = \text{Total Amount} - \frac{\text{Total Amount}}{1.07}$$

---

## 2. Customer Health & Retention Intelligence

### 2.1 Composite Customer Health Score (0–100)
* **Purpose**: Provide an explainable, multi-factor score evaluating account engagement, payment stability, and retention probability.
* **Scoring Breakdown**:

| Factor | Weight | Evaluation Criteria | Signals / Penalties |
| :--- | :---: | :--- | :--- |
| **Search Activity Recency** | 30 pts | $\bullet$ $>500$ searches: 30 pts<br>$\bullet$ $50-500$ searches: 20 pts<br>$\bullet$ $1-49$ searches: 10 pts<br>$\bullet$ 0 searches: 0 pts | "Zero search queries recorded this cycle" |
| **Quota Utilization Ratio** | 25 pts | $\bullet$ $30\% - 85\%$ quota: 25 pts (Optimal)<br>$\bullet$ $>85\%$ quota: 20 pts (Expansion Candidate)<br>$\bullet$ $5\% - 29\%$: 15 pts<br>$\bullet$ $<5\%$: 5 pts | "Low quota utilization (<5%)" |
| **Subscription & Payment** | 25 pts | $\bullet$ `ACTIVE`: 25 pts<br>$\bullet$ `GRACE_PERIOD`: 15 pts<br>$\bullet$ `PAST_DUE`: 10 pts<br>$\bullet$ `CANCELLED`: 5 pts<br>$\bullet$ `SUSPENDED`/`EXPIRED`: 0 pts | "Account in Grace Period (payment retry)" |
| **Team Engagement** | 20 pts | $\bullet$ $\ge 3$ active users: 20 pts<br>$\bullet$ 2 active users: 15 pts<br>$\bullet$ 1 user: 10 pts | Multiple team members working in workspace |

* **Health Classification**:
  * **HEALTHY** ($\ge 75$): Highly engaged, prompt payments, multi-user utilization.
  * **ATTENTION** ($50 - 74$): Moderate usage or minor billing friction.
  * **AT_RISK** ($< 50$): Zero search queries in 14 days, payment failure, or cancellation pending.

---

### 2.2 Customer Churn Rate (%)
* **Definition**: Percentage of customer subscriptions lost within the measurement period.
* **Formula**:
  $$\text{Churn Rate} = \frac{\text{Count of Churned Subscriptions}}{\max(1, \text{Active Subs} + \text{Churned Subs})} \times 100\%$$

---

## 3. Automotive Search Demand Intelligence

### 3.1 Search Success Rate (%)
* **Definition**: The proportion of customer search queries that returned at least one matching automotive part or cross-reference.
* **Formula**:
  $$\text{Search Success Rate} = \frac{\text{Searches with results\_count} > 0}{\text{Total Searches}} \times 100\%$$

---

### 3.2 Top Zero-Result Queries (Data Gap Intelligence)
* **Definition**: Distinct search terms where `results_count = 0`, aggregated by search frequency.
* **Business Utility**: Serves as direct data intelligence for the EPC catalog team to prioritize scraping, supplier data onboarding, and AI cross-referencing for missing parts.

---

### 3.3 Brand & Category Demand
* **Definition**: Aggregation of search volume and saved bookmarks categorized by vehicle brand (e.g. Toyota, Honda, Isuzu) and parts system (e.g. ระบบเบรก, ระบบกรอง, ระบบช่วงล่าง).

---

## 4. Growth & Upgrade Triggers

### 4.1 Proactive Upgrade Opportunities
* **Trigger Condition**:
  $$\frac{\text{Searches Used}}{\text{Monthly Search Quota}} \ge 0.80 \quad \text{OR} \quad \frac{\text{Active Users}}{\text{Max Users}} \ge 0.80$$
* **Recommended Actions**: Automatically maps customer to next tier (e.g. Starter $\rightarrow$ Professional $\rightarrow$ Business $\rightarrow$ Enterprise) and generates an Upgrade Pitch prompt in the Customer 360 view.
