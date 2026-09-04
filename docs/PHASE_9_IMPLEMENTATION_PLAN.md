# Phase 9 Implementation Blueprint: AI Intelligence Layer

**Date**: September 3, 2026  
**Status**: Step-by-Step Blueprint  

---

## 1. Incremental Implementation Phases

### Increment 9.1: Database Schema Migration (`009_ai_intelligence_layer.sql`)
- Create `ai_prompts` table with prompt keys, version numbers, system instructions, and active status.
- Create `ai_match_candidates` table (`id`, `source_brand`, `source_part_number`, `target_brand`, `target_part_number`, `relation_type`, `confidence_score`, `evidence_json`, `status`, `reviewed_by`, `reviewed_at`, `rejection_reason`).
- Create `ai_query_logs` table (`id`, `org_id`, `user_id`, `feature_key`, `raw_prompt`, `parsed_intent_json`, `model_name`, `tokens_used`, `latency_ms`, `grounded_result_count`).
- Seed standard prompts (`AI_SEARCH_INTENT`, `AI_XREF_MATCHER`, `AI_SEARCH_EXPLAINER`).

### Increment 9.2: Centralized AI Orchestrator & Services
- Build `backend/services/ai_intelligence_service.py`:
  - `AIProviderInterface` with `GoogleGeminiProvider` and resilient `MockFallbackProvider`.
  - `AIOrchestratorService`: Unified pipeline for authentication, entitlement gating, prompt building, model invocation, output schema validation, usage deduction, and error handling.
  - `AISearchIntentParser`: Natural language entity extraction into structured `advanced_search_parts` queries.
  - `AIMatchingAssistant`: Generates cross-reference candidate records with confidence scores and evidence.
  - `AIReviewService`: Workflow for approving/rejecting match candidates by Data Staff.

### Increment 9.3: REST API Controllers in `main.py`
- Customer AI Endpoints (`/api/saas/ai/*` & `/api/v1/ai/*`):
  - `POST /api/saas/ai/search`: Natural language AI search returning grounded parts.
  - `POST /api/saas/ai/explain`: Grounded explanation of fitment and cross-reference compatibility.
  - `GET /api/saas/ai/history`: Customer AI request history and remaining credits.
- Staff AI Operations (`/api/staff/ai/*`):
  - `GET /api/staff/ai/review-queue`: Staged `AI_MATCHED` cross-reference candidates.
  - `POST /api/staff/ai/match/{id}/approve`: Approves and transitions record to `VERIFIED` in master relations.
  - `POST /api/staff/ai/match/{id}/reject`: Rejects candidate with structured reason.
- Admin AI Configuration (`/api/admin/ai/*`):
  - Prompt registry management, model switching, latency and token metrics.

### Increment 9.4: UI Enhancements (`index.html`)
- Customer AI Search Portal (`#customer-sub-ai` & Search bar AI toggle):
  - Natural language input box with prompt suggestions.
  - Structured automotive card results with confidence and grounded data tags.
  - "Why is this a match?" AI explanation modal.
- Staff AI Review Queue (`#staff-sub-ai`):
  - Candidate comparison viewer with approval, rejection, and evidence breakdown.

### Increment 9.5: Automated Test Suite & Regression Verification
- Build `scratch/test_phase9_ai_intelligence_layer.py` covering 20 test scenarios:
  - Natural language entity extraction (Thai & English)
  - Grounding validation (ensuring zero hallucinated parts)
  - Entitlement & subscription gating (commercial lock on non-entitled plans)
  - Cross-reference candidate staging and human approval workflow
  - Multi-tenant isolation and prompt injection defense
  - Fallback resiliency when external LLM is offline
- Run full system regression across all 9 phases (**100+ automated tests passing with 100% success rate**).
