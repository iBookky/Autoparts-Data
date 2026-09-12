import io
import csv
import uuid
import time
from typing import Dict, List, Any, Optional
from backend.database import (
    insert_temp_part,
    find_matching_master_part,
    update_master_part_from_dict,
    merge_master_part_from_dict,
    get_db_connection,
    get_meta_categories
)

HEADER_MAP = {
    "แบรนด์ของสินค้า": "brand",
    "แบรนด์": "brand",
    "หมวดหมู่สินค้า": "category",
    "หมวดหมู่": "category",
    "รหัสสินค้า": "part_number",
    "เบอร์ oem": "oem_number",
    "เบอร์ OEM": "oem_number",
    "oem": "oem_number",
    "ชื่อสินค้า (ไทย)": "product_name_th",
    "ชื่อสินค้าไทย": "product_name_th",
    "ชื่อสินค้า (อังกฤษ)": "product_name_en",
    "ชื่อสินค้าอังกฤษ": "product_name_en",
    "ยี่ห้อรถ": "car_brand",
    "ยี่ห้อ": "car_brand",
    "รุ่นรถ": "car_model",
    "รุ่น": "car_model",
    "ปีเริ่มต้น": "year_start",
    "ปีสิ้นสุด": "year_end",
    "เครื่องยนต์": "engine",
    "น้ำมัน": "fuel",
    "เกียร์": "transmission",
    "รายละเอียดสินค้า": "description",
    "รายละเอียด": "description",
    "หน่วยราคาทุน": "cost_unit",
    "ราคาทุน": "cost_unit",
    "ราคา": "cost_unit",
    "หมายเหตุ": "notes",
    # English equivalents for convenience
    "brand": "brand",
    "category": "category",
    "part_number": "part_number",
    "part_no": "part_number",
    "sku": "part_number",
    "oem_number": "oem_number",
    "oem_no": "oem_number",
    "product_name_th": "product_name_th",
    "product_name_en": "product_name_en",
    "car_brand": "car_brand",
    "make": "car_brand",
    "car_model": "car_model",
    "model": "car_model",
    "year_start": "year_start",
    "year_end": "year_end",
    "engine": "engine",
    "fuel": "fuel",
    "fuel_type": "fuel",
    "transmission": "transmission",
    "description": "description",
    "cost_unit": "cost_unit",
    "cost": "cost_unit",
    "price": "cost_unit",
    "notes": "notes",
    "note": "notes"
}

# In-memory storage for active conflict resolution sessions
_IMPORT_SESSIONS: Dict[str, dict] = {}
SESSION_EXPIRY_SECONDS = 1800  # 30 minutes

