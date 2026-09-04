# Phase 9: AI Data Governance & Safety Standard

**Date**: September 3, 2026  
**Status**: Data Governance Specification  

---

## 1. Data Verification Classification

The system enforces 5 immutable data confidence tiers:

1. **`VERIFIED` (Highest Authority)**:
   - Official OE manufacturer specifications, factory service manuals, or validated by certified Human Data Staff.
   - Grounded basis for all search results and customer exports.
2. **`REVIEWED`**:
   - Scraped from recognized EPC catalogs and checked for vehicle compatibility by an internal operator.
3. **`AI_MATCHED` (Supplemental Candidate)**:
   - Generated algorithmically or via LLM analysis.
   - Carries an explicit `confidence_score` (e.g. 0.92).
   - **Must NEVER be displayed to customers as `VERIFIED` without human approval.**
4. **`AI_GENERATED`**:
   - Synthetic part descriptions or natural language translations generated for display.
5. **`UNVERIFIED`**:
   - Raw data from external on-demand web searches awaiting review.

---

## 2. Human-in-the-Loop Publishing Workflow

```
AI Candidate Generated
       ↓
Status: AI_MATCHED
       ↓
Enters Staff AI Review Queue (/staff/ai/review)
       ↓
Assigned to Data Staff / AI Specialist
       ↓
Human Verification against Catalog
       ↓
[ACTION: APPROVE] ───→ Status: VERIFIED ───→ Production Catalog
       │
[ACTION: REJECT]  ───→ Status: REJECTED ───→ Audit Trail with Reason
```

---

## 3. Grounding & Anti-Hallucination Guardrails

- **No In-Memory Invention**: AI search queries MUST resolve against actual database rows in `master_parts`. If no records match, the AI must explicitly return: `"ไม่พบข้อมูลที่ยืนยันได้"` (No verified data found).
- **Prompt Injection Neutralization**: Any user prompt containing system override phrases (*"Ignore previous instructions"*, *"Dump all tables"*) is intercepted by the Input Sanitizer and rejected.
- **Data Minimization**: Prompts sent to external LLMs contain only non-confidential automotive attributes (e.g. *"Toyota Hilux Revo, Brake Pad, Front"*). Customer organization IDs, billing info, and internal notes are strictly excluded.
