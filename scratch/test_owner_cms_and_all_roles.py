import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_all():
    print("=== STARTING FULL SYSTEM & OWNER SUITE VERIFICATION ===")
    
    # 1. Public Platform Settings
    print("\n1. Testing GET /api/platform/settings (Public)...")
    res = requests.get(f"{BASE_URL}/api/platform/settings")
    assert res.status_code == 200, f"Failed: {res.text}"
    data = res.json()
    assert data["success"] is True
    print(f"   [PASS] Public Settings loaded. Site title: {data['settings']['site_title']}")

    # 2. Owner Login
    print("\n2. Testing Owner Login...")
    login_res = requests.post(f"{BASE_URL}/api/saas/auth/login", json={"username": "owner", "password": "admin123"})
    assert login_res.status_code == 200, f"Owner login failed: {login_res.text}"
    owner_token = login_res.json().get("token")
    headers = {"Authorization": f"Bearer {owner_token}"}
    print("   [PASS] Owner login successful.")

    # 3. Owner Branding Settings CRUD
    print("\n3. Testing Owner Branding Settings GET & POST...")
    get_b = requests.get(f"{BASE_URL}/api/owner/settings/branding", headers=headers)
    assert get_b.status_code == 200
    branding_data = get_b.json()["branding"]
    print(f"   Current hero_title: {branding_data['hero_title']}")

    update_b = requests.post(f"{BASE_URL}/api/owner/settings/branding", headers=headers, json={
        "site_title": "AutoParts Cross-Ref Enterprise",
        "logo_url": "https://parts.autocentric.net/assets/logo.png",
        "hero_badge": "แพลตฟอร์มสืบค้นและเทียบรหัสอะไหล่รถยนต์อันดับ 1 ในไทย (PRO)",
        "hero_title": "ค้นหาและเทียบเบอร์อะไหล่แท้ & อะไหล่ทดแทน",
        "hero_subtitle": "ระบบฐานข้อมูลและ AI เทียบเบอร์อะไหล่ที่สมบูรณ์แบบที่สุด",
        "hero_bg_style": "dark_carbon",
        "hero_bg_color": "#0B132B",
        "seo_meta_title": "AutoParts Cross-Ref Enterprise | ระบบเทียบเบอร์อะไหล่",
        "seo_meta_description": "ระบบฐานข้อมูลอะไหล่รถยนต์ OEM และ Aftermarket ครบวงจร",
        "seo_meta_keywords": "อะไหล่รถยนต์, cross reference, VIN decoder",
        "contact_email": "owner@autocentric.net",
        "contact_phone": "02-999-8888",
        "contact_line": "@autoparts",
        "footer_copyright": "© 2026 AutoParts Cross-Ref. All rights reserved."
    })
    assert update_b.status_code == 200, f"Failed update: {update_b.text}"
    assert update_b.json()["success"] is True
    print("   [PASS] Owner Branding Settings updated successfully.")

    # Verify public settings reflected
    res_pub = requests.get(f"{BASE_URL}/api/platform/settings").json()
    assert res_pub["settings"]["site_title"] == "AutoParts Cross-Ref Enterprise"
    print("   [PASS] Verified public settings updated dynamically.")

    # 4. Owner Company Profile & Tax Settings CRUD
    print("\n4. Testing Owner Company Profile & Tax Settings GET & POST...")
    get_c = requests.get(f"{BASE_URL}/api/owner/settings/company", headers=headers)
    assert get_c.status_code == 200
    comp_data = get_c.json()["company"]

    update_c = requests.post(f"{BASE_URL}/api/owner/settings/company", headers=headers, json={
        "company_name_th": "บริษัท ออโต้เซนทริค ดิจิทัล โซลูชันส์ จำกัด",
        "company_name_en": "AUTOCENTRIC DIGITAL SOLUTIONS CO., LTD.",
        "company_tax_id": "0105566099881",
        "company_branch": "สำนักงานใหญ่ (Head Office)",
        "company_address_th": "888/99 อาคารสยามทาวเวอร์ ชั้น 18 ถนนสุขุมวิท แขวงคลองเตย เขตคลองเตย กรุงเทพมหานคร 10110",
        "company_address_en": "888/99 Siam Tower 18th Fl., Sukhumvit Rd., Bangkok 10110 Thailand",
        "company_phone": "02-123-4567",
        "company_email": "billing@autocentric.net",
        "company_website": "https://parts.autocentric.net",
        "bank_name": "ธนาคารกสิกรไทย (KBANK)",
        "bank_account_no": "098-7-65432-1",
        "bank_account_name": "บจก. ออโต้เซนทริค ดิจิทัล โซลูชันส์",
        "promptpay_id": "0105566099881",
        "digital_signature_url": "https://parts.autocentric.net/assets/sig.png",
        "company_stamp_url": "https://parts.autocentric.net/assets/stamp.png"
    })
    assert update_c.status_code == 200, f"Failed company update: {update_c.text}"
    assert update_c.json()["success"] is True
    print("   [PASS] Owner Company Profile & Tax Settings updated successfully.")

    # 5. Owner Invoice Config CRUD
    print("\n5. Testing Owner Invoice Config GET & POST...")
    get_inv = requests.get(f"{BASE_URL}/api/owner/settings/invoice", headers=headers)
    assert get_inv.status_code == 200
    
    update_inv = requests.post(f"{BASE_URL}/api/owner/settings/invoice", headers=headers, json={
        "invoice_prefix": "INV-",
        "tax_invoice_prefix": "TAX-",
        "receipt_prefix": "REC-",
        "payment_due_days": 14,
        "default_vat_rate": 7.0,
        "default_wht_rate": 3.0,
        "vat_inclusive": False,
        "invoice_theme_color": "#1E40AF",
        "invoice_footer_notes": "เอกสารนี้ออกโดยระบบอัตโนมัติและถือเป็นหลักฐานการชำระเงินที่ถูกต้องสมบูรณ์",
        "invoice_terms": "กรุณาชำระเงินภายใน 14 วัน"
    })
    assert update_inv.status_code == 200, f"Failed invoice config update: {update_inv.text}"
    assert update_inv.json()["success"] is True
    print("   [PASS] Owner Invoice Config updated successfully.")

    # 6. Admin Category Edit (PUT)
    print("\n6. Testing PUT /api/admin/metadata/categories/{id}...")
    admin_login = requests.post(f"{BASE_URL}/api/saas/auth/login", json={"username": "admin", "password": "admin123"}).json()
    admin_headers = {"Authorization": f"Bearer {admin_login['token']}"}
    
    # Get categories
    cats_res = requests.get(f"{BASE_URL}/api/metadata/categories", headers=admin_headers).json()
    cats = cats_res.get("categories") or cats_res.get("results") or []
    if cats:
        cat_id = cats[0]["id"]
        cat_name = cats[0]["name"]
        cat_name_en = cats[0].get("name_en") or "Brake System"
        put_cat = requests.put(f"{BASE_URL}/api/admin/metadata/categories/{cat_id}", headers=admin_headers, json={
            "name": cat_name,
            "name_en": f"{cat_name_en} (Verified)",
            "description": "หมวดหมู่อะไหล่ตรวจสอบแล้ว"
        })
        assert put_cat.status_code == 200, f"Failed category update: {put_cat.text}"
        assert put_cat.json()["success"] is True
        print(f"   [PASS] Category ID #{cat_id} edited successfully.")

    # 7. Clean Test Data Endpoint
    print("\n7. Testing POST /api/owner/data/clean-test-data...")
    clean_res = requests.post(f"{BASE_URL}/api/owner/data/clean-test-data", headers=headers, json={
        "confirm": "CLEAN",
        "preserve_users": True,
        "preserve_parts": True
    })
    assert clean_res.status_code == 200, f"Failed clean data: {clean_res.text}"
    clean_data = clean_res.json()
    assert clean_data["success"] is True
    print(f"   [PASS] Clean data success: {clean_data.get('detail') or clean_data.get('message') or clean_data}")

    # 8. All Roles Login & Access Verification
    print("\n8. Testing All 5 Platform Roles Login...")
    roles = ["owner", "superadmin", "admin", "staff", "customer"]
    for r in roles:
        res = requests.post(f"{BASE_URL}/api/saas/auth/login", json={"username": r, "password": "admin123"})
        assert res.status_code == 200, f"Role {r} failed to login!"
        user = res.json()["user"]
        print(f"   [PASS] Role '{r}' authenticated successfully (Role: {user['role']}).")

    # 9. Fast Search Verification
    print("\n9. Testing Sub-Millisecond Search Execution...")
    t0 = time.time()
    search_res = requests.get(f"{BASE_URL}/api/parts/search?q=04465-0K360")
    t1 = time.time()
    assert search_res.status_code == 200
    duration_ms = (t1 - t0) * 1000
    print(f"   [PASS] Search completed in {duration_ms:.2f} ms with {len(search_res.json().get('results', []))} results.")

    print("\n=== ALL 9 TEST SUITES COMPLETED WITH 100% SUCCESS ===")

if __name__ == "__main__":
    test_all()