CATEGORY_RULES = [
    ("ระบบเบรก", [
        "เบรก", "เบรค", "ผ้าเบรก", "ผ้าเบรค", "จานเบรก", "จานเบรค", "คาลิปเปอร์", 
        "ก้ามเบรก", "ก้ามเบรค", "น้ำมันเบรก", "กระบอกเบรก", "สายเบรก", "brake", "pad", "rotor", 
        "caliper", "disc", "drum"
    ]),
    ("โช๊คอัพ", [
        "โช๊ค", "โช้ค", "โช๊คอัพ", "โช้คอัพ", "สปริง", "เบ้าโช๊ค", "ยางกันกระแทกโช๊ค", 
        "shock", "strut", "damper", "absorber", "coil spring"
    ]),
    ("ระบบช่วงล่าง", [
        "ช่วงล่าง", "ลูกหมาก", "ปีกนก", "บูช", "บูชปีกนก", "ยางกันโคลง", "เหล็กกันโคลง", 
        "แร็ค", "เพลา", "ลูกปืนล้อ", "suspension", "ball joint", "control arm", 
        "bushing", "stabilizer", "tie rod", "rack", "wheel bearing"
    ]),
    ("กรองอากาศ / กรองน้ำมัน", [
        "กรอง", "ไส้กรอง", "กรองอากาศ", "กรองน้ำมัน", "กรองเครื่อง", "กรองเกียร์", 
        "กรองแอร์", "กรองโซล่า", "filter", "air filter", "oil filter", "cabin filter", "fuel filter"
    ]),
    ("สายพาน / ลูกรอก", [
        "สายพาน", "ลูกรอก", "ไทม์มิ่ง", "สายพานหน้าเครื่อง", "ลูกรอกสายพาน", 
        "belt", "timing belt", "v-belt", "pulley", "tensioner"
    ]),
    ("ระบบหล่อเย็น / หม้อน้ำ", [
        "หม้อน้ำ", "พัดลมหม้อน้ำ", "วาล์วน้ำ", "ปั๊มน้ำ", "ท่อยางหม้อน้ำ", "ฝาหม้อน้ำ", 
        "coolant", "radiator", "water pump", "thermostat"
    ]),
    ("ระบบเครื่องยนต์", [
        "เครื่องยนต์", "ลูกสูบ", "แหวนลูกสูบ", "ปะเก็น", "ฝาสูบ", "วาล์ว", "หัวเทียน", 
        "คอยล์", "คอยล์จุดระเบิด", "หัวฉีด", "engine", "piston", "gasket", "spark plug", "ignition coil", "injector"
    ]),
    ("ระบบส่งกำลัง / เกียร์", [
        "เกียร์", "คลัตช์", "หวีคลัตช์", "ผ้าคลัตช์", "ลูกปืนคลัตช์", "ฟลายวีล", 
        "transmission", "clutch", "gearbox", "flywheel"
    ]),
    ("ระบบไฟ / แบตเตอรี่", [
        "แบตเตอรี่", "ไดชาร์จ", "ไดสตาร์ท", "หลอดไฟ", "ไฟหน้า", "ไฟท้าย", "ฟิวส์", 
        "alternator", "starter", "battery", "headlight", "taillight", "bulb", "fuse"
    ])
]


def suggest_part_category(product_name_th: str = "", product_name_en: str = "", part_number: str = "", car_brand: str = "") -> str:
    """
    Intelligently suggests a product category based on product title keywords,
    description text, or existing catalog part numbers.
    """
    search_text = f"{product_name_th or ''} {product_name_en or ''} {part_number or ''}".lower()
    for cat_name, keywords in CATEGORY_RULES:
        for kw in keywords:
            if kw.lower() in search_text:
                return cat_name
    
    # Try looking up existing master parts with identical part_number
    pn = (part_number or "").strip().upper()
    if pn:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT category FROM master_parts WHERE UPPER(part_number) = ? AND category IS NOT NULL AND category != '' LIMIT 1",
                (pn,)
            )
            row = cursor.fetchone()
            conn.close()
            if row and row[0]:
                return row[0]
        except Exception:
            pass

    return "ระบบช่วงล่าง"


def suggest_part_oem(part_number: str = "", brand: str = "", car_brand: str = "", car_model: str = "") -> str:
    """
    Suggests genuine OEM part number by consulting:
    1. master_parts catalog (prioritizing same car make/model)
    2. cross_reference_relations table
    Returns OEM string or empty string if unknown (optional).
    """
    pn = (part_number or "").strip().upper()
    cb = (car_brand or "").strip().upper()
    cm = (car_model or "").strip().upper()
    if not pn:
        return ""

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Look in master_parts with priority for car_brand & car_model
        if cb and cm:
            cursor.execute("""
                SELECT oem_number FROM master_parts 
                WHERE UPPER(part_number) = ? AND UPPER(car_brand) = ? AND UPPER(car_model) = ?
                  AND oem_number IS NOT NULL AND oem_number != ''
                LIMIT 1
            """, (pn, cb, cm))
            row = cursor.fetchone()
            if row and row[0]:
                conn.close()
                return str(row[0]).strip()
        
        # 2. Look in master_parts for part_number only
        cursor.execute("""
            SELECT oem_number FROM master_parts 
            WHERE UPPER(part_number) = ? AND oem_number IS NOT NULL AND oem_number != ''
            LIMIT 1
        """, (pn,))
        row = cursor.fetchone()
        if row and row[0]:
            conn.close()
            return str(row[0]).strip()

        # 3. Look in cross_reference_relations
        cursor.execute("""
            SELECT target_part_number FROM cross_reference_relations
            WHERE UPPER(source_part_number) = ? AND UPPER(target_brand) IN ('GENUINE', 'OEM', ?)
            LIMIT 1
        """, (pn, cb))
        row = cursor.fetchone()
        if row and row[0]:
            conn.close()
            return str(row[0]).strip()

        cursor.execute("""
            SELECT source_part_number FROM cross_reference_relations
            WHERE UPPER(target_part_number) = ? AND UPPER(source_brand) IN ('GENUINE', 'OEM', ?)
            LIMIT 1
        """, (pn, cb))
        row = cursor.fetchone()
        if row and row[0]:
            conn.close()
            return str(row[0]).strip()

        conn.close()
    except Exception:
        pass

    return ""


