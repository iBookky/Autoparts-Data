import sys
import os
import asyncio
import re

# Add path to import scraper module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import (
    AFTERMARKET_BRAND_ALIASES,
    CATEGORIZED_AFTERMARKET_BRANDS,
    get_category_target_brands,
    extract_aftermarket_brands,
    extract_aftermarket_details,
    get_aftermarket_recommendations_list,
    get_aftermarket_recommendations,
    verify_and_process_autoparts
)

REQUESTED_57_BRANDS = [
    "LUCAS", "DENSO", "AISIN", "BOSCH", "NGK", "VALEO", "GMB", "EXEDY", "GATES", "GSP",
    "555 (Three Five)", "TRW", "CTR", "333 / CJ", "RBI", "POP (ชลิต อินดัสทรี)", "MOTIF",
    "KYB (Kayaba)", "TOKICO", "MONROE", "ZF (ZF Aftermarket)", "BC RACING", "PROFENDER",
    "TEIN", "BREMBO", "BENDIX", "COMPACT BRAKE", "AKEBONO", "MIG (MIG BRAKE)", "NIBK",
    "GIRLING", "TIMKEN", "LUCAS", "NSK", "KOYO", "NTN", "SKF", "WIX FILTERS", "SAKURA",
    "K&N", "ACDELCO", "GS", "FB", "PANASONIC", "AMARON", "PTT Lubricants (ปตท.)",
    "Bangchak (บางจาก)", "Pulzar (เพลซาร์)", "Shell (เชลล์)", "Castrol (คาสตรอล)",
    "Mobil 1 (โมบิล วัน)", "Caltex (คาลเท็กซ์)", "TotalEnergies (โททาลเอนเนอร์ยี่ส์)",
    "Motul (โมตุล)", "Liqui Moly (ลิควิ โมลี่)", "Amsoil (แอมซอยล์)", "Sunoco (ซูโนโก้)"
]

def test_all_brands_in_alias_map():
    print("--- Test 1: Verifying all requested 57 brands exist in AFTERMARKET_BRAND_ALIASES ---")
    missing = []
    unique_requested = set(REQUESTED_57_BRANDS)
    for b in unique_requested:
        if b not in AFTERMARKET_BRAND_ALIASES:
            missing.append(b)
    
    assert not missing, f"Missing brands in AFTERMARKET_BRAND_ALIASES: {missing}"
    print(f"SUCCESS: All {len(unique_requested)} unique requested brands present in AFTERMARKET_BRAND_ALIASES!\n")

def test_category_target_brands():
    print("--- Test 2: Verifying category target brand mappings ---")
    
    # 1. Brakes
    brakes_targets = get_category_target_brands("ผ้าเบรก หน้า Honda Civic")
    assert "BREMBO" in brakes_targets
    assert "BENDIX" in brakes_targets
    assert "COMPACT BRAKE" in brakes_targets
    assert "AKEBONO" in brakes_targets
    print("  [✓] Brakes category targets verified")

    # 2. Suspension
    suspension_targets = get_category_target_brands("โช๊คอัพ หน้า Toyota Vios")
    assert "KYB (Kayaba)" in suspension_targets
    assert "TOKICO" in suspension_targets
    assert "555 (Three Five)" in suspension_targets
    assert "PROFENDER" in suspension_targets
    print("  [✓] Suspension category targets verified")

    # 3. Bearings
    bearing_targets = get_category_target_brands("ตลับลูกปืนดุมล้อ หลัง Toyota Altis")
    assert "SKF" in bearing_targets
    assert "NSK" in bearing_targets
    assert "KOYO" in bearing_targets
    assert "NTN" in bearing_targets
    assert "TIMKEN" in bearing_targets
    print("  [✓] Bearings category targets verified")

    # 4. Clutch
    clutch_targets = get_category_target_brands("ชุดจานคลัทช์ Isuzu D-Max")
    assert "AISIN" in clutch_targets
    assert "EXEDY" in clutch_targets
    print("  [✓] Clutch category targets verified")

    # 5. Lubricants
    oil_targets = get_category_target_brands("น้ำมันเครื่องสังเคราะห์ 5W-30")
    assert "PTT Lubricants (ปตท.)" in oil_targets
    assert "Bangchak (บางจาก)" in oil_targets
    assert "Shell (เชลล์)" in oil_targets
    assert "Mobil 1 (โมบิล วัน)" in oil_targets
    assert "Liqui Moly (ลิควิ โมลี่)" in oil_targets
    print("  [✓] Lubricants category targets verified")

    # 6. Batteries & Electrical
    battery_targets = get_category_target_brands("แบตเตอรี่ กึ่งแห้ง MFX-60L")
    assert "GS" in battery_targets
    assert "FB" in battery_targets
    assert "PANASONIC" in battery_targets
    assert "AMARON" in battery_targets
    print("  [✓] Batteries category targets verified")
    
    print("SUCCESS: Category target mappings test passed!\n")

