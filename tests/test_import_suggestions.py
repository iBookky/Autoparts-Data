import unittest
import io
import csv
from fastapi.testclient import TestClient
from main import app
from backend.database import get_db_connection, init_db, add_cross_reference_relation
from backend.import_helper import (
    suggest_part_category,
    suggest_part_oem,
    parse_csv_file,
    resolve_import_session
)

client = TestClient(app)

class TestImportSuggestions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()
        conn = get_db_connection()
        cursor = conn.cursor()
        # Clean up test records
        cursor.execute("DELETE FROM master_parts WHERE part_number IN ('TEST-PAD-01', 'TEST-SHOCK-01', 'TEST-FILTER-01', 'SUG-BOSCH-01')")
        cursor.execute("DELETE FROM temp_parts WHERE part_number IN ('TEST-PAD-01', 'TEST-SHOCK-01', 'TEST-FILTER-01', 'SUG-BOSCH-01')")
        
        # Seed a master part with OEM for suggestion lookup
        cursor.execute("""
            INSERT INTO master_parts (
                brand, part_number, oem_number, product_name_th, product_name_en, category,
                car_brand, car_model, year_start, year_end, cost_unit, description, notes
            ) VALUES (
                'GENUINE', '04465-0D150', '04465-0D150', 'ผ้าเบรกแท้โตโยต้า', 'Brake Pad Genuine', 'ระบบเบรก',
                'TOYOTA', 'VIOS', '2013', '2019', '1200', 'ผ้าเบรกหน้าแท้', 'ศูนย์โตโยต้า'
            ) ON CONFLICT (brand, part_number, oem_number, car_brand, car_model) DO NOTHING
        """)
        
        # Seed cross reference relation: SUG-BOSCH-01 -> 04465-0D150
        cursor.execute("""
            INSERT INTO cross_reference_relations (
                source_brand, source_part_number, target_brand, target_part_number, relation_type, confidence_score
            ) VALUES (
                'BOSCH', 'SUG-BOSCH-01', 'GENUINE', '04465-0D150', 'EQUIVALENT', 1.0
            )
        """)
        conn.commit()
        conn.close()

    @classmethod
    def tearDownClass(cls):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM master_parts WHERE part_number IN ('TEST-PAD-01', 'TEST-SHOCK-01', 'TEST-FILTER-01', 'SUG-BOSCH-01', '04465-0D150')")
            cursor.execute("DELETE FROM temp_parts WHERE part_number IN ('TEST-PAD-01', 'TEST-SHOCK-01', 'TEST-FILTER-01', 'SUG-BOSCH-01')")
            cursor.execute("DELETE FROM cross_reference_relations WHERE source_part_number = 'SUG-BOSCH-01'")
            conn.commit()
            conn.close()
        except Exception:
            pass

    def test_01_suggest_part_category_by_keywords(self):
        # Brake
        self.assertEqual(suggest_part_category("ผ้าเบรกหน้าเกรดพรีเมียม", "Brake Pad Front"), "ระบบเบรก")
        self.assertEqual(suggest_part_category("", "Brake Disc Rotor"), "ระบบเบรก")
        
        # Shock Absorber
        self.assertEqual(suggest_part_category("โช๊คอัพแก๊สหลัง", "Rear Shock Absorber"), "โช๊คอัพ")
        
        # Filter
        self.assertEqual(suggest_part_category("ไส้กรองน้ำมันเครื่อง", "Oil Filter"), "กรองอากาศ / กรองน้ำมัน")
        self.assertEqual(suggest_part_category("กรองแอร์ PM2.5", "Cabin Air Filter"), "กรองอากาศ / กรองน้ำมัน")
        
        # Suspension
        self.assertEqual(suggest_part_category("ลูกหมากปีกนกล่าง", "Lower Ball Joint"), "ระบบช่วงล่าง")
        
        # Belts
        self.assertEqual(suggest_part_category("สายพานหน้าเครื่อง 6PK", "Serpentine Timing Belt"), "สายพาน / ลูกรอก")

    def test_02_suggest_part_oem_from_cross_reference_and_master(self):
        # 1. From cross_reference_relations table
        suggested_oem = suggest_part_oem('SUG-BOSCH-01', brand='BOSCH', car_brand='TOYOTA', car_model='VIOS')
        self.assertEqual(suggested_oem, '04465-0D150')

        # 2. Unknown part returns empty string without error (strictly optional as requested)
        unknown_oem = suggest_part_oem('RANDOM-UNKNOWN-CODE-999')
        self.assertEqual(unknown_oem, '')

    def test_03_import_dataset_with_missing_category_and_oem(self):
        # CSV missing category and missing OEM number
        csv_rows = [
            ["แบรนด์ของสินค้า", "หมวดหมู่สินค้า", "รหัสสินค้า", "เบอร์ OEM", "ชื่อสินค้า (ไทย)", "ยี่ห้อรถ", "รุ่นรถ"],
            ["BOSCH", "", "SUG-BOSCH-01", "", "ผ้าเบรกหน้า Ceramic", "TOYOTA", "VIOS"],
            ["DENSO", "", "TEST-FILTER-01", "", "กรองอากาศเครื่องยนต์", "HONDA", "CITY"]
        ]
        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerows(csv_rows)
        csv_bytes = out.getvalue().encode('utf-8')

        result = parse_csv_file(csv_bytes, duplicate_policy="ASK")
        self.assertTrue(result["success"])
        # Should require review because category and OEM were missing
        self.assertTrue(result["requires_resolution"])
        self.assertIn("session_id", result)
        self.assertIn("review_items", result)
        self.assertEqual(len(result["review_items"]), 2)

        item1 = result["review_items"][0]
        self.assertEqual(item1["part_number"], "SUG-BOSCH-01")
        self.assertTrue(item1["is_category_suggested"])
        self.assertEqual(item1["category"], "ระบบเบรก")  # Auto-suggested!
        self.assertTrue(item1["is_oem_suggested"])
        self.assertEqual(item1["oem_number"], "04465-0D150")  # Auto-suggested from cross reference!

        item2 = result["review_items"][1]
        self.assertEqual(item2["part_number"], "TEST-FILTER-01")
        self.assertTrue(item2["is_category_suggested"])
        self.assertEqual(item2["category"], "กรองอากาศ / กรองน้ำมัน")  # Auto-suggested!

        # Now test confirmation with user manual adjustments
        # Confirming person adjusts item 1 category to 'ระบบเบรกพิเศษ' and leaves item 2 OEM blank
        session_id = result["session_id"]
        resolve_res = resolve_import_session(
            session_id=session_id,
            resolutions=[],
            reviewed_items=[
                {"item_id": item1["item_id"], "category": "ระบบเบรกพิเศษ", "oem_number": "04465-0D150-MOD"},
                {"item_id": item2["item_id"], "category": "กรองอากาศ / กรองน้ำมัน", "oem_number": ""}
            ]
        )
        self.assertTrue(resolve_res["success"])
        self.assertEqual(resolve_res["imported_count"], 2)

        # Verify items saved in temp_parts with user adjusted values
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT category, oem_number FROM temp_parts WHERE part_number = 'SUG-BOSCH-01'")
        row1 = cursor.fetchone()
        self.assertIsNotNone(row1)
        self.assertEqual(row1[0], "ระบบเบรกพิเศษ")
        self.assertEqual(row1[1], "04465-0D150-MOD")

        cursor.execute("SELECT category, oem_number FROM temp_parts WHERE part_number = 'TEST-FILTER-01'")
        row2 = cursor.fetchone()
        self.assertIsNotNone(row2)
        self.assertEqual(row2[0], "กรองอากาศ / กรองน้ำมัน")
        self.assertEqual(row2[1], "")  # left blank
        conn.close()

if __name__ == '__main__':
    unittest.main()