def _cleanup_expired_sessions():
    now = time.time()
    expired = [sid for sid, sdata in _IMPORT_SESSIONS.items() if now - sdata.get("created_at", 0) > SESSION_EXPIRY_SECONDS]
    for sid in expired:
        _IMPORT_SESSIONS.pop(sid, None)


def extract_rows_from_csv(file_content: bytes) -> tuple[List[dict], List[str]]:
    """Parses a CSV file and extracts normalized part data rows."""
    text_content = None
    for enc in ["utf-8-sig", "utf-8", "tis-620", "windows-874", "cp874", "latin-1"]:
        try:
            text_content = file_content.decode(enc)
            break
        except (UnicodeDecodeError, LookupError):
            continue

    if text_content is None:
        text_content = file_content.decode("utf-8-sig", errors="ignore")

    reader = csv.reader(io.StringIO(text_content))
    try:
        headers = next(reader)
    except StopIteration:
        raise ValueError("ไฟล์ CSV ว่างเปล่า")

    mapped_headers = []
    for h in headers:
        cleaned_h = str(h).strip().lower()
        found = False
        for original_name, db_field in HEADER_MAP.items():
            if cleaned_h == original_name.lower():
                mapped_headers.append(db_field)
                found = True
                break
        if not found:
            mapped_headers.append(None)

    rows = []
    errors = []
    for line_idx, row in enumerate(reader, start=2):
        if not row or all(str(val).strip() == "" for val in row):
            continue

        part_data = {
            "brand": "GENUINE",
            "category": "",
            "part_number": "",
            "oem_number": "",
            "product_name_th": "อะไหล่รถยนต์",
            "product_name_en": "",
            "car_brand": "",
            "car_model": "",
            "year_start": "",
            "year_end": "",
            "engine": "",
            "fuel": "",
            "transmission": "",
            "description": "",
            "cost_unit": "",
            "notes": "",
            "source_type": "EXCEL_IMPORT",
            "status": "PENDING",
            "staff_note": ""
        }

        for col_idx, cell_value in enumerate(row):
            if col_idx < len(mapped_headers) and mapped_headers[col_idx] is not None:
                field_name = mapped_headers[col_idx]
                part_data[field_name] = str(cell_value).strip()

        if not part_data["part_number"] and not part_data["oem_number"]:
            errors.append(f"แถวที่ {line_idx}: ไม่พบ รหัสสินค้า หรือ เบอร์ OEM")
            continue

        rows.append(part_data)

    return rows, errors


