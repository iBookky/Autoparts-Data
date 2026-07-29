import os
import json
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv

load_dotenv()

# File names
CREDS_FILE = "service_account.json"
MOCK_FILE = "local_sheets_mock.json"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_absolute_path(filename: str) -> str:
    if not filename:
        return ""
    if os.path.isabs(filename):
        return filename
    return os.path.abspath(os.path.join(BASE_DIR, filename))

# Column configuration
HEADERS = [
    "แบรนด์ของสินค้า", 
    "รหัสสินค้า", 
    "เบอร์ OEM", 
    "ชื่อสินค้า (ไทย)", 
    "ชื่อสินค้า (อังกฤษ)", 
    "ยี่ห้อรถ", 
    "รุ่นรถ", 
    "ปีเริ่มต้น", 
    "ปีสิ้นสุด", 
    "เครื่องยนต์", 
    "น้ำมัน", 
    "เกียร์", 
    "รายละเอียดสินค้า", 
    "หน่วยราคาทุน", 
    "หมายเหตุ"
]

def load_local_mock() -> dict:
    """Loads local mock data. If doesn't exist, initializes it with sample data."""
    mock_path = get_absolute_path(MOCK_FILE)
    if not os.path.exists(mock_path):
        sample_data = {
            "Sheet1": [
                {
                    "แบรนด์ของสินค้า": "GENUINE",
                    "รหัสสินค้า": "52610-TR7-B03",
                    "เบอร์ OEM": "52610-TR7-B03",
                    "ชื่อสินค้า (ไทย)": "โช๊คอัพหลังขวา",
                    "ยี่ห้อรถ": "HONDA",
                    "รุ่นรถ": "Civic FB",
                    "ปีเริ่มต้น": "2012",
                    "ปีสิ้นสุด": "2016",
                    "เครื่องยนต์": "R18Z",
                    "น้ำมัน": "เบนซิน",
                    "เกียร์": "อัตโนมัติ",
                    "รายละเอียดสินค้า": "โช๊คอัพแก๊สแท้ศูนย์ สเปคแสตนดาร์ด"
                },
                {
                    "แบรนด์ของสินค้า": "KYB",
                    "รหัสสินค้า": "333462",
                    "เบอร์ OEM": "52610-TR7-B03",
                    "ชื่อสินค้า (ไทย)": "โช๊คอัพหลังขวา",
                    "ยี่ห้อรถ": "HONDA",
                    "รุ่นรถ": "Civic FB",
                    "ปีเริ่มต้น": "2012",
                    "ปีสิ้นสุด": "2016",
                    "เครื่องยนต์": "R18Z",
                    "น้ำมัน": "เบนซิน",
                    "เกียร์": "อัตโนมัติ",
                    "รายละเอียดสินค้า": "KYB Excel-G ปรับจูนพิเศษเพื่อความนุ่มนวล"
                }
            ],
            "brands": [
                "LUCAS", "DENSO", "AISIN", "BOSCH", "NGK", "VALEO", "GMB", "EXEDY", "GATES", "GSP",
                "555 (Three Five)", "TRW", "CTR", "333 / CJ", "RBI", "POP (ชลิต อินดัสทรี)", "MOTIF",
                "KYB (Kayaba)", "TOKICO", "MONROE", "ZF (ZF Aftermarket)", "BC RACING", "PROFENDER",
                "TEIN", "BREMBO", "BENDIX", "COMPACT BRAKE", "AKEBONO", "MIG (MIG BRAKE)", "NIBK",
                "GIRLING", "TIMKEN", "LUCAS (ระบบลูกปืน)", "NSK", "KOYO", "NTN", "SKF", "WIX FILTERS",
                "SAKURA", "K&N", "ACDELCO", "GS", "FB", "PANASONIC", "AMARON", "PTT Lubricants (ปตท.)",
                "Bangchak (บางจาก)", "Pulzar (เพลซาร์)", "Shell (เชลล์)", "Castrol (คาสตรอล)",
                "Mobil 1 (โมบิล วัน)", "Caltex (คาลเท็กซ์)", "TotalEnergies (โททาลเอนเนอร์ยี่ส์)",
                "Motul (โมตุล)", "Liqui Moly (ลิควิ โมลี่)", "Amsoil (แอมซอยล์)", "Sunoco (ซูโนโก้)"
            ],
            "temp": []
        }
        try:
            with open(mock_path, "w", encoding="utf-8") as f:
                json.dump(sample_data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error creating local mock file: {e}")
            return sample_data
    try:
        with open(mock_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading local mock file: {e}")
        return {}

def save_local_mock(data: dict):
    """Saves data back to the local mock file."""
    try:
        with open(get_absolute_path(MOCK_FILE), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Error saving local mock: {e}")

def parse_single_year(val) -> int:
    if not val:
        return 0
    val_str = str(val).strip()
    nums = re.findall(r'\b\d{4}\b', val_str)
    if nums:
        y = int(nums[0])
        if y > 2400:
            y -= 543
        return y
    nums2 = re.findall(r'\b\d{2}\b', val_str)
    if nums2:
        y2 = int(nums2[0])
        return (2000 + y2) if y2 < 50 else (1900 + y2)
    return 0

def parse_year_range(start_val: str, end_val: str) -> tuple[int, int]:
    s_str = str(start_val or "").strip()
    e_str = str(end_val or "").strip()

    s_nums = [int(n) - 543 if int(n) > 2400 else int(n) for n in re.findall(r'\b\d{4}\b', s_str)]
    e_nums = [int(n) - 543 if int(n) > 2400 else int(n) for n in re.findall(r'\b\d{4}\b', e_str)]

    y_start = 1900
    y_end = 2099

    if s_nums:
        y_start = s_nums[0]
        if len(s_nums) > 1:
            y_end = s_nums[1]

    if e_nums:
        y_end = e_nums[0]

    if any(k in e_str.upper() or k in s_str.upper() for k in ["ปัจจุบัน", "PRESENT", "ON", "ONWARD", "+", "NOW"]):
        y_end = 2099

    return y_start, y_end

class SheetsHelper:
    def __init__(self):
        self.sheet_id = os.environ.get("GOOGLE_SHEET_ID")
        self.use_mock = False
        self.client = None
        self.spreadsheet = None
        self._brands_cache = None

        if not self.sheet_id:
            print("[SheetsHelper] WARNING: GOOGLE_SHEET_ID is not configured in environment. Using Local Mock Mode.")
            self.use_mock = True
            return

        service_account_json_str = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        service_account_file = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", CREDS_FILE)
        scope = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
        creds = None

        if service_account_json_str:
            try:
                creds_dict = json.loads(service_account_json_str)
                creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
                print("[SheetsHelper] Loaded credentials from GOOGLE_SERVICE_ACCOUNT_JSON environment variable.")
            except Exception as e:
                print(f"[SheetsHelper] Failed to load credentials from GOOGLE_SERVICE_ACCOUNT_JSON string: {e}")

        if not creds and service_account_file and os.path.exists(service_account_file):
            try:
                creds = ServiceAccountCredentials.from_json_keyfile_name(service_account_file, scope)
                print(f"[SheetsHelper] Loaded credentials from file: {service_account_file}")
            except Exception as e:
                print(f"[SheetsHelper] Failed to load credentials from file {service_account_file}: {e}")

        # If Service Account creds not loaded, try Google OAuth 2.0 Desktop App Flow
        if not creds:
            oauth_client_file = os.environ.get("GOOGLE_OAUTH_CLIENT_FILE", "credentials.json")
            oauth_user_file = os.environ.get("GOOGLE_AUTHORIZED_USER_FILE", "authorized_user.json")
            if oauth_client_file and os.path.exists(oauth_client_file):
                try:
                    self.client = gspread.oauth(
                        scopes=scope,
                        credentials_filename=oauth_client_file,
                        authorized_user_filename=oauth_user_file
                    )
                    self.spreadsheet = self.client.open_by_key(self.sheet_id)
                    print(f"[SheetsHelper] Authorized and connected to Google Sheets via OAuth: {self.spreadsheet.title}")
                    return
                except Exception as oauth_err:
                    import traceback
                    print(f"[SheetsHelper] Failed to load/authenticate OAuth credentials: {repr(oauth_err)}")
                    traceback.print_exc()

        if not creds:
            print("[SheetsHelper] WARNING: No valid credentials found (Service Account or OAuth Client). Using Local Mock Mode.")
            self.use_mock = True
        else:
            try:
                self.client = gspread.authorize(creds)
                self.spreadsheet = self.client.open_by_key(self.sheet_id)
                print(f"[SheetsHelper] Connected to Google Sheets: {self.spreadsheet.title}")
            except Exception as e:
                print(f"[SheetsHelper] ERROR: Google Sheets connection failed: {e}. Switching to Local Mock Mode.")
                self.use_mock = True

    def get_brands_from_sheet(self) -> list[str]:
        """
        Dynamically reads all brand names from the 'brands' worksheet tab in Google Sheets.
        Returns a clean list of brand names.
        """
        if self._brands_cache:
            return self._brands_cache

        brands_list = []
        if self.use_mock:
            mock_data = load_local_mock()
            mock_brands = mock_data.get("brands", [])
            for item in mock_brands:
                if isinstance(item, dict):
                    val = list(item.values())[0] if item else ""
                else:
                    val = str(item)
                if val and val.strip():
                    brands_list.append(val.strip())
        else:
            try:
                worksheets = self.spreadsheet.worksheets()
                brands_ws = next((ws for ws in worksheets if ws.title.strip().lower() == "brands"), None)
                if brands_ws:
                    all_vals = brands_ws.get_all_values()
                    for row in all_vals:
                        if row and row[0].strip():
                            b_val = row[0].strip()
                            if b_val and b_val not in brands_list:
                                brands_list.append(b_val)
                    print(f"[SheetsHelper] Loaded {len(brands_list)} brands from tab 'brands'.")
            except Exception as e:
                print(f"[SheetsHelper] Error fetching 'brands' worksheet tab: {e}")

        if not brands_list:
            brands_list = [
                'LUCAS', 'DENSO', 'AISIN', 'BOSCH', 'NGK', 'VALEO', 'GMB', 'EXEDY', 'GATES', 'GSP',
                '555 (Three Five)', 'TRW', 'CTR', '333 / CJ', 'RBI', 'POP (ชลิต อินดัสทรี)', 'MOTIF',
                'KYB (Kayaba)', 'TOKICO', 'MONROE', 'ZF (ZF Aftermarket)', 'BC RACING', 'PROFENDER',
                'TEIN', 'BREMBO', 'BENDIX', 'COMPACT BRAKE', 'AKEBONO', 'MIG (MIG BRAKE)', 'NIBK',
                'GIRLING', 'TIMKEN', 'NSK', 'KOYO', 'NTN', 'SKF', 'WIX FILTERS', 'SAKURA', 'K&N',
                'ACDELCO', 'GS', 'FB', 'PANASONIC', 'AMARON', 'PTT Lubricants (ปตท.)', 'Bangchak (บางจาก)',
                'Pulzar (เพลซาร์)', 'Shell (เชลล์)', 'Castrol (คาสตรอล)', 'Mobil 1 (โมบิล วัน)',
                'Caltex (คาลเท็กซ์)', 'TotalEnergies (โททาลเอนเนอร์ยี่ส์)', 'Motul (โมตุล)',
                'Liqui Moly (ลิควิ โมลี่)', 'Amsoil (แอมซอยล์)', 'Sunoco (ซูโนโก้)'
            ]

        self._brands_cache = brands_list
        return brands_list

    def search_oem(self, oem_code: str) -> list[dict]:
        """Search for rows matching OEM code in all tabs."""
        return self.search_by_vehicle_and_product(oem_code=oem_code)

    def search_by_vehicle_and_product(
        self,
        brand: str = "",
        model: str = "",
        product_name: str = "",
        year: str = "",
        oem_code: str = ""
    ) -> list[dict]:
        """
        Search Google Sheets across all tabs by vehicle brand, model, product name, year, and OEM code.
        Returns ALL matching rows (e.g. all KYB series: Excel-G, Super Red, New SR, etc.).
        """
        brand_clean = brand.strip().lower()
        model_clean = model.strip().lower()
        product_clean = product_name.strip().lower()
        year_clean = year.strip()
        oem_clean = oem_code.strip().upper()

        # Build type-specific product keywords for precise matching
        prod_keywords = []
        # ประเภทสินค้า -> คำที่ต้องมีในชื่อสินค้าใน Google Sheet
        PRODUCT_TYPE_MAP = [
            (["ผ้าดิส", "ผ้าเบรกหน้า", "ผ้าเบรคหน้า"],      ["ผ้าดิส", "ผ้าเบรกหน้า", "ผ้าเบรคหน้า", "brake pad"]),
            (["ผ้าเบรกหลัง", "ผ้าเบรคหลัง"],                 ["ผ้าเบรกหลัง", "ผ้าเบรคหลัง", "brake pad rear"]),
            (["ผ้าเบรก", "ผ้าเบรค", "brake pad"],            ["ผ้าเบรก", "ผ้าเบรค", "ผ้าดิส", "brake pad"]),
            (["ก้ามเบรก", "ก้ามเบรค", "brake shoe"],         ["ก้ามเบรก", "ก้ามเบรค", "brake shoe"]),
            (["จานเบรก", "จานดิส", "disc", "rotor"],         ["จานเบรก", "จานดิส", "brake disc", "rotor"]),
            (["โช้คอัพ", "โช้ค", "โช๊ค", "shock"],           ["โช้คอัพ", "โช้ค", "โช๊ค", "shock absorber"]),
            (["กรองอากาศ", "air filter"],                    ["กรองอากาศ", "air filter"]),
            (["กรองแอร์", "cabin filter"],                   ["กรองแอร์", "cabin filter"]),
            (["กรองเครื่อง", "กรองน้ำมัน", "oil filter"],    ["กรองเครื่อง", "กรองน้ำมัน", "oil filter"]),
            (["กรองโซล่า", "กรองดีเซล", "fuel filter"],      ["กรองโซล่า", "กรองดีเซล", "fuel filter"]),
            (["ลูกปืนล้อ", "ลูกปืนดุม", "wheel bearing", "hub bearing"], ["ลูกปืนล้อ", "ลูกปืนดุม", "wheel bearing", "hub bearing"]),
            (["ลูกปืน", "bearing"],                         ["ลูกปืน", "bearing"]),
            (["คลัตช์", "คลัทช์", "clutch"],                ["คลัตช์", "คลัทช์", "clutch"]),
            (["สายพาน", "belt"],                            ["สายพาน", "belt"]),
            (["ยางแท่นเครื่อง", "engine mount"],            ["ยางแท่นเครื่อง", "engine mount"]),
            (["ยาง", "rubber"],                             ["ยาง", "rubber"]),
        ]

        matched_type_keywords = None
        for triggers, row_keywords in PRODUCT_TYPE_MAP:
            if any(t in product_clean for t in triggers):
                matched_type_keywords = row_keywords
                break

        if matched_type_keywords:
            prod_keywords = matched_type_keywords
        elif product_clean:
            prod_keywords = [product_clean]

        want_rear = any(w in product_clean for w in ["หลัง", "rear"])
        want_front = any(w in product_clean for w in ["หน้า", "front"])
        want_left = any(w in product_clean for w in ["ซ้าย", "left"])
        want_right = any(w in product_clean for w in ["ขวา", "right"])

        results = []
        seen_keys = set()

        def add_record_if_new(r):
            row_dict = {k: str(r.get(k, "")) for k in HEADERS}
            key = (
                row_dict.get("แบรนด์ของสินค้า", "").strip().upper(),
                row_dict.get("รหัสสินค้า", "").strip().upper(),
                row_dict.get("เบอร์ OEM", "").strip().upper(),
                row_dict.get("ยี่ห้อรถ", "").strip().upper(),
                row_dict.get("รุ่นรถ", "").strip().upper(),
                row_dict.get("ปีเริ่มต้น", "").strip(),
                row_dict.get("ปีสิ้นสุด", "").strip(),
                row_dict.get("เครื่องยนต์", "").strip().upper()
            )
            if key not in seen_keys:
                seen_keys.add(key)
                results.append(row_dict)

        records_by_tab = []
        if self.use_mock:
            mock_data = load_local_mock()
            for tab_name, rows in mock_data.items():
                records_by_tab.append(rows)
        else:
            try:
                worksheets = self.spreadsheet.worksheets()
                for ws in worksheets:
                    records_by_tab.append(ws.get_all_records())
            except Exception as e:
                print(f"[SheetsHelper] Error fetching worksheets: {e}")

        for records in records_by_tab:
            for r in records:
                if not isinstance(r, dict):
                    continue
                row_oem = str(r.get("เบอร์ OEM", "")).strip().upper()
                row_sku = str(r.get("รหัสสินค้า", "")).strip().upper()
                row_brand_car = str(r.get("ยี่ห้อรถ", "")).strip().lower()
                row_model_car = str(r.get("รุ่นรถ", "")).strip().lower()
                row_prod_th = str(r.get("ชื่อสินค้า (ไทย)", "")).strip().lower()
                row_prod_en = str(r.get("ชื่อสินค้า (อังกฤษ)", "")).strip().lower()
                row_desc = str(r.get("รายละเอียดสินค้า", "")).strip().lower()
                row_year_start = str(r.get("ปีเริ่มต้น", "")).strip()
                row_year_end = str(r.get("ปีสิ้นสุด", "")).strip()

                # 1. Product Title & Sub-category Classification
                prod_title_only = f"{row_prod_th} {row_prod_en}".lower()
                prod_combined = f"{row_prod_th} {row_prod_en} {row_desc}".lower()

                # Sub-category check (Discs vs Pads vs Shoes, Oil vs Air vs Cabin vs Fuel Filter)
                want_disc = any(w in product_clean for w in ["จาน", "disc", "rotor"])
                want_pad = any(w in product_clean for w in ["ผ้า", "pad"])
                want_shoe = any(w in product_clean for w in ["ก้าม", "shoe"])

                if want_disc:
                    has_disc_title = any(w in prod_title_only for w in ["จาน", "disc", "rotor"])
                    has_pad_title = any(w in prod_title_only for w in ["ผ้า", "ก้าม", "pad", "shoe"])
                    if has_pad_title and not has_disc_title:
                        continue
                    if not has_disc_title and "จาน" in product_clean:
                        continue

                if want_pad or want_shoe:
                    has_pad_or_shoe = any(w in prod_combined for w in ["ผ้า", "ก้าม", "pad", "shoe", "lining", "เบรค", "เบรก"])
                    has_disc_title = any(w in prod_title_only for w in ["จาน", "rotor"])
                    if has_disc_title and not any(w in prod_title_only for w in ["ผ้า", "ก้าม", "pad", "shoe"]):
                        continue
                    is_other_brake_part = any(w in prod_title_only for w in ["แม่ปั๊ม", "ปั๊ม", "ท่อยาง", "สายเบรค", "สายเบรก", "สวิตช์", "กระบอก", "น้ำมันเบรก", "น้ำมันเบรค"])
                    if is_other_brake_part and not any(w in prod_title_only for w in ["ผ้า", "ก้าม", "pad", "shoe"]):
                        continue
                    if not has_pad_or_shoe:
                        continue

                # Filters sub-category check
                want_oil_filter = any(w in product_clean for w in ["กรองเครื่อง", "กรองน้ำมันเครื่อง", "oil filter"])
                want_air_filter = any(w in product_clean for w in ["กรองอากาศ", "air filter"])
                want_cabin_filter = any(w in product_clean for w in ["กรองแอร์", "cabin filter"])

                if want_oil_filter:
                    if any(w in prod_title_only for w in ["อากาศ", "แอร์", "โซล่า", "ดีเซล", "air filter", "cabin filter", "fuel filter"]) and not any(w in prod_title_only for w in ["เครื่อง", "น้ำมันเครื่อง", "oil filter"]):
                        continue

                if want_air_filter:
                    if any(w in prod_title_only for w in ["เครื่อง", "แอร์", "โซล่า", "ดีเซล", "oil filter", "cabin filter", "fuel filter"]) and not any(w in prod_title_only for w in ["อากาศ", "air filter"]):
                        continue

                if want_cabin_filter:
                    if any(w in prod_title_only for w in ["เครื่อง", "อากาศ", "โซล่า", "ดีเซล", "oil filter", "air filter", "fuel filter"]) and not any(w in prod_title_only for w in ["แอร์", "cabin filter"]):
                        continue

                # Position check (Front vs Rear)
                has_rear = any(w in prod_combined for w in ["หลัง", "rear"])
                has_front = any(w in prod_combined for w in ["หน้า", "front"])

                if want_rear and has_front and not has_rear:
                    continue

                if want_front and has_rear and not has_front:
                    continue

                # Side check (Left vs Right)
                has_left = any(w in prod_combined for w in ["ซ้าย", "left"])
                has_right = any(w in prod_combined for w in ["ขวา", "right"])

                if want_left and has_right and not has_left:
                    continue
                if want_right and has_left and not has_right:
                    continue

                # Vehicle & Product match
                brand_match = True
                if brand_clean:
                    b_tokens = [t.strip() for t in re.split(r'[\(\)\-/\s]+', brand_clean) if len(t.strip()) >= 2 and t.strip() not in ["รถบรรทุก", "บัส", "รถกระบะ", "รถยนต์"]]
                    r_b_tokens = [t.strip() for t in re.split(r'[\(\)\-/\s]+', row_brand_car) if len(t.strip()) >= 2]
                    brand_match = not b_tokens or any(t in row_brand_car or any(rt in t or t in rt for rt in r_b_tokens) for t in b_tokens)

                # OEM code match check after position/sub-category & brand validation
                clean_oem_req = re.sub(r'[^A-Z0-9]', '', oem_clean)
                clean_r_oem = re.sub(r'[^A-Z0-9]', '', row_oem)
                clean_r_sku = re.sub(r'[^A-Z0-9]', '', row_sku)

                if clean_oem_req and (clean_oem_req in clean_r_oem or clean_oem_req in clean_r_sku or (clean_r_oem and clean_r_oem in clean_oem_req)):
                    if brand_match:
                        add_record_if_new(r)
                        continue

                model_match = True
                if model_clean:
                    m_tokens = [m.strip() for m in re.split(r'[\(\)\-/\s]+', model_clean) if len(m.strip()) >= 2]
                    model_match = (
                        model_clean in row_model_car or
                        row_model_car in model_clean or
                        any(m in row_model_car for m in m_tokens) or
                        row_model_car in ["", "-", "–", "ทุกรุ่น", "standard model", "all models"]
                    )

                prod_match = True
                if prod_keywords:
                    prod_match = any(kw in prod_combined for kw in prod_keywords)

                year_match = True
                if year_clean:
                    target_y = parse_single_year(year_clean)
                    if target_y:
                        y_start, y_end = parse_year_range(row_year_start, row_year_end)
                        if not (y_start <= target_y <= y_end):
                            year_match = False

                if brand_match and model_match and prod_match and year_match:
                    add_record_if_new(r)

        return results

    def write_temp_sheet(self, rows: list[dict]):
        """Append rows to sheet named 'temp'."""
        if not rows:
            return

        # Build list representation of rows
        rows_to_write = []
        for row in rows:
            row_list = [row.get(col, "") for col in HEADERS]
            rows_to_write.append(row_list)

        if self.use_mock:
            mock_data = load_local_mock()
            if "temp" not in mock_data:
                mock_data["temp"] = []
            for r in rows:
                mock_data["temp"].append(r)
            save_local_mock(mock_data)
            print(f"[SheetsHelper-Mock] Appended {len(rows)} rows to local mock temp sheet.")
            return

        # Real Google Sheet workflow
        try:
            # Check if temp worksheet exists, if not create it
            try:
                temp_ws = self.spreadsheet.worksheet("temp")
            except gspread.exceptions.WorksheetNotFound:
                temp_ws = self.spreadsheet.add_worksheet(title="temp", rows="100", cols=str(len(HEADERS)))
                temp_ws.append_row(HEADERS)
                print("[SheetsHelper] Created 'temp' worksheet in Google Sheets.")

            # Append rows
            temp_ws.append_rows(rows_to_write)
            print(f"[SheetsHelper] Successfully appended {len(rows)} rows to 'temp' sheet in Google Sheets.")
        except Exception as e:
            print(f"[SheetsHelper] Error writing to Google Sheet: {e}")
