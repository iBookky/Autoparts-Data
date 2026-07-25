import asyncio
import json
import urllib.request

def test_oem_lookup(oem_code: str, brand: str = "", product_name: str = ""):
    print(f"\n==========================================================================================")
    print(f"  TESTING OEM LOOKUP: OEM='{oem_code}' | BRAND='{brand}' | PRODUCT='{product_name}'")
    print(f"==========================================================================================")
    
    url = "http://127.0.0.1:8000/api/search"
    payload = {
        "oem_code": oem_code,
        "brand": brand,
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
            
            print(f"{'แบรนด์สินค้า':<22} | {'รหัสสินค้า (SKU)':<18} | {'เบอร์ OEM':<16} | {'รุ่นรถ':<18} | {'รายละเอียดสินค้า'}")
            print("-" * 115)
            for r in rows:
                b = r.get("แบรนด์ของสินค้า", "")
                sku = r.get("รหัสสินค้า", "")
                oem = r.get("เบอร์ OEM", "")
                model = r.get("รุ่นรถ", "")
                detail = r.get("รายละเอียดสินค้า", "")
                if len(detail) > 42:
                    detail = detail[:39] + "..."
                print(f"{b:<22} | {sku:<18} | {oem:<16} | {model:<18} | {detail}")
            print("-" * 115)
            return data
    except Exception as e:
        print(f"Error querying API: {e}")
        return None

if __name__ == "__main__":
    test_oem_lookup("47441-5730", "HINO (ฮีโน่ - รถบรรทุก/บัส)", "ผ้าเบรค")