def extract_rows_from_excel(file_content: bytes) -> tuple[List[dict], List[str]]:
    """Parses an Excel (.xlsx / .xls) file and extracts normalized part data rows."""
    try:
        import openpyxl
    except ImportError:
        raise ImportError("โปรดติดตั้งไลบรารี openpyxl เพื่ออัปโหลดไฟล์ Excel (.xlsx)")

    wb = openpyxl.load_workbook(io.BytesIO(file_content), read_only=True, data_only=True)
    sheet = wb.active

    rows = list(sheet.iter_rows(values_only=True))
    if not rows:
        raise ValueError("ไฟล์ Excel ว่างเปล่า")

    headers = [str(cell) if cell is not None else "" for cell in rows[0]]
    mapped_headers = []
    for h in headers:
        cleaned_h = h.strip().lower()
        found = False
        for original_name, db_field in HEADER_MAP.items():
            if cleaned_h == original_name.lower():
                mapped_headers.append(db_field)
                found = True
                break
        if not found:
            mapped_headers.append(None)

    extracted_rows = []
    errors = []

    for line_idx, row in enumerate(rows[1:], start=2):
        if not row or all(cell is None or str(cell).strip() == "" for cell in row):
            continue

        part_data = {
            "brand": "GENUINE",
            "category": "",
            "part_number": "",
            "oem_number": "",
            "product_name_th": "อะไหล่รถยนต์",
            "product_name_en": "",
            "car_brand": "",
            "car_model": "",
            "year_start": "",
            "year_end": "",
            "engine": "",
            "fuel": "",
            "transmission": "",
            "description": "",
            "cost_unit": "",
            "notes": "",
            "source_type": "EXCEL_IMPORT",
            "status": "PENDING",
            "staff_note": ""
        }

        for col_idx, cell_value in enumerate(row):
            if col_idx < len(mapped_headers) and mapped_headers[col_idx] is not None:
                field_name = mapped_headers[col_idx]
                part_data[field_name] = str(cell_value).strip() if cell_value is not None else ""

        if not part_data["part_number"] and not part_data["oem_number"]:
            errors.append(f"แถวที่ {line_idx}: ไม่พบ รหัสสินค้า หรือ เบอร์ OEM")
            continue

        extracted_rows.append(part_data)

    return extracted_rows, errors


