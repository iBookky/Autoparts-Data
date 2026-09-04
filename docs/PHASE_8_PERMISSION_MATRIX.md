# Phase 8: API & Export Permission Matrix

**Date**: September 3, 2026  
**Status**: Authorization Specification  

---

## 1. Action Permission Matrix

| Action | Owner | Super Admin | Admin | API Staff | Billing Staff | CS Staff | Support Staff | Data Staff | Customer Owner | Customer Manager | Customer Staff |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **API_VIEW** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **API_KEY_CREATE** | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **API_KEY_REVOKE** | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **API_KEY_ROTATE** | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| **API_USAGE_VIEW** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ❌ |
| **API_ERROR_VIEW** | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ |
| **API_QUERY_EXECUTE**| ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ✅ (Key-based)| ✅ (Key-based) | ✅ (Key-based) |
| **EXPORT_CREATE** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Entitled) | ✅ (Entitled)  | ✅ (Entitled)  |
| **EXPORT_VIEW** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Own Org)  | ✅ (Own Org)   | ✅ (Own Org)   |
| **EXPORT_DOWNLOAD** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Signed URL)| ✅ (Signed URL) | ✅ (Signed URL) |
| **EXPORT_CANCEL** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ (Own Org)  | ❌             | ❌             |
| **API_ADMIN_MANAGE**| ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌            | ❌             | ❌             |
