import unittest
import io
import csv
from fastapi.testclient import TestClient
from main import app
from backend.database import get_db_connection, init_db, find_matching_master_part
from backend.import_helper import parse_csv_file, resolve_import_session

client = TestClient(app)

class TestDuplicatePartsResolution(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        # Seed a master part for testing
        cursor.execute("""
            INSERT INTO master_parts (
                brand, part_number, oem_number, product_name_th, product_name_en, category,
                car_brand, car_model, year_start, year_end, cost_unit, description, notes
            ) VALUES (
                'DENSO', 'IK20', '90919-01210', 'หัวเทียน Iridium Power', 'Spark Plug Iridium', 'ระบบจุดระเบิด',
                'TOYOTA', 'VIOS', '2007', '2013', '350', 'หัวเทียนเดนโซ่แท้', 'เดิมในระบบ'
            ) ON CONFLICT (brand, part_number, oem_number, car_brand, car_model) DO UPDATE SET
                cost_unit = '350', notes = 'เดิมในระบบ'
        """)
        conn.commit()
        conn.close()

    def test_01_find_matching_master_part(self):
        # 1. Exact match (same aftermarket brand, same car brand/model, same part_number)
        match = find_matching_master_part('DENSO', 'IK20', '90919-01210', 'TOYOTA', 'VIOS')
        self.assertIsNotNone(match)
        self.assertEqual(match['brand'], 'DENSO')
        self.assertEqual(match['part_number'], 'IK20')

        # 2. Distinct aftermarket brand should NOT match (per user rule: different aftermarket brand is distinct)
        match_diff_brand = find_matching_master_part('NGK', 'IK20', '90919-01210', 'TOYOTA', 'VIOS')
        self.assertIsNone(match_diff_brand)

        # 3. Different vehicle model should NOT match
        match_diff_model = find_matching_master_part('DENSO', 'IK20', '90919-01210', 'HONDA', 'CIVIC')
        self.assertIsNone(match_diff_model)

    def test_02_import_csv_with_duplicate_detection_ask_mode(self):
        # CSV content containing 1 duplicate item (DENSO IK20 for TOYOTA VIOS) and 1 brand new item (BOSCH FR7DC for HONDA CIVIC)
        csv_rows = [
            ["แบรนด์ของสินค้า", "หมวดหมู่สินค้า", "รหัสสินค้า", "เบอร์ OEM", "ชื่อสินค้า (ไทย)", "ยี่ห้อรถ", "รุ่นรถ", "ปีเริ่มต้น", "ปีสิ้นสุด", "หน่วยราคาทุน", "หมายเหตุ"],
            ["DENSO", "ระบบจุดระเบิด", "IK20", "90919-01210", "หัวเทียน เดนโซ่ อิริเดียม ใหม่", "TOYOTA", "VIOS", "2007", "2013", "420", "ราคาใหม่จากซัพพลายเออร์"],
            ["BOSCH", "ระบบจุดระเบิด", "FR7DC", "98079-5514E", "หัวเทียน Bosch", "HONDA", "CIVIC", "2006", "2011", "120", "สินค้าใหม่"]
        ]
        
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerows(csv_rows)
        csv_bytes = out.getvalue().encode('utf-8')

        result = parse_csv_file(csv_bytes, duplicate_policy="ASK")
        self.assertTrue(result["success"])
        self.assertTrue(result["requires_resolution"])
        self.assertEqual(result["conflict_count"], 1)
        self.assertEqual(result["new_count"], 1)
        self.assertIn("session_id", result)
        
        conflict = result["conflicts"][0]
        self.assertEqual(conflict["incoming"]["part_number"], "IK20")
        self.assertEqual(conflict["existing"]["brand"], "DENSO")
        self.assertIn("cost_unit", conflict["differences"])

        # Test Overwrite resolution
        session_id = result["session_id"]
        resolve_res = resolve_import_session(session_id, [
            {"conflict_id": conflict["conflict_id"], "action": "OVERWRITE_NEW"}
        ])
        self.assertTrue(resolve_res["success"])
        self.assertEqual(resolve_res["updated_count"], 1)
        self.assertEqual(resolve_res["imported_count"], 1)

        # Verify master_parts updated without duplicating rows
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM master_parts WHERE brand = 'DENSO' AND part_number = 'IK20' AND car_brand = 'TOYOTA' AND car_model = 'VIOS'")
        rows = cursor.fetchall()
        self.assertEqual(len(rows), 1)
        updated_row = dict(rows[0])
        self.assertEqual(updated_row["cost_unit"], "420")
        self.assertEqual(updated_row["notes"], "ราคาใหม่จากซัพพลายเออร์")
        conn.close()

    def test_03_api_import_and_resolve_flow(self):
        headers = {"Authorization": "Bearer superadmin:SUPER_ADMIN"}

        # Upload CSV with duplicate
        csv_content = (
            "แบรนด์ของสินค้า,หมวดหมู่สินค้า,รหัสสินค้า,เบอร์ OEM,ชื่อสินค้า (ไทย),ยี่ห้อรถ,รุ่นรถ,ปีเริ่มต้น,ปีสิ้นสุด,หน่วยราคาทุน,หมายเหตุ\n"
            "DENSO,ระบบจุดระเบิด,IK20,90919-01210,หัวเทียน IK20,TOYOTA,VIOS,2007,2013,450,ทดสอบผ่าน API\n"
        )
        
        files = {"file": ("test_parts.csv", csv_content.encode("utf-8"), "text/csv")}
        data = {"duplicate_policy": "ASK"}
        
        res = client.post("/api/parts/import", files=files, data=data, headers=headers)
        self.assertEqual(res.status_code, 200)
        res_data = res.json()
        self.assertTrue(res_data.get("requires_resolution"))
        
        session_id = res_data.get("session_id")
        conflicts = res_data.get("conflicts", [])
        self.assertEqual(len(conflicts), 1)

        # Resolve using KEEP_EXISTING
        resolve_payload = {
            "session_id": session_id,
            "resolutions": [
                {"conflict_id": conflicts[0]["conflict_id"], "action": "KEEP_EXISTING"}
            ]
        }
        resolve_res = client.post("/api/parts/import/resolve-duplicates", json=resolve_payload, headers=headers)
        self.assertEqual(resolve_res.status_code, 200)
        resolve_json = resolve_res.json()
        self.assertTrue(resolve_json.get("success"))
        self.assertEqual(resolve_json.get("kept_count"), 1)

if __name__ == "__main__":
    unittest.main()