def process_import_dataset(rows: List[dict], errors: List[str], duplicate_policy: str = "ASK") -> dict:
    """
    Processes extracted rows against master catalog duplicate detection and auto-suggests missing category/OEM.
    duplicate_policy:
    - 'ASK' (Default): Return conflict/review session & interactive data if duplicates or suggestions found.
    - 'KEEP_EXISTING': Ignore incoming changes for duplicate parts.
    - 'OVERWRITE_NEW': Overwrite existing master parts with incoming data.
    - 'MERGE': Merge incoming non-empty fields into existing master parts.
    """
    _cleanup_expired_sessions()
    
    conflicts = []
    new_items = []
    review_items = []
    updated_count = 0
    kept_count = 0
    merged_count = 0

    fields_to_compare = [
        'brand', 'part_number', 'oem_number', 'product_name_th', 'product_name_en',
        'category', 'car_brand', 'car_model', 'year_start', 'year_end',
        'engine', 'fuel', 'transmission', 'cost_unit', 'description', 'notes'
    ]

    for idx, part in enumerate(rows):
        item_id = f"item_{idx + 1}"
        part["item_id"] = item_id

        # 1. Check and suggest Category if missing
        raw_cat = (part.get("category") or "").strip()
        if not raw_cat:
            suggested_cat = suggest_part_category(
                part.get("product_name_th", ""),
                part.get("product_name_en", ""),
                part.get("part_number", ""),
                part.get("car_brand", "")
            )
            part["category"] = suggested_cat
            part["is_category_suggested"] = True
        else:
            part["is_category_suggested"] = False

        # 2. Check and suggest OEM Number if missing
        raw_oem = (part.get("oem_number") or "").strip()
        if not raw_oem:
            suggested_oem = suggest_part_oem(
                part.get("part_number", ""),
                part.get("brand", ""),
                part.get("car_brand", ""),
                part.get("car_model", "")
            )
            part["oem_number"] = suggested_oem
            part["is_oem_suggested"] = True
        else:
            part["is_oem_suggested"] = False

        needs_review = part["is_category_suggested"] or part["is_oem_suggested"]

        existing = find_matching_master_part(
            part.get("brand", ""),
            part.get("part_number", ""),
            part.get("oem_number", ""),
            part.get("car_brand", ""),
            part.get("car_model", "")
        )

        if existing:
            # Found exact duplicate matching brand, vehicle make/model, and code
            diffs = {}
            for f in fields_to_compare:
                ex_val = str(existing.get(f) or "").strip()
                in_val = str(part.get(f) or "").strip()
                if ex_val != in_val:
                    diffs[f] = {"existing": ex_val, "incoming": in_val}

            if duplicate_policy == "ASK":
                conflict_id = f"c_{len(conflicts) + 1}"
                conflicts.append({
                    "conflict_id": conflict_id,
                    "item_id": item_id,
                    "master_id": existing.get("id"),
                    "existing": existing,
                    "incoming": part,
                    "differences": diffs,
                    "diff_count": len(diffs),
                    "match_summary": f"แบรนด์: {part.get('brand')} | รถ: {part.get('car_brand')} {part.get('car_model')} | รหัส: {part.get('part_number') or part.get('oem_number')}"
                })
                if needs_review:
                    review_items.append(part)
            elif duplicate_policy == "KEEP_EXISTING":
                kept_count += 1
            elif duplicate_policy == "OVERWRITE_NEW":
                update_master_part_from_dict(existing["id"], part)
                updated_count += 1
            elif duplicate_policy == "MERGE":
                merge_master_part_from_dict(existing["id"], part)
                merged_count += 1
        else:
            if duplicate_policy == "ASK":
                new_items.append(part)
                if needs_review:
                    review_items.append(part)
            else:
                try:
                    clean_item = {k: v for k, v in part.items() if k not in ("item_id", "is_category_suggested", "is_oem_suggested")}
                    insert_temp_part(clean_item)
                except Exception as e:
                    errors.append(f"DB error ({part.get('part_number', '')}): {str(e)}")

    if duplicate_policy == "ASK" and (conflicts or review_items):
        session_id = str(uuid.uuid4())
        _IMPORT_SESSIONS[session_id] = {
            "conflicts": conflicts,
            "new_items": new_items,
            "review_items": review_items,
            "errors": errors,
            "created_at": time.time()
        }
        meta_cats = []
        try:
            meta_cats = [c.get("name") for c in get_meta_categories() if c.get("name")]
        except Exception:
            meta_cats = [
                "ระบบเบรก", "ระบบช่วงล่าง", "กรองอากาศ / กรองน้ำมัน", "โช๊คอัพ",
                "สายพาน / ลูกรอก", "ระบบหล่อเย็น / หม้อน้ำ", "ระบบเครื่องยนต์",
                "ระบบส่งกำลัง / เกียร์", "ระบบไฟ / แบตเตอรี่"
            ]

        return {
            "success": True,
            "requires_resolution": True,
            "session_id": session_id,
            "conflict_count": len(conflicts),
            "new_count": len(new_items),
            "review_count": len(review_items),
            "conflicts": conflicts,
            "review_items": review_items,
            "categories": meta_cats,
            "errors": errors,
            "message": "พบรายการที่ระบบแนะนำหมวดหมู่ หรือ OEM อะไหล่แท้ โปรดตรวจสอบและยืนยันก่อนบันทึก"
        }

    # If no conflicts and no review items needed under ASK policy
    if duplicate_policy == "ASK":
        inserted_count = 0
        for item in new_items:
            try:
                clean_item = {k: v for k, v in item.items() if k not in ("item_id", "is_category_suggested", "is_oem_suggested")}
                insert_temp_part(clean_item)
                inserted_count += 1
            except Exception as e:
                errors.append(f"DB error ({item.get('part_number', '')}): {str(e)}")
        return {
            "success": True,
            "requires_resolution": False,
            "imported_count": inserted_count,
            "conflict_count": 0,
            "review_count": 0,
            "updated_count": 0,
            "kept_count": 0,
            "merged_count": 0,
            "errors": errors
        }

    return {
        "success": True,
        "requires_resolution": False,
        "imported_count": len(rows) - (kept_count + updated_count + merged_count),
        "conflict_count": kept_count + updated_count + merged_count,
        "review_count": len(review_items),
        "updated_count": updated_count,
        "kept_count": kept_count,
        "merged_count": merged_count,
        "errors": errors
    }


