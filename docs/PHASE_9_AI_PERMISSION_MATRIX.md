# Phase 9: AI Intelligence Layer Permission Matrix

**Date**: September 3, 2026  
**Status**: Authorization Specification  

---

## 1. Action Permission Matrix

| Action | Owner | Super Admin | Admin | AI Staff | Data Staff | CS Staff | Support Staff | Customer Owner | Customer Staff |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **AI_SEARCH** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Entitled) | ✅ (Entitled) |
| **AI_EXPLAIN_MATCH** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Entitled) | ✅ (Entitled) |
| **AI_RECOMMEND** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ (Entitled) | ✅ (Entitled) |
| **AI_XREF_DISCOVER**| ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **AI_REVIEW_QUEUE** | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **AI_APPROVE_MATCH**| ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **AI_REJECT_MATCH** | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **AI_MODEL_MANAGE** | ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **AI_PROMPT_MANAGE**| ❌ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **AI_USAGE_VIEW** | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ (Own Org) | ❌ |
| **AI_EVALUATE** | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
