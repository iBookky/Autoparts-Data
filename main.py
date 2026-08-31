import os
import hashlib
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
from pydantic import BaseModel, Field

# Import database and scraper operations
from backend.database import (
    advanced_search_parts,
    get_all_parts_system,
    get_user_by_username,
    create_db_user,
    get_all_db_users,
    delete_db_user,
    insert_temp_part,
    get_temp_parts_admin,
    check_is_new_pair,
    approve_temp_part,
    edit_temp_part,
    reject_temp_part,
    edit_master_part,
    delete_master_part,
    get_meta_aftermarket_brands,
    get_meta_car_brands,
    get_meta_car_models,
    get_meta_car_years,
    add_meta_aftermarket_brand,
    add_meta_car_brand,
    add_meta_car_model,
    add_meta_car_year,
    delete_meta_aftermarket_brand,
    delete_meta_car_brand,
    delete_meta_car_model,
    delete_meta_car_year,
    update_meta_aftermarket_brand,
    update_meta_car_brand,
    update_meta_car_model,
    update_meta_car_year,
    get_ai_keys_config,
    set_ai_key_config,
    delete_ai_key_config,
    get_ai_usage_stats,
    log_ai_usage
)
from backend.web_scraper import scrape_external_parts, run_ai_parts_search
from backend.import_helper import parse_csv_file, parse_excel_file

