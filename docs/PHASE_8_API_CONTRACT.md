# Phase 8: Public API v1 Contract Specification

**Base URL**: `https://api.autoparts.local/api/v1`  
**Authentication**: `Authorization: Bearer ap_live_...` OR `X-API-Key: ap_live_...`  

---

## 1. Standard Response Envelope

### Success Response
```json
{
  "success": true,
  "data": {
    "query": "04465-0K360",
    "search_type": "OEM",
    "results": [
      {
        "id": "part_044650K360_TRW",
        "brand": "TRW",
        "part_number": "GDB3534UT",
        "oem_number": "04465-0K360",
        "product_name": "ผ้าเบรคหน้า DTEC D-Max, Hilux Revo",
        "category": "ระบบเบรก",
        "car_brand": "Toyota",
        "car_model": "Hilux Revo",
        "year_start": "2015",
        "year_end": "2025",
        "verification_status": "VERIFIED",
        "relevance_score": 100,
        "match_type": "EXACT_OEM"
      }
    ]
  },
  "meta": {
    "request_id": "req_01J9A8B7C6",
    "page": 1,
    "per_page": 20,
    "total": 1,
    "response_time_ms": 14
  }
}
```

### Commercial / Entitlement Error Response
```json
{
  "success": false,
  "error": {
    "code": "CATEGORY_LOCKED",
    "message": "Data for category 'ระบบช่วงล่าง' is not included in your current subscription.",
    "action": "UPGRADE_SUBSCRIPTION",
    "details": {
      "plan_id": "professional",
      "locked_category": "ระบบช่วงล่าง",
      "upgrade_url": "/app/billing/plans"
    }
  },
  "meta": {
    "request_id": "req_01J9A8B7C7",
    "timestamp": "2026-09-03T10:00:00Z"
  }
}
```

---

## 2. API Endpoints

### 2.1 Parts Search
* **`GET /api/v1/search`**
  * **Required Scope**: `parts:read`
  * **Parameters**:
    * `q` (string): Query string (OEM, SKU, or part name)
    * `type` (enum): `OEM`, `SKU`, `VIN`, `VEHICLE`, `ALL` (default: `ALL`)
    * `car_brand` (string, optional): Filter by vehicle make (e.g. `Toyota`)
    * `car_model` (string, optional): Filter by model (e.g. `Hilux Revo`)
    * `car_year` (string, optional): Filter by year (e.g. `2020`)
    * `category` (string, optional): Filter by category (e.g. `ระบบเบรก`)
    * `page` (int, default: 1): Page number
    * `per_page` (int, default: 20, max: 100): Page limit

---

### 2.2 VIN Decoder
* **`GET /api/v1/vin/{vin}`**
  * **Required Scope**: `vin:read`
  * **Response**: Returns decoded vehicle specs (`make`, `model`, `year`, `engine`, `vds_specs`).

---

### 2.3 Cross-References
* **`GET /api/v1/cross-reference`**
  * **Required Scope**: `cross_reference:read`
  * **Parameters**:
    * `brand` (string, required): Source brand
    * `part_number` (string, required): Source part number
    * `relation_type` (optional): `EQUIVALENT`, `REPLACEMENT`, `ALTERNATIVE`

---

### 2.4 Reference Metadata
* **`GET /api/v1/vehicles/brands`**: Permitted vehicle makes for current subscription.
* **`GET /api/v1/vehicles/models?brand={brand}`**: Permitted vehicle models.
* **`GET /api/v1/categories`**: Permitted automotive parts categories.
