# Phase 10: Production Architecture & Hardening Specification

**Date**: September 3, 2026  
**Status**: Production Architecture Blueprint  

---

## 1. Multi-Layer Production Defense Pipeline

```
                                  [Incoming Request]
                                          │
                                          ▼
                             [Security Headers & CORS Guard]
                             • HSTS, CSP, X-Content-Type-Options
                             • Domain-restricted CORS
                                          │
                                          ▼
                             [Rate Limiter & Brute-Force Guard]
                             • Sliding-window per IP & API Key
                             • Lockout after 5 failed login attempts
                                          │
                                          ▼
                            [Cryptographic Authentication]
                             • Signed Bearer JWT / API Key SHA-256
                             • Server-Side User & Organization Lookup
                                          │
                                          ▼
                            [RBAC & Scope Authorization]
                             • Role Verification from Database
                             • Entitlement Whitelisting (Brands/Categories)
                             • Quota & Subscription Status Check
                                          │
                                          ▼
                           [Input Validation & Anti-Injection]
                             • Pydantic Type Checking
                             • Parameter Sanitization & Normalization
                                          │
                                          ▼
                            [Authoritative Search & Services]
                             • `advanced_search_parts`
                             • Multi-tier relevance ranking
                             • AI Sandbox (Grounding & Human Review)
                                          │
                                          ▼
                             [DTO Sanitization & Audit Log]
                             • Strip internal IDs & supplier costs
                             • Append-only Platform Audit Trail
```

---

## 2. Production Database Hardening

1. **Connection Optimizations**:
   - `PRAGMA journal_mode = WAL;` (Enables concurrent reads and writes).
   - `PRAGMA synchronous = NORMAL;` (Maximizes write performance while maintaining durability).
   - `PRAGMA foreign_keys = ON;` (Guarantees relational integrity on cascade and constraints).
   - `PRAGMA busy_timeout = 5000;` (Eliminates database locked concurrency errors).
2. **Automated Backup Strategy**:
   - Daily automated vacuum and snapshot backup (`backups/parts_cross_ref_YYYYMMDD.db.bak`).
   - Rolling 30-day retention with verification checksums (SHA-256).
   - Recovery Point Objective (RPO): 24 Hours.
   - Recovery Time Objective (RTO): < 15 Minutes.