def resolve_import_session(
    session_id: str,
    resolutions: Optional[List[dict]] = None,
    reviewed_items: Optional[List[dict]] = None
) -> dict:
    """
    Applies user resolution decisions and custom review choices (category/OEM edits)
    from the interactive modal and processes non-conflicting items.
    """
    _cleanup_expired_sessions()
    session = _IMPORT_SESSIONS.pop(session_id, None)
    if not session:
        raise ValueError("Session หมดอายุหรือไม่ถูกต้อง โปรดอัปโหลดไฟล์ใหม่อีกครั้ง")

    conflicts = {c["conflict_id"]: c for c in session.get("conflicts", [])}
    new_items = session.get("new_items", [])
    errors = list(session.get("errors", []))

    # 1. Apply reviewed/adjusted category and OEM numbers
    if reviewed_items:
        rev_map = {str(item.get("item_id")): item for item in reviewed_items if item.get("item_id")}
        for item in new_items:
            iid = str(item.get("item_id", ""))
            if iid in rev_map:
                rev = rev_map[iid]
                if "category" in rev and rev["category"] is not None:
                    item["category"] = str(rev["category"]).strip()
                if "oem_number" in rev and rev["oem_number"] is not None:
                    item["oem_number"] = str(rev["oem_number"]).strip()

        for conf in conflicts.values():
            inc = conf.get("incoming", {})
            iid = str(inc.get("item_id", ""))
            if iid in rev_map:
                rev = rev_map[iid]
                if "category" in rev and rev["category"] is not None:
                    inc["category"] = str(rev["category"]).strip()
                if "oem_number" in rev and rev["oem_number"] is not None:
                    inc["oem_number"] = str(rev["oem_number"]).strip()

    kept_count = 0
    updated_count = 0
    merged_count = 0

    # 2. Process duplicate conflicts resolutions
    for res in (resolutions or []):
        cid = res.get("conflict_id")
        action = res.get("action", "KEEP_EXISTING").upper()
        conflict = conflicts.get(cid)
        if not conflict:
            continue

        master_id = conflict["master_id"]
        incoming = conflict["incoming"]

        try:
            if action == "OVERWRITE_NEW":
                update_master_part_from_dict(master_id, incoming)
                updated_count += 1
            elif action == "MERGE":
                merge_master_part_from_dict(master_id, incoming)
                merged_count += 1
            else:  # KEEP_EXISTING
                kept_count += 1
        except Exception as e:
            errors.append(f"Master ID {master_id}: {str(e)}")

    # 3. Insert non-conflicting new items
    inserted_count = 0
    for item in new_items:
        try:
            clean_item = {k: v for k, v in item.items() if k not in ("item_id", "is_category_suggested", "is_oem_suggested")}
            insert_temp_part(clean_item)
            inserted_count += 1
        except Exception as e:
            errors.append(f"New Item ({item.get('part_number', '')}): {str(e)}")

    msg_parts = []
    if inserted_count:
        msg_parts.append(f"รายการใหม่ {inserted_count} รายการ")
    if updated_count:
        msg_parts.append(f"อัปเดตข้อมูลเดิม {updated_count} รายการ")
    if merged_count:
        msg_parts.append(f"ผสานข้อมูล {merged_count} รายการ")
    if kept_count:
        msg_parts.append(f"ข้ามข้อมูลเดิม {kept_count} รายการ")
    msg_str = ", ".join(msg_parts) if msg_parts else "ดำเนินการเสร็จสิ้น"

    return {
        "success": True,
        "message": f"นำเข้าข้อมูลสำเร็จ: {msg_str}",
        "imported_count": inserted_count,
        "updated_count": updated_count,
        "merged_count": merged_count,
        "kept_count": kept_count,
        "errors": errors
    }



def parse_csv_file(file_content: bytes, duplicate_policy: str = "ASK") -> dict:
    """Parses a CSV file from bytes content and runs duplicate detection."""
    rows, errors = extract_rows_from_csv(file_content)
    return process_import_dataset(rows, errors, duplicate_policy)


def parse_excel_file(file_content: bytes, duplicate_policy: str = "ASK") -> dict:
    """Parses an Excel file (.xlsx or .xls) and runs duplicate detection."""
    rows, errors = extract_rows_from_excel(file_content)
    return process_import_dataset(rows, errors, duplicate_policy)
