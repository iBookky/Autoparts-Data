# Phase 9 Audit: AI Intelligence Layer

**Date**: September 3, 2026  
**Status**: Pre-Implementation Discovery & Gap Analysis  

---

## 1. Executive Summary

Phase 9 designs and builds the **AI Intelligence Layer** on top of the existing automotive parts search and cross-reference platform. 

In strict adherence to the **Core AI Principles**:
- **The Automotive Parts Database remains the primary source of truth.**
- AI is a supplemental intelligence layer for natural language query interpretation, search explanation, and cross-reference discovery.
- **AI MUST NOT directly publish or overwrite production automotive data without human verification.**

---

## 2. Current AI Architecture & System Inventory

### 2.1 Current AI Capabilities Audit
1. **Existing Model Configurations (`meta_ai_models`, `ai_keys_config`)**:
   - `meta_ai_models` lists preset models (`gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-pro`, `gemini-1.5-flash`).
   - `ai_keys_config` stores provider API keys for model invocation.
   - `ai_usage_stats` tracks basic `call_count` and `tokens_used` by date.
2. **Current AI Call Pipeline (`scraper.py::call_gemini_json`)**:
   - Used as an on-demand fallback during external web scraping and VIN specification decoding when WMI/VIS rules fail.
   - **Gaps**: Hardcoded prompt strings embedded in scraper scripts; lacks an abstracted multi-provider interface (`AIProviderInterface`), versioned prompt registry (`ai_prompts`), structured schema validation, and tool-calling sandbox.
3. **Cross-Reference Status Lifecycle (`cross_reference_relations`)**:
   - Statuses: `VERIFIED`, `REVIEWED`, `AI_MATCHED`, `UNVERIFIED`.
   - AI-matched entries are already staged with `verification_status = 'AI_MATCHED'` and confidence scores (`confidence_score: 0.0 - 1.0`).

---

## 3. Search, Entitlement & Usage Integration Audit

1. **Search Integration**:
   - `advanced_search_parts` executes normalized SQL queries against `master_parts` and `temp_parts`.
   - **Gaps**: No natural language parser to transform Thai/English colloquial prompts (e.g. *"ผ้าเบรคหน้า Hilux Revo 2.4 ปี 2020"*) into structured parameters (`car_brand="Toyota"`, `car_model="Hilux Revo"`, `category="ระบบเบรก"`, `year="2020"`).
2. **Entitlement Service**:
   - `EntitlementService.validate_search_access` checks `ai_search_enabled` (on Business/Enterprise plans or via `ai_power_pack` add-on).
   - Fully ready to gate AI endpoints with commercial lock messages (`AI_NOT_ENTITLED`).
3. **Usage Records**:
   - `usage_records.ai_credits_used` tracks monthly AI consumption per organization.

---

## 4. Security Risks Identified

1. **AI Hallucination & Fake Parts Creation**: LLMs could invent non-existent OEM part numbers or incorrect fitment years if ungrounded.
2. **Prompt Injection & Data Exfiltration**: Malicious user prompts attempting to bypass multi-tenant isolation or extract other organizations' search logs or API keys.
3. **Unchecked Tool Calling**: Allowing an LLM direct database write or raw SQL execution.
4. **Runaway Provider Costs**: Unthrottled recursive LLM queries causing excessive API token bills.
