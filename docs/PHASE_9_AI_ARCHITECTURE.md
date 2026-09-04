# Phase 9 Architecture: AI Intelligence Layer

**Date**: September 3, 2026  
**Status**: Architecture Specification  

---

## 1. Natural Language to Grounded Parts Search Architecture

```
                    [Customer Natural Language Query]
                 "ผ้าเบรคหน้าสำหรับ Hilux Revo 2.4 ปี 2021"
                                    │
                                    ▼
                          [AI Intent Parser]
                 • Extract Entities & Vehicle Specs
                 • Normalize to Canonical Taxonomy
                                    │
                                    ▼
                      [Structured Search Parameters]
                 {
                   "category": "ระบบเบรก",
                   "part_name": "ผ้าเบรคหน้า",
                   "car_brand": "Toyota",
                   "car_model": "Hilux Revo",
                   "car_year": "2021"
                 }
                                    │
                                    ▼
                        [Entitlement Validation]
                 • Check `ai_search_enabled`
                 • Check Brand Whitelist ('Toyota' ∈ Allowed)
                 • Check Category Whitelist ('ระบบเบรก' ∈ Allowed)
                 • Check Monthly AI Credits Quota
                                    │
                                    ▼
                     [advanced_search_parts Engine]
                 • Query `master_parts` & active `temp_parts`
                 • Execute Multi-Tier Relevance Scoring
                                    │
                                    ▼
                        [Grounded Verified Data]
                 • Product 1: TRW GDB3534UT (Score: 100)
                 • Product 2: Brembo P 83 066 (Score: 95)
                                    │
                                    ▼
                        [AI Explanation & Output]
                 "พบผ้าเบรคหน้าตรงรุ่น Hilux Revo 2.4 (2021) ทั้งหมด 2 รายการ"
```

---

## 2. AI Cross-Reference & Data Matching Governance

```
                   [AI Cross-Reference Discovery]
                 Analyzes dimensions, fitment, OEM codes
                                    │
                                    ▼
                         [AI Match Candidate]
                   Status: 'AI_MATCHED' (e.g. 92%)
                                    │
                                    ▼
                     [Staff AI Review Queue]
                 /staff/ai/review (Data / AI Staff)
                                    │
                 ┌──────────────────┴──────────────────┐
                 ▼                                     ▼
            [Approve]                             [Reject]
        Reviewed by Data Staff             Record Rejection Reason
                 │                                     │
                 ▼                                     ▼
       Status: 'VERIFIED'                     Status: 'REJECTED'
   Published to Master DB                 Logged in Audit Trail
```

---

## 3. Provider Abstraction & Prompt Management

### 3.1 `AIProviderInterface`
```python
class AIProviderInterface(ABC):
    @abstractmethod
    async def generate_structured_json(
        self,
        prompt: str,
        system_instruction: str,
        schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        max_tokens: int = 1000
    ) -> Dict[str, Any]:
        pass
```
- Implemented providers: `GoogleGeminiProvider` (Primary, supports `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-1.5-flash`), `MockFallbackProvider` (Offline testing & high-resiliency fallback).

### 3.2 Prompt Registry (`ai_prompts`)
All system prompts are centralized and versioned:
1. `AI_SEARCH_INTENT` (v1.0): Extracts automotive entities (Brand, Model, Year, Category, OEM, SKU, Position).
2. `AI_XREF_MATCHER` (v1.0): Compares technical specifications and dimensions to suggest relationship type (`EQUIVALENT`, `REPLACEMENT`, `ALTERNATIVE`).
3. `AI_SEARCH_EXPLAINER` (v1.0): Grounded explanations of why a part matches a vehicle.
4. `AI_DATA_ANOMALY` (v1.0): Detects duplicate OEM codes and missing catalog attributes.

---

## 4. Controlled AI Tools Sandbox

AI models interact exclusively via pre-authorized Python tools with strict multi-tenant boundaries:
- `Tool: search_parts(brand, model, year, category)`: Gated by caller's entitlement.
- `Tool: decode_vin(vin)`: Decodes WMI/VDS specifications.
- `Tool: get_cross_references(brand, part_number)`: Retrieves existing verified relationships.
- ❌ **Prohibited**: `ExecuteSQL`, `DatabaseWrite`, `DirectTableDump`.
