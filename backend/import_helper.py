import io
import csv
import uuid
import time
from typing import Dict, List, Any, Optional
from backend.database import (
    insert_temp_part,
    find_matching_master_part,
    update_master_part_from_dict,
    merge_master_part_from_dict
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
    Processes extracted rows against master catalog duplicate detection.
    duplicate_policy:
    - 'ASK' (Default): Return conflict session & side-by-side data if duplicates found.
    - 'KEEP_EXISTING': Ignore incoming changes for duplicate parts.
    - 'OVERWRITE_NEW': Overwrite existing master parts with incoming data.
    - 'MERGE': Merge incoming non-empty fields into existing master parts.
    """
    _cleanup_expired_sessions()
    
    conflicts = []
    new_items = []
    updated_count = 0
    kept_count = 0
    merged_count = 0

    fields_to_compare = [
        'brand', 'part_number', 'oem_number', 'product_name_th', 'product_name_en',
        'category', 'car_brand', 'car_model', 'year_start', 'year_end',
        'engine', 'fuel', 'transmission', 'cost_unit', 'description', 'notes'
    ]

    for part in rows:
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
                    "master_id": existing.get("id"),
                    "existing": existing,
                    "incoming": part,
                    "differences": diffs,
                    "diff_count": len(diffs),
                    "match_summary": f"แบรนด์: {part.get('brand')} | รถ: {part.get('car_brand')} {part.get('car_model')} | รหัส: {part.get('part_number') or part.get('oem_number')}"
                })
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
            else:
                try:
                    insert_temp_part(part)
                except Exception as e:
                    errors.append(f"DB error ({part.get('part_number', '')}): {str(e)}")

    if duplicate_policy == "ASK" and conflicts:
        session_id = str(uuid.uuid4())
        _IMPORT_SESSIONS[session_id] = {
            "conflicts": conflicts,
            "new_items": new_items,
            "errors": errors,
            "created_at": time.time()
        }
        return {
            "success": True,
            "requires_resolution": True,
            "session_id": session_id,
            "conflict_count": len(conflicts),
            "new_count": len(new_items),
            "conflicts": conflicts,
            "errors": errors
        }

    # If no conflicts or non-ASK policy applied
    if duplicate_policy == "ASK":
        inserted_count = 0
        for item in new_items:
            try:
                insert_temp_part(item)
                inserted_count += 1
            except Exception as e:
                errors.append(f"DB error ({item.get('part_number', '')}): {str(e)}")
        return {
            "success": True,
            "requires_resolution": False,
            "imported_count": inserted_count,
            "conflict_count": 0,
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
        "updated_count": updated_count,
        "kept_count": kept_count,
        "merged_count": merged_count,
        "errors": errors
    }


def resolve_import_session(session_id: str, resolutions: List[dict]) -> dict:
    """
    Applies user resolution decisions from the interactive modal and processes non-conflicting items.
    resolutions: list of {"conflict_id": "c_1", "action": "KEEP_EXISTING" | "OVERWRITE_NEW" | "MERGE"}
    """
    _cleanup_expired_sessions()
    session = _IMPORT_SESSIONS.pop(session_id, None)
    if not session:
        raise ValueError("Session หมดอายุหรือไม่ถูกต้อง โปรดอัปโหลดไฟล์ใหม่อีกครั้ง")

    conflicts = {c["conflict_id"]: c for c in session.get("conflicts", [])}
    new_items = session.get("new_items", [])
    errors = list(session.get("errors", []))

    kept_count = 0
    updated_count = 0
    merged_count = 0

    for res in resolutions:
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

    inserted_count = 0
    for item in new_items:
        try:
            insert_temp_part(item)
            inserted_count += 1
        except Exception as e:
            errors.append(f"New Item ({item.get('part_number', '')}): {str(e)}")

    return {
        "success": True,
        "message": f"นำเข้าข้อมูลสำเร็จ: รายการใหม่ {inserted_count} รายการ, อัปเดตข้อมูลเดิม {updated_count} รายการ, ผสานข้อมูล {merged_count} รายการ, ข้ามข้อมูลเดิม {kept_count} รายการ",
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
