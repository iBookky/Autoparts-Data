import sys
import json
import urllib.request

def test_oem_lookup(oem_code: str, product_name: str = ""):
    print(f"\n==========================================================================================")
    print(f"  TESTING LIVE OEM LOOKUP: OEM='{oem_code}' | PRODUCT='{product_name}'")
    print(f"==========================================================================================")
    
    url = "http://127.0.0.1:8000/api/search"
    payload = {
        "oem_code": oem_code,
        "product_name": product_name or "อะไหล่"
    }
    
    headers = {"Content-Type": "application/json"}
    req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers)
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            data = res_data.get("data", {})
            
            print(f"Data Source: {data.get('data_source')}")
            print(f"OEM Code Result: {data.get('oem_code')}")
            rows = data.get("rows", [])
            print(f"Total Matching Rows Found: {len(rows)}\n")
            
            print(f"{'แบรนด์สินค้า':<22} | {'รหัสสินค้า (SKU)':<18} | {'เบอร์ OEM':<16} | {'รุ่นรถ':<16} | {'รายละเอียดสินค้า'}")
            print("-" * 110)
            for r in rows:
                b = r.get("แบรนด์ของสินค้า", "")
                sku = r.get("รหัสสินค้า", "")
                oem = r.get("เบอร์ OEM", "")
                model = r.get("รุ่นรถ", "")
                detail = r.get("รายละเอียดสินค้า", "")
                if len(detail) > 42:
                    detail = detail[:39] + "..."
                print(f"{b:<22} | {sku:<18} | {oem:<16} | {model:<16} | {detail}")
            print("-" * 110)
            return data
    except Exception as e:
        print(f"Error querying API: {e}")
        return None

if __name__ == "__main__":
    # Test OEM code not in Google Sheets (should trigger Global Web Search AI and write to temp tab)
    test_oem_lookup("31922-4H900", "กรองโซล่า")
    
    # Test OEM code in Google Sheets
    test_oem_lookup("04465-0D020", "ผ้าเบรคหน้า")
