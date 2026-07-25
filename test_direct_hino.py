import asyncio
import json
from scraper import verify_and_process_autoparts

async def main():
    print("==========================================================================================")
    print("  DIRECT PYTHON TEST: OEM='47441-5730' | BRAND='HINO' | PRODUCT='ผ้าเบรค'")
    print("==========================================================================================")
    
    res = await verify_and_process_autoparts(
        oem_code="47441-5730",
        brand="HINO (ฮีโน่ - รถบรรทุก/บัส)",
        product_name="ผ้าเบรค"
    )
    
    print(f"Success: {res.get('success')}")
    print(f"Data Source: {res.get('data_source')}")
    print(f"OEM Code: {res.get('oem_code')}")
    rows = res.get("rows", [])
    print(f"Total Rows Returned: {len(rows)}\n")
    
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

if __name__ == "__main__":
    asyncio.run(main())