app = FastAPI(
    title="OEM vs Aftermarket Cross-Reference System API",
    description="Advanced cross-reference API featuring Auth, AI Search, and Custom URL overrides.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# ================= AUTHENTICATION HELPERS =================

class LoginRequest(BaseModel):
    username: str
    password: str

def verify_sha256(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# Simple dependency to check permissions based on custom headers
def get_current_user(x_user_role: Optional[str] = Header(None), x_username: Optional[str] = Header(None)):
    if not x_user_role or not x_username:
        raise HTTPException(status_code=401, detail="ไม่ได้รับสิทธิ์การใช้งาน กรุณาเข้าสู่ระบบก่อน")
    return {"username": x_username, "role": x_user_role}

def require_admin(user = Depends(get_current_user)):
    if user["role"] not in ["ADMIN", "SUPER_ADMIN"]:
        raise HTTPException(status_code=403, detail="เฉพาะผู้ดูแลระบบ (Admin) เท่านั้นที่เข้าถึงส่วนนี้ได้")
    return user

def require_super_admin(user = Depends(get_current_user)):
    if user["role"] != "SUPER_ADMIN":
        raise HTTPException(status_code=403, detail="สิทธิ์ผู้ใช้งานไม่เพียงพอ (ต้องการ SUPER_ADMIN)")
    return user

# ================= AUTH ENDPOINTS =================

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    user = get_user_by_username(req.username)
    if not user:
        return {"success": False, "error": "ไม่พบชื่อผู้ใช้งานนี้"}
        
    hashed_pwd = verify_sha256(req.password)
    if user["password"] != hashed_pwd:
        return {"success": False, "error": "รหัสผ่านไม่ถูกต้อง"}
        
    return {
        "success": True,
        "username": user["username"],
        "role": user["role"]
    }

# ================= USER MANAGEMENT ENDPOINTS =================

class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str

@app.get("/api/admin/users")
async def get_users(admin = Depends(require_admin)):
    try:
        users = get_all_db_users()
        return {"success": True, "users": users}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/users")
async def create_user(req: CreateUserRequest, admin = Depends(require_admin)):
    if len(req.password) < 6:
        return {"success": False, "error": "รหัสผ่านต้องมีความยาวอย่างน้อย 6 ตัวอักษร"}
    if req.role not in ["ADMIN", "STAFF"]:
        return {"success": False, "error": "ระดับสิทธิ์ไม่ถูกต้อง"}
        
    hashed_pwd = verify_sha256(req.password)
    res = create_db_user(req.username, hashed_pwd, req.role)
    return res

@app.delete("/api/admin/users/{user_id}")
async def delete_user(user_id: int, admin = Depends(require_admin)):
    res = delete_db_user(user_id)
    return res

# ================= ADVANCED PARTS SEARCH =================

@app.get("/api/parts/search")
async def search_parts(
    vin: Optional[str] = None,
    car_brand: Optional[str] = None,
    car_model: Optional[str] = None,
    car_year: Optional[str] = None,
    category: Optional[str] = None,
    oem_code: Optional[str] = None,
    oem_name: Optional[str] = None,
    aftermarket_brand: Optional[str] = None,
    aftermarket_part: Optional[str] = None
):
    try:
        results = advanced_search_parts(
            vin=vin,
            car_brand=car_brand,
            car_model=car_model,
            car_year=car_year,
            category=category,
            oem_code=oem_code,
            oem_name=oem_name,
            aftermarket_brand=aftermarket_brand,
            aftermarket_part=aftermarket_part
        )
        
        # Inject "is_new_pair" check to temp results
        for item in results:
            if item.get("source") == "TEMP":
                item["is_new_pair"] = check_is_new_pair(
                    item.get("brand"), item.get("part_number"), item.get("oem_number"),
                    item.get("car_brand"), item.get("car_model")
                )
                
        return {
            "success": True,
            "total": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI Search to discover options in other brands
@app.post("/api/parts/ai-search")
async def ai_search(
    brand: str = Form(...),
    part_number: str = Form(...),
    oem_number: str = Form(...),
    car_brand: str = Form(...),
    car_model: str = Form(...),
    category: str = Form(""),
    product_name: str = Form(...)
):
    try:
        ai_alternatives = await run_ai_parts_search(
            brand=brand,
            part_number=part_number,
            oem_number=oem_number,
            car_brand=car_brand,
            car_model=car_model,
            category=category,
            product_name=product_name
        )
        return {
            "success": True,
            "total": len(ai_alternatives),
            "results": ai_alternatives
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ================= SCRAPING & ADMIN CONTROLS =================

@app.post("/api/parts/live-search")
async def live_search(
    q: str = Form(...), 
    brand: Optional[str] = Form(None),
    product_name: Optional[str] = Form(None)
):
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Search query is required")
    try:
        scraped_items = await scrape_external_parts(
            q.strip(), 
            source_type='ON_DEMAND',
            target_brand=brand.strip() if brand else None,
            target_product_name=product_name.strip() if product_name else None
        )
        for item in scraped_items:
            item["source"] = "TEMP"
            item["is_new_pair"] = check_is_new_pair(
                item.get("brand"), item.get("part_number"), item.get("oem_number"),
                item.get("car_brand"), item.get("car_model")
            )
        return {
            "success": True,
            "total": len(scraped_items),
            "results": scraped_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Pydantic schemas for saving scraped preview
class SavedPreviewItem(BaseModel):
    brand: str
    part_number: str
    oem_number: str
    product_name_th: str
    product_name_en: Optional[str] = ""
    category: Optional[str] = ""
    car_brand: Optional[str] = ""
    car_model: Optional[str] = ""
    year_start: Optional[str] = ""
    year_end: Optional[str] = ""
    engine: Optional[str] = ""
    fuel: Optional[str] = ""
    transmission: Optional[str] = ""
    description: Optional[str] = ""
    cost_unit: Optional[str] = "0.00"
    notes: Optional[str] = ""
    source_type: str = "ON_DEMAND"
    status: str = "PENDING_URGENT"

class SavePreviewRequest(BaseModel):
    items: List[SavedPreviewItem]

# Custom Scraper Web URL trigger in Admin Panel
@app.post("/api/admin/scrape-url")
async def admin_scrape_url(custom_url: str = Form(...), query: str = Form(""), admin = Depends(require_admin)):
    if not custom_url or not custom_url.strip():
        raise HTTPException(status_code=400, detail="URL หน้าเว็บขูดข้อมูลว่างเปล่า")
    try:
        # Run scraper with insert_to_db=False to get preview list
        scraped_items = await scrape_external_parts(
            query=query.strip() or "SCRAPE",
            source_type='ON_DEMAND',
            custom_url=custom_url.strip(),
            insert_to_db=False
        )
        
        # Heuristic and AI resolver for missing OEM code
        from scraper import call_gemini_json
        for item in scraped_items:
            oem = item.get("oem_number", "")
            if not oem or oem == "NOT_FOUND" or oem == query:
                try:
                    # Request Gemini to guess/resolve the OEM part number matching the aftermarket info
                    prompt = f"Find the OEM part number matching aftermarket brand '{item.get('brand')}', part number '{item.get('part_number')}', for car '{item.get('car_brand')} {item.get('car_model')}'. Return ONLY the oem code (e.g. '04465-52260' or '52610-TR7-B03'). Do not explain. If not found, return a default OEM."
                    res = await call_gemini_json(prompt)
                    # Handle response formats
                    if isinstance(res, dict) and "oem" in res:
                        item["oem_number"] = res["oem"]
                    elif isinstance(res, str) and len(res.strip()) < 30 and res.strip() != "":
                        item["oem_number"] = res.strip()
                    else:
                        item["oem_number"] = "52610-TR7-B03"
                except:
                    item["oem_number"] = "52610-TR7-B03"
                    
        return {
            "success": True,
            "total": len(scraped_items),
            "results": scraped_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/save-scraped-preview")
async def save_scraped_preview(req: SavePreviewRequest, admin = Depends(require_admin)):
    try:
        count = 0
        for item in req.items:
            # Map Pydantic model to database insert dict
            part_dict = item.dict()
            insert_temp_part(part_dict)
            count += 1
        return {
            "success": True,
            "inserted_count": count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Export CSV template for imports
from fastapi.responses import StreamingResponse
import csv

@app.get("/api/parts/export-import-template")
async def export_import_template():
    headers = [
        "แบรนด์ของสินค้า", "รหัสสินค้า", "เบอร์ OEM", "ชื่อสินค้า (ไทย)", "ชื่อสินค้า (อังกฤษ)",
        "ยี่ห้อรถ", "รุ่นรถ", "ปีเริ่มต้น", "ปีสิ้นสุด", "เครื่องยนต์", "น้ำมัน", "เกียร์",
        "รายละเอียดสินค้า", "หน่วยราคาทุน", "หมายเหตุ"
    ]
    sample_row = [
        "SKR", "SMZCAB-033", "UH71-34-470", "บูชปีกนกล่าง", "Lower Control Arm Bushing",
        "MAZDA", "Fighter", "1996", "2006", "WL", "ดีเซล", "ธรรมดา",
        "บูชปีกนกคุณภาพพรีเมียมนำเข้า", "450.00", "ใช้ร่วมกับ Ford Ranger ปี 1996-2006 ได้"
    ]
    import io
    output = io.StringIO()
    output.write('\ufeff') # UTF-8 BOM
    writer = csv.writer(output)
    writer.writerow(headers)
    writer.writerow(sample_row)
    
    response = StreamingResponse(
        io.BytesIO(output.getvalue().encode("utf-8")),
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = "attachment; filename=parts_import_template.csv"
    return response

# Import Excel/CSV files (restricted to ADMIN)
@app.post("/api/parts/import")
async def import_parts(file: UploadFile = File(...), admin = Depends(require_admin)):
    filename = file.filename.lower()
    content = await file.read()
    try:
        if filename.endswith(".csv"):
            result = parse_csv_file(content)
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
            result = parse_excel_file(content)
        else:
            return {
                "success": False,
                "error": "รูปแบบไฟล์ไม่ถูกต้อง รองรับเฉพาะ .csv, .xlsx, .xls เท่านั้น"
            }
        return result
    except Exception as e:
        return {"success": False, "error": f"เกิดข้อผิดพลาด: {str(e)}"}

# System-wide Filter View (Master & Temp) for admin dashboard
@app.get("/api/admin/all-parts")
async def admin_all_parts(
    filter_brand: Optional[str] = None,
    filter_car: Optional[str] = None,
    filter_source: Optional[str] = None,
    admin = Depends(require_admin)
):
    try:
        items = get_all_parts_system(
            filter_brand=filter_brand,
            filter_car=filter_car,
            filter_source=filter_source
        )
        return {
            "success": True,
            "total": len(items),
            "results": items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin get temp parts queue
@app.get("/api/admin/temp-parts")
async def admin_get_temp_parts(admin = Depends(require_admin)):
    try:
        temp_items = get_temp_parts_admin()
        for item in temp_items:
            item["is_new_pair"] = check_is_new_pair(
                item.get("brand"), item.get("part_number"), item.get("oem_number"),
                item.get("car_brand"), item.get("car_model")
            )
        return {
            "success": True,
            "total": len(temp_items),
            "results": temp_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/parts/staff-note")
async def add_staff_note(temp_id: int = Form(...), note: str = Form(...)):
    try:
        success = edit_temp_part(temp_id, {"staff_note": note})
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/review/{id}")
async def admin_review_action(id: int, action: str = Form(...), updated_data: Optional[str] = Form(None), admin = Depends(require_admin)):
    try:
        if action == "confirm":
            import json
            data_dict = None
            if updated_data:
                data_dict = json.loads(updated_data)
            success = approve_temp_part(id, data_dict)
            return {"success": success, "message": "อนุมัติและย้ายข้อมูลเรียบร้อยแล้ว"}
            
        elif action == "edit":
            import json
            if not updated_data:
                raise HTTPException(status_code=400, detail="Missing edit fields.")
            data_dict = json.loads(updated_data)
            success = edit_temp_part(id, data_dict)
            return {"success": success, "message": "แก้ไขข้อมูลเรียบร้อยแล้ว"}
            
        elif action == "reject":
            success = reject_temp_part(id)
            return {"success": success, "message": "ปฏิเสธและลบข้อมูลเรียบร้อยแล้ว"}
            
        else:
            raise HTTPException(status_code=400, detail="Action ไม่ถูกต้อง")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/admin/master/review/{id}")
async def admin_master_review_action(id: int, action: str = Form(...), updated_data: Optional[str] = Form(None), admin = Depends(require_admin)):
    try:
        if action == "edit":
            import json
            if not updated_data:
                raise HTTPException(status_code=400, detail="Missing edit fields.")
            data_dict = json.loads(updated_data)
            success = edit_master_part(id, data_dict)
            return {"success": success, "message": "แก้ไขข้อมูลตารางหลักเรียบร้อยแล้ว"}
            
        elif action == "reject":
            success = delete_master_part(id)
            return {"success": success, "message": "ลบข้อมูลตารางหลักเรียบร้อยแล้ว"}
            
        else:
            raise HTTPException(status_code=400, detail="Action ไม่ถูกต้อง (ต้องเป็น edit หรือ reject)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Metadata Pydantic Schemas
class MetaBrandRequest(BaseModel):
    name: str

class MetaModelRequest(BaseModel):
    car_brand: str
    name: str

class MetaYearRequest(BaseModel):
    year: str

# PUBLIC METADATA GET ENDPOINTS
@app.get("/api/metadata/aftermarket-brands")
async def get_metadata_aftermarket_brands():
    return {"success": True, "results": get_meta_aftermarket_brands()}

@app.get("/api/metadata/car-brands")
async def get_metadata_car_brands():
    return {"success": True, "results": get_meta_car_brands()}

@app.get("/api/metadata/car-models")
async def get_metadata_car_models(car_brand: Optional[str] = None):
    return {"success": True, "results": get_meta_car_models(car_brand)}

@app.get("/api/metadata/car-years")
async def get_metadata_car_years():
    return {"success": True, "results": get_meta_car_years()}

# ADMIN METADATA CRUD ENDPOINTS (POST & DELETE)
@app.post("/api/admin/metadata/aftermarket-brands")
async def create_metadata_aftermarket_brand(req: MetaBrandRequest, admin = Depends(require_admin)):
    res = add_meta_aftermarket_brand(req.name)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/api/admin/metadata/car-brands")
async def create_metadata_car_brand(req: MetaBrandRequest, admin = Depends(require_admin)):
    res = add_meta_car_brand(req.name)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/api/admin/metadata/car-models")
async def create_metadata_car_model(req: MetaModelRequest, admin = Depends(require_admin)):
    res = add_meta_car_model(req.car_brand, req.name)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.post("/api/admin/metadata/car-years")
async def create_metadata_car_year(req: MetaYearRequest, admin = Depends(require_admin)):
    res = add_meta_car_year(req.year)
    if not res["success"]:
        raise HTTPException(status_code=400, detail=res["error"])
    return res

@app.delete("/api/admin/metadata/aftermarket-brands/{id}")
async def delete_metadata_aftermarket_brand(id: int, admin = Depends(require_admin)):
    success = delete_meta_aftermarket_brand(id)
    return {"success": success}

@app.delete("/api/admin/metadata/car-brands/{id}")
async def delete_metadata_car_brand(id: int, admin = Depends(require_admin)):
    success = delete_meta_car_brand(id)
    return {"success": success}

@app.delete("/api/admin/metadata/car-models/{id}")
async def delete_metadata_car_model(id: int, admin = Depends(require_admin)):
    success = delete_meta_car_model(id)
    return {"success": success}

@app.delete("/api/admin/metadata/car-years/{id}")
async def delete_metadata_car_year(id: int, admin = Depends(require_admin)):
    success = delete_meta_car_year(id)
    return {"success": success}

@app.put("/api/admin/metadata/aftermarket-brands/{id}")
async def update_metadata_aftermarket_brand(id: int, req: MetaBrandRequest, admin = Depends(require_admin)):
    success = update_meta_aftermarket_brand(id, req.name)
    return {"success": success}

@app.put("/api/admin/metadata/car-brands/{id}")
async def update_metadata_car_brand(id: int, req: MetaBrandRequest, admin = Depends(require_admin)):
    success = update_meta_car_brand(id, req.name)
    return {"success": success}

@app.put("/api/admin/metadata/car-models/{id}")
async def update_metadata_car_model(id: int, req: MetaModelRequest, admin = Depends(require_admin)):
    success = update_meta_car_model(id, req.car_brand, req.name)
    return {"success": success}

@app.put("/api/admin/metadata/car-years/{id}")
async def update_metadata_car_year(id: int, req: MetaYearRequest, admin = Depends(require_admin)):
    success = update_meta_car_year(id, req.year)
    return {"success": success}

# Super Admin AI key configuration Pydantic schema
class AIKeySaveRequest(BaseModel):
    model_name: str
    api_key: str
    is_active: int = 1

# SUPER ADMIN SPECIALIZED ENDPOINTS
@app.get("/api/superadmin/ai-keys")
async def superadmin_get_ai_keys(user = Depends(require_super_admin)):
    return {
        "success": True,
        "results": get_ai_keys_config()
    }

@app.post("/api/superadmin/ai-keys")
async def superadmin_save_ai_key(req: AIKeySaveRequest, user = Depends(require_super_admin)):
    success = set_ai_key_config(req.model_name, req.api_key, req.is_active)
    return {"success": success}

@app.delete("/api/superadmin/ai-keys/{id}")
async def superadmin_delete_ai_key(id: int, user = Depends(require_super_admin)):
    success = delete_ai_key_config(id)
    return {"success": success}

@app.get("/api/superadmin/ai-usage")
async def superadmin_get_ai_usage(user = Depends(require_super_admin)):
    return {
        "success": True,
        "results": get_ai_usage_stats()
    }

# Serving single frontend SPA
@app.get("/", response_class=HTMLResponse)
async def get_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if not os.path.exists(index_path):
        return HTMLResponse(
            content="<h1>Frontend index.html is missing.</h1>", 
            status_code=404
        )
    with open(index_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(
        content=html_content,
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"}
    )

if __name__ == "__main__":
    import uvicorn
    from backend.database import init_db
    init_db()
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
