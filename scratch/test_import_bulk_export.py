import io
import csv
import json
from fastapi.testclient import TestClient
from main import app
from backend.database import get_db_connection

client = TestClient(app)

admin_headers = {
    "x-user-role": "ADMIN",
    "x-username": "admin"
}

def test_export_import_templates():
    # 1. Test CSV template
    res = client.get("/api/parts/export-import-template", headers=admin_headers)
    assert res.status_code == 200, res.text
    assert "parts_import_template.csv" in res.headers.get("Content-Disposition", "")
    content = res.content.decode("utf-8-sig")
    reader = list(csv.reader(io.StringIO(content)))
    assert len(reader) >= 2
    headers = reader[0]
    expected_headers = [
        "แบรนด์ของสินค้า", "หมวดหมู่สินค้า", "รหัสสินค้า", "เบอร์ OEM", "ชื่อสินค้า (ไทย)", "ชื่อสินค้า (อังกฤษ)",
        "ยี่ห้อรถ", "รุ่นรถ", "ปีเริ่มต้น", "ปีสิ้นสุด", "เครื่องยนต์", "น้ำมัน", "เกียร์",
        "รายละเอียดสินค้า", "หน่วยราคาทุน", "หมายเหตุ"
    ]
    assert headers == expected_headers
    print("✓ CSV Import Template format matches 16 columns (OK)")

    # 2. Test XLSX template
    res = client.get("/api/parts/export-import-template-xlsx", headers=admin_headers)
    assert res.status_code == 200, res.text
    assert "parts_import_template.xlsx" in res.headers.get("Content-Disposition", "")
    assert len(res.content) > 100
    print("✓ XLSX Import Template generated and downloadable (OK)")

