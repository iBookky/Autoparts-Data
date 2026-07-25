import os
import json
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

        prod_keywords = []
        if product_clean:
            if any(w in product_clean for w in ["โช้ค", "โช๊ค", "shock"]):
                prod_keywords.extend(["โช้ค", "โช๊ค", "shock"])
            if any(w in product_clean for w in ["เบรก", "เบรค", "brake"]):
                prod_keywords.extend(["เบรก", "เบรค", "brake"])
            if any(w in product_clean for w in ["กรอง", "filter"]):
                prod_keywords.extend(["กรอง", "filter"])
            if any(w in product_clean for w in ["ลูกปืน", "bearing"]):
                prod_keywords.extend(["ลูกปืน", "bearing"])
            if any(w in product_clean for w in ["คลัตช์", "คลัทช์", "clutch"]):
                prod_keywords.extend(["คลัตช์", "คลัทช์", "clutch"])
            if not prod_keywords:
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
                row_dict.get("แบรนด์ของสินค้า", "").upper(),
                row_dict.get("รหัสสินค้า", "").upper(),
                row_dict.get("เบอร์ OEM", "").upper()
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
                    has_pad_title = any(w in prod_title_only for w in ["ผ้า", "pad"])
                    if has_pad_title and not has_disc_title:
                        continue
                    if not has_disc_title and "จาน" in product_clean:
                        continue

                if want_pad:
                    has_pad_title = any(w in prod_title_only for w in ["ผ้า", "pad"])
                    has_disc_title = any(w in prod_title_only for w in ["จาน", "disc", "rotor"])
                    if has_disc_title and not has_pad_title:
                        continue
                    if not has_pad_title and "ผ้า" in product_clean:
                        continue

                if want_shoe:
                    has_shoe_title = any(w in prod_title_only for w in ["ก้าม", "shoe"])
                    if not has_shoe_title:
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
                if want_rear and not has_rear:
                    continue

                if want_front and has_rear and not has_front:
                    continue
                if want_front and not has_front:
                    continue

                # Side check (Left vs Right)
                has_left = any(w in prod_combined for w in ["ซ้าย", "left"])
                has_right = any(w in prod_combined for w in ["ขวา", "right"])

                if want_left and has_right and not has_left:
                    continue
                if want_right and has_left and not has_right:
                    continue

                # OEM code match check after position/sub-category validation
                if oem_clean and oem_clean in (row_oem, row_sku):
                    add_record_if_new(r)
                    continue

                # Vehicle & Product match
                brand_match = True
                if brand_clean:
                    brand_match = (
                        brand_clean in row_brand_car or
                        row_brand_car in brand_clean or
                        ("โตโยต้า" in brand_clean and "toyota" in row_brand_car) or
                        ("ฮอนด้า" in brand_clean and "honda" in row_brand_car)
                    )

                model_match = True
                if model_clean:
                    model_match = (
                        model_clean in row_model_car or
                        any(m in row_model_car for m in model_clean.split() if len(m) >= 2)
                    )

                prod_match = True
                if prod_keywords:
                    prod_match = any(kw in prod_combined for kw in prod_keywords)

                year_match = True
                if year_clean and year_clean.isdigit():
                    y = int(year_clean)
                    try:
                        y_start = int(row_year_start) if row_year_start.isdigit() else 1900
                        y_end = int(row_year_end) if row_year_end.isdigit() else 2099
                        if not (y_start <= y <= y_end):
                            year_match = False
                    except ValueError:
                        pass

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
