# Unauthorized Functions & Permission Drift Audit

**Generated:** 2026-09-04 19:35:46

## 1. Executive Summary

This document records permission drifts, over-permissioning, and insecure defaults discovered during the full codebase audit.

## 2. Identified Security & Permission Anomalies

| Severity | Function / Component | Current Implementation | Expected Authoritative Behavior | Risk Analysis | Recommended Remediation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HIGH** | Header-based Auth Parameter Defaults | Several endpoints declare `x_username: Optional[str] = Header('admin')` | Missing auth headers must return `401 Unauthorized` | Unauthenticated calls could inherit admin context if run without headers | Remove `'admin'` default, enforce strict `Header(...)` with session check |
| **MEDIUM** | DB Seed Permission Drift | `role_permissions` contains historical `export.use` assigned to `org_owner` | `org_owner` must not have `export.use` | Confuses DB-level audits, although backend code explicitly blocks it | Deprecate/Delete `export.use` row from `role_permissions` in migration |
| **MEDIUM** | Client `x_user_role` Header Trust | `get_current_user` inspects `x_user_role` header | Role must be resolved strictly from DB `users.role` | Client could attempt role forgery by injecting `x_user_role: OWNER` | Lookup `users.role` in DB for the authenticated user session |
| **LOW** | Duplicate Role Identifiers | `roles` table contains both `owner`/`customer_owner` and `org_owner`/`customer_member` | Unified naming standard across platform | Redundant role records in DB | Maintain clean mapping in tenant context resolver |
