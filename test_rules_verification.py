import asyncio
import json
from sheets_helper import SheetsHelper
from scraper import verify_and_process_autoparts, get_oem_by_vehicle_and_product

async def run_verification():
    print("==========================================================================================")
    print("  COMPREHENSIVE RULE VERIFICATION TEST SUITE (ALL 4 USER CONDITIONS)")
    print("==========================================================================================")

    # ------------------------------------------------------------------------------------------
    # GLOBAL TEST: Mandatory Part Name Check
    # ------------------------------------------------------------------------------------------
    print("\n--- TEST G: Mandatory Part Name Check ---")
    res_no_product = await verify_and_process_autoparts(
        oem_code="04465-0D020",
        product_name=""
    )
    print(f"Success: {res_no_product.get('success')}")
    print(f"Error Message: {res_no_product.get('error')}")
    assert res_no_product.get('success') is False, "Failed: Blank product_name should be rejected!"
    assert "กรุณาระบุชื่อสินค้า" in res_no_product.get('error', ''), "Failed: Wrong error message for missing product name!"
    print("PASSED: Blank part name correctly blocked.")

    # ------------------------------------------------------------------------------------------
    # REFERENCE TEST 1: Toyota Yaris (2012-2014) OEM 04465-52260 & ACDelco 19371548
    # ------------------------------------------------------------------------------------------
    print("\n--- TEST R1: Toyota Yaris (2012-2014) Reference Check ---")
    spec_yaris = get_oem_by_vehicle_and_product("Toyota", "Yaris", "ผ้าเบรคหน้า")
    print(f"Model: {spec_yaris['model']}")
    print(f"OEM Code: {spec_yaris['oem_code']}")
    assert spec_yaris["oem_code"] == "04465-52260", f"Expected 04465-52260 for Yaris, got {spec_yaris['oem_code']}"
    print("PASSED: Toyota Yaris OEM 04465-52260 accurately mapped.")

    # ------------------------------------------------------------------------------------------
    # REFERENCE TEST 2: Isuzu D-Max (2012-2020) OEM 8-98079-104-0 & ACDelco 19374024
    # ------------------------------------------------------------------------------------------
    print("\n--- TEST R2: Isuzu D-Max (2012-2020) Reference Check ---")
    spec_dmax = get_oem_by_vehicle_and_product("ISUZU", "D-Max", "ผ้าเบรคหน้า")
    print(f"Model: {spec_dmax['model']}")
    print(f"OEM Code: {spec_dmax['oem_code']}")
    assert spec_dmax["oem_code"] == "8-98079-104-0", f"Expected 8-98079-104-0 for D-Max, got {spec_dmax['oem_code']}"
    print("PASSED: Isuzu D-Max OEM 8-98079-104-0 accurately mapped.")

    # ------------------------------------------------------------------------------------------
    # CONDITION 1 TEST: OEM Code Lookup & Web Search & Temp Tab Saving
    # ------------------------------------------------------------------------------------------
    print("\n--- TEST 1: OEM Code Lookup & Global Web Search ---")
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
    for r in rows_oem[:5]:
        print(f" - {r.get('แบรนด์ของสินค้า'):<18} | SKU: {r.get('รหัสสินค้า'):<16} | Model: {r.get('รุ่นรถ')}")
    assert res_oem.get('success') is True, "Failed: Condition 1 search failed!"

    # ------------------------------------------------------------------------------------------
    # CONDITION 2 TEST: VIN Provided -> Mandate Car Brand
    # ------------------------------------------------------------------------------------------
    print("\n--- TEST 2A: VIN Provided WITHOUT Brand (Should Fail) ---")
    res_vin_no_brand = await verify_and_process_autoparts(
        vin="MR0KA3CD900000000",
        product_name="กรองน้ำมันเครื่อง"
    )
    print(f"Success: {res_vin_no_brand.get('success')}")
    print(f"Error Message: {res_vin_no_brand.get('error')}")
    assert res_vin_no_brand.get('success') is False, "Failed: VIN without Brand should be rejected!"
    assert "บังคับให้ระบุยี่ห้อรถยนต์" in res_vin_no_brand.get('error', ''), "Failed: Wrong error message for VIN without Brand!"
    print("PASSED: VIN without Brand correctly blocked.")

    # ------------------------------------------------------------------------------------------
    # CONDITION 3 TEST: No OEM & No VIN -> Mandate Car Brand AND Car Model
    # ------------------------------------------------------------------------------------------
    print("\n--- TEST 3A: No OEM & No VIN WITHOUT Model (Should Fail) ---")
    res_no_model = await verify_and_process_autoparts(
        brand="Honda",
        product_name="ผ้าเบรคหน้า"
    )
    print(f"Success: {res_no_model.get('success')}")
    print(f"Error Message: {res_no_model.get('error')}")
    assert res_no_model.get('success') is False, "Failed: Search without Model when no OEM/VIN should be rejected!"
    assert "บังคับให้ระบุทั้งยี่ห้อรถยนต์ (Brand) และรุ่นรถยนต์ (Model)" in res_no_model.get('error', ''), "Failed: Wrong error message for missing Model!"
    print("PASSED: Search without Model when no OEM/VIN correctly blocked.")

    # ------------------------------------------------------------------------------------------
    # CONDITION 4 TEST: ALL Fields Provided -> Cross-Verification & Conflict Alert
    # ------------------------------------------------------------------------------------------
    print("\n--- TEST 4: ALL Fields Provided with Conflicting OEM Code ---")
    res_conflict = await verify_and_process_autoparts(
        oem_code="45022-S04-150", # Honda Civic OEM code
        vin="MR0KA3CD900000000", # Toyota VIN
        brand="Toyota",
        model="Hilux Revo",
        year="2020",
        product_name="ผ้าเบรคหน้า"
    )
    print(f"Success: {res_conflict.get('success')}")
    print(f"OEM Warning Flag: '{res_conflict.get('oem_warning')}'")
    print(f"VIN Explanation: {res_conflict.get('vin_explanation')}")
    assert res_conflict.get('oem_warning') == "ตรวจสอบเลขโอเอ็มใหม่" or "ตรวจสอบเลขโอเอ็มใหม่" in res_conflict.get('vin_explanation', ''), "Failed: Conflict warning 'ตรวจสอบเลขโอเอ็มใหม่' was not triggered!"
    print("PASSED: OEM conflict warning 'ตรวจสอบเลขโอเอ็มใหม่' correctly generated.")

    print("\n==========================================================================================")
    print("  ALL TEST SUITE CASES COMPLETED AND PASSED PERFECTLY!")
    print("==========================================================================================")

if __name__ == "__main__":
    asyncio.run(run_verification())
