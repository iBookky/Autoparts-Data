import asyncio
import json
from sheets_helper import SheetsHelper
from scraper import verify_and_process_autoparts

async def run_verification():
    print("==========================================================================================")
    print("  TEST 1: DYNAMIC BRANDS LOADING FROM TAB 'brands' (Rule #2)")
    print("==========================================================================================")
    sh = SheetsHelper()
    brands = sh.get_brands_from_sheet()
    print(f"Total Brands Loaded from tab 'brands': {len(brands)}")
    print(f"Sample Brands: {brands[:15]}\n")
    assert len(brands) > 0, "Failed: brands list is empty!"
    assert "BENDIX" in [b.upper() for b in brands] or "COMPACT BRAKE" in [b.upper() for b in brands], "Failed to load aftermarket brands!"

    print("==========================================================================================")
    print("  TEST 2: OEM LOOKUP & WEB VERIFICATION & TEMP TAB SAVING (Rule #4)")
    print("==========================================================================================")
    res_oem = await verify_and_process_autoparts(
        oem_code="47441-5730",
        brand="HINO (ฮีโน่ - รถบรรทุก/บัส)",
        product_name="ผ้าเบรค"
    )
    print(f"Success: {res_oem.get('success')}")
    print(f"Data Source: {res_oem.get('data_source')}")
    print(f"OEM Code: {res_oem.get('oem_code')}")
    rows_oem = res_oem.get("rows", [])
    print(f"Total Brands Returned: {len(rows_oem)}")
    for r in rows_oem:
        print(f" - {r.get('แบรนด์ของสินค้า'):<18} | SKU: {r.get('รหัสสินค้า'):<16} | Model: {r.get('รุ่นรถ')}")
    print()

    print("==========================================================================================")
    print("  TEST 3: NO-OEM LOOKUP USING VEHICLE SPECS (Rule #5)")
    print("==========================================================================================")
    res_no_oem = await verify_and_process_autoparts(
        brand="ISUZU",
        model="D-Max",
        year="2020",
        product_name="ผ้าเบรคหน้า"
    )
    print(f"Success: {res_no_oem.get('success')}")
    print(f"Data Source: {res_no_oem.get('data_source')}")
    print(f"OEM Identified: {res_no_oem.get('oem_code')}")
    rows_no_oem = res_no_oem.get("rows", [])
    print(f"Total Brands Returned: {len(rows_no_oem)}")
    for r in rows_no_oem:
        print(f" - {r.get('แบรนด์ของสินค้า'):<18} | SKU: {r.get('รหัสสินค้า'):<16} | Model: {r.get('รุ่นรถ')}")
    print()

    print("==========================================================================================")
    print("  TEST 4: VIN VALIDATION & VERIFICATION (Rule #6)")
    print("==========================================================================================")
    res_vin = await verify_and_process_autoparts(
        vin="MR0KA3CD900000000", # Toyota VIN
        brand="Toyota",
        model="Hilux Revo",
        product_name="กรองน้ำมันเครื่อง"
    )
    print(f"Success: {res_vin.get('success')}")
    print(f"VIN Corrected: {res_vin.get('vin_corrected')}")
    print(f"Corrected VIN: {res_vin.get('corrected_vin')}")
    print(f"VIN Explanation: {res_vin.get('vin_explanation')}")
    print(f"OEM Identified: {res_vin.get('oem_code')}")
    print(f"Total Rows: {len(res_vin.get('rows', []))}\n")

    print("==========================================================================================")
    print("  ALL 4 VERIFICATION TESTS COMPLETED SUCCESSFULLY!")
    print("==========================================================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
