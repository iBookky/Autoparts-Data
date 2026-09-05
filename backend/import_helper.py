import io
import csv
from backend.database import insert_temp_part

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

def parse_csv_file(file_content: bytes) -> dict:
    """Parses a CSV file from bytes content and returns mapped dictionaries."""
    # Attempt UTF-8 with BOM first, then UTF-8, then TIS-620/Windows-874
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

    # Clean headers and map to DB fields
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
            mapped_headers.append(None) # ignore unknown columns

    imported_count = 0
    errors = []
    
    for line_idx, row in enumerate(reader, start=2):
        if not row or all(str(val).strip() == "" for val in row):
            continue # skip empty rows
        
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

        # Simple validation
        if not part_data["part_number"] and not part_data["oem_number"]:
            errors.append(f"แถวที่ {line_idx}: ไม่พบ รหัสสินค้า หรือ เบอร์ OEM")
            continue
            
        try:
            insert_temp_part(part_data)
            imported_count += 1
        except Exception as db_err:
            errors.append(f"แถวที่ {line_idx} (DB error): {str(db_err)}")

    return {
        "success": True,
        "imported_count": imported_count,
        "errors": errors
    }

def parse_excel_file(file_content: bytes) -> dict:
    """
    Parses an Excel file (.xlsx or .xls) using openpyxl.
    """
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
    
    # Map headers to DB columns
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

    imported_count = 0
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

        try:
            insert_temp_part(part_data)
            imported_count += 1
        except Exception as db_err:
            errors.append(f"แถวที่ {line_idx} (DB error): {str(db_err)}")

    return {
        "success": True,
        "imported_count": imported_count,
        "errors": errors
    }