def test_extract_aftermarket_brands_from_snippets():
    print("--- Test 3: Extracting aftermarket brands & SKUs from snippets ---")
    mock_snippets = [
        ("ร้านอะไหล่แท้", "จำหน่าย ผ้าเบรก Brembo P83054 สำหรับ Toyota Altis"),
        ("โช๊คอัพ คายาบา", "โช้คอัพ KYB Excel-G เบอร์ 333462 รับประกันศูนย์"),
        ("น้ำมันเครื่อง ปตท", "น้ำมันเครื่อง PTT Performa Synthetic 5W-30 ลิตร"),
        ("แบตเตอรี่ จีเอส", "แบตเตอรี่ GS MFX-70L สเปคแห้งพร้อมใช้งาน"),
        ("ลูกหมาก ตองห้า", "ลูกหมากปีกนก 555 เบอร์ SB-3602 สำหรับ Civic FB"),
        ("กรองอากาศ วิกซ์", "กรองอากาศ Wix Filters 51348 ประสิทธิภาพสูง"),
        ("ชุดคลัทช์ ไอซิน", "ชุดจานคลัทช์ AISIN WPT-001 คุณภาพมาตรฐาน OEM")
    ]

    extracted = extract_aftermarket_brands(mock_snippets, oem_number="52610-TR7-B03")
    extracted_dict = {item["brand"]: item["sku"] for item in extracted}

    assert "BREMBO" in extracted_dict
    assert extracted_dict["BREMBO"] == "P83054"

    assert "KYB (Kayaba)" in extracted_dict
    assert extracted_dict["KYB (Kayaba)"] == "333462"

    assert "PTT Lubricants (ปตท.)" in extracted_dict

    assert "GS" in extracted_dict
    assert extracted_dict["GS"] == "MFX-70L"

    assert "555 (Three Five)" in extracted_dict
    assert extracted_dict["555 (Three Five)"] == "SB-3602"

    assert "WIX FILTERS" in extracted_dict
    assert extracted_dict["WIX FILTERS"] == "51348"

    assert "AISIN" in extracted_dict

    print("Extracted Aftermarket Brands from Mock Snippets:")
    for item in extracted:
        print(f"  - {item['brand']}: SKU={item['sku']}")

    print("\nSUCCESS: Aftermarket brand extraction test passed!\n")

def test_extract_aftermarket_details():
    print("--- Test 4: Testing extract_aftermarket_details ---")
    snippets = [
        ("Brake Pad Shop", "Compact Nano DCC-1234 ผ้าเบรคหน้าเกรดพรีเมียม OEM 04465-0D020")
    ]
    brand, sku = extract_aftermarket_details(snippets, oem_number="04465-0D020")
    assert brand == "COMPACT BRAKE", f"Expected COMPACT BRAKE, got {brand}"
    assert sku == "DCC-1234", f"Expected DCC-1234, got {sku}"
    print(f"  [✓] Extracted: Brand={brand}, SKU={sku}")
    print("SUCCESS: extract_aftermarket_details test passed!\n")

async def test_full_search_workflow():
    print("--- Test 5: Testing verify_and_process_autoparts with mock sheet search ---")
    result = await verify_and_process_autoparts(
        oem_code="52610-TR7-B03",
        product_name="โช๊คอัพหลังขวา"
    )
    assert result.get("success") == True
    assert "rows" in result
    rows = result["rows"]
    print(f"  [✓] Processed OEM 52610-TR7-B03 successfully, returned {len(rows)} row(s):")
    for r in rows:
        print(f"      - Brand: {r.get('แบรนด์ของสินค้า')}, SKU: {r.get('รหัสสินค้า')}")
    print("SUCCESS: Full search workflow test passed!\n")

if __name__ == "__main__":
    print("==================================================")
    print("  RUNNING 57 AFTERMARKET BRANDS VERIFICATION TESTS")
    print("==================================================")
    test_all_brands_in_alias_map()
    test_category_target_brands()
    test_extract_aftermarket_brands_from_snippets()
    test_extract_aftermarket_details()
    asyncio.run(test_full_search_workflow())
    print("==================================================")
    print("  ALL 57 AFTERMARKET BRAND TESTS PASSED 100%!")
    print("==================================================")