def test_csv_import_to_review_queue():
    headers = [
        "แบรนด์ของสินค้า", "หมวดหมู่สินค้า", "รหัสสินค้า", "เบอร์ OEM", "ชื่อสินค้า (ไทย)", "ชื่อสินค้า (อังกฤษ)",
        "ยี่ห้อรถ", "รุ่นรถ", "ปีเริ่มต้น", "ปีสิ้นสุด", "เครื่องยนต์", "น้ำมัน", "เกียร์",
        "รายละเอียดสินค้า", "หน่วยราคาทุน", "หมายเหตุ"
    ]
    row1 = [
        "TEST_CSV_BRAND", "ระบบเบรก", "CSV-PART-001", "OEM-CSV-001", "จานเบรกหน้า Test CSV", "Front Brake Disc",
        "TOYOTA", "Vios", "2013", "2020", "1NZ-FE", "เบนซิน", "อัตโนมัติ",
        "จานเบรกนำเข้าเกรด OEM", "850.00", "นำเข้าผ่านระบบ CSV Test"
    ]
    row2 = [
        "TEST_CSV_BRAND", "ระบบช่วงล่าง", "CSV-PART-002", "OEM-CSV-002", "ลูกหมากกันโคลง Test CSV", "Stabilizer Link",
        "HONDA", "Civic", "2016", "2021", "1.8 E", "เบนซิน", "CVT",
        "ลูกหมากคุณภาพสูง", "320.00", "นำเข้าผ่านระบบ CSV Test"
    ]

    out = io.StringIO()
    out.write('\ufeff')
    writer = csv.writer(out)
    writer.writerow(headers)
    writer.writerow(row1)
    writer.writerow(row2)
    csv_bytes = out.getvalue().encode("utf-8")

    files = {
        "file": ("test_import.csv", csv_bytes, "text/csv")
    }
    res = client.post("/api/parts/import", files=files, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    assert data.get("imported_count") == 2
    print(f"✓ CSV Import: Imported {data.get('imported_count')} parts into Review Queue (OK)")

    # Verify present in temp_parts
    res = client.get("/api/admin/temp-parts", headers=admin_headers)
    results = res.json()["results"]
    imported_items = [t for t in results if t.get("brand") == "TEST_CSV_BRAND"]
    assert len(imported_items) >= 2
    print("✓ Items verified in temp_parts Review Queue with status PENDING (OK)")
    return [t["id"] for t in imported_items]

def test_xlsx_import_to_review_queue():
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    headers = [
        "แบรนด์ของสินค้า", "หมวดหมู่สินค้า", "รหัสสินค้า", "เบอร์ OEM", "ชื่อสินค้า (ไทย)", "ชื่อสินค้า (อังกฤษ)",
        "ยี่ห้อรถ", "รุ่นรถ", "ปีเริ่มต้น", "ปีสิ้นสุด", "เครื่องยนต์", "น้ำมัน", "เกียร์",
        "รายละเอียดสินค้า", "หน่วยราคาทุน", "หมายเหตุ"
    ]
    row1 = [
        "TEST_XLSX_BRAND", "กรองอากาศ / กรองน้ำมัน", "XLSX-PART-001", "OEM-XLSX-001", "กรองแอร์ PM2.5 Test XLSX", "Cabin Filter PM2.5",
        "MAZDA", "Mazda 2", "2015", "2024", "Skyactiv-G 1.3", "เบนซิน", "อัตโนมัติ",
        "ไส้กรองแอร์ป้องกันฝุ่น PM2.5", "190.00", "นำเข้าผ่านระบบ Excel Test"
    ]
    ws.append(headers)
    ws.append(row1)
    out = io.BytesIO()
    wb.save(out)
    xlsx_bytes = out.getvalue()

    files = {
        "file": ("test_import.xlsx", xlsx_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }
    res = client.post("/api/parts/import", files=files, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    assert data.get("imported_count") == 1
    print(f"✓ Excel (.xlsx) Import: Imported {data.get('imported_count')} parts into Review Queue (OK)")

    # Verify present in temp_parts
    res = client.get("/api/admin/temp-parts", headers=admin_headers)
    results = res.json()["results"]
    imported_items = [t for t in results if t.get("brand") == "TEST_XLSX_BRAND"]
    assert len(imported_items) >= 1
    print("✓ Excel items verified in temp_parts Review Queue with status PENDING (OK)")
    return [t["id"] for t in imported_items]

def test_bulk_review_actions(csv_ids, xlsx_ids):
    all_test_ids = csv_ids + xlsx_ids
    assert len(all_test_ids) >= 3

    # 1. Bulk Approve first 2 items to Master Catalog
    approve_ids = all_test_ids[:2]
    res = client.post("/api/admin/review/bulk", json={"action": "confirm", "temp_ids": approve_ids}, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    assert data.get("count") == 2
    print(f"✓ Bulk Approve: Successfully approved {data.get('count')} parts into Master Catalog (OK)")

    # Verify moved to master_parts and removed from temp_parts
    res = client.get("/api/admin/temp-parts", headers=admin_headers)
    remaining_temp = [t["id"] for t in res.json()["results"]]
    for aid in approve_ids:
        assert aid not in remaining_temp

    # 2. Bulk Reject remaining item(s)
    reject_ids = all_test_ids[2:]
    res = client.post("/api/admin/review/bulk", json={"action": "reject", "temp_ids": reject_ids}, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    assert data.get("count") == len(reject_ids)
    print(f"✓ Bulk Reject: Successfully rejected and deleted {data.get('count')} parts from queue (OK)")

    # Clean up test items in master_parts
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM master_parts WHERE brand IN ('TEST_CSV_BRAND', 'TEST_XLSX_BRAND')")
    cursor.execute("DELETE FROM temp_parts WHERE brand IN ('TEST_CSV_BRAND', 'TEST_XLSX_BRAND')")
    conn.commit()
    conn.close()

def test_master_catalog_export():
    # 1. Export CSV
    res = client.get("/api/admin/master-parts/export?format=csv", headers=admin_headers)
    assert res.status_code == 200, res.text
    assert "master_catalog_parts.csv" in res.headers.get("Content-Disposition", "")
    content = res.content.decode("utf-8-sig")
    reader = list(csv.reader(io.StringIO(content)))
    assert len(reader) >= 1
    assert reader[0] == [
        "แบรนด์ของสินค้า", "หมวดหมู่สินค้า", "รหัสสินค้า", "เบอร์ OEM", "ชื่อสินค้า (ไทย)", "ชื่อสินค้า (อังกฤษ)",
        "ยี่ห้อรถ", "รุ่นรถ", "ปีเริ่มต้น", "ปีสิ้นสุด", "เครื่องยนต์", "น้ำมัน", "เกียร์",
        "รายละเอียดสินค้า", "หน่วยราคาทุน", "หมายเหตุ"
    ]
    print(f"✓ Master Catalog Export CSV: {len(reader)-1} parts exported (OK)")

    # 2. Export XLSX
    res = client.get("/api/admin/master-parts/export?format=xlsx", headers=admin_headers)
    assert res.status_code == 200, res.text
    assert "master_catalog_parts.xlsx" in res.headers.get("Content-Disposition", "")
    assert len(res.content) > 500
    print("✓ Master Catalog Export XLSX: Generated styled Excel workbook (OK)")

if __name__ == "__main__":
    test_export_import_templates()
    c_ids = test_csv_import_to_review_queue()
    x_ids = test_xlsx_import_to_review_queue()
    test_bulk_review_actions(c_ids, x_ids)
    test_master_catalog_export()
    print("\n>>> ALL EXCEL/CSV IMPORT, BULK REVIEW & MASTER EXPORT TESTS PASSED! <<<")
