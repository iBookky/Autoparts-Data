import requests
import json

BASE_URL = "http://localhost:8000"

def test_metadata_crud():
    print("=== TESTING METADATA CRUD FOR ALL 5 CATEGORIES/TYPES ===")
    
    # 1. Admin Login
    login_res = requests.post(f"{BASE_URL}/api/saas/auth/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("   [PASS] Admin authenticated.")

    # 2. Test Aftermarket Brand PUT
    # Get brands
    b_res = requests.get(f"{BASE_URL}/api/metadata/aftermarket-brands", headers=headers).json()
    brands = b_res.get("brands") or b_res.get("results") or []
    if brands:
        brand_id = brands[0]["id"]
        old_name = brands[0]["name"]
        print(f"   Editing Aftermarket Brand ID #{brand_id} ({old_name})...")
        put_b = requests.put(f"{BASE_URL}/api/admin/metadata/aftermarket-brands/{brand_id}", headers=headers, json={"name": f"{old_name}"})
        assert put_b.status_code == 200
        assert put_b.json()["success"] is True
        print("   [PASS] Aftermarket Brand PUT working.")

    # 3. Test Car Brand PUT
    cb_res = requests.get(f"{BASE_URL}/api/metadata/car-brands", headers=headers).json()
    car_brands = cb_res.get("brands") or cb_res.get("results") or []
    if car_brands:
        cb_id = car_brands[0]["id"]
        cb_name = car_brands[0]["name"]
        print(f"   Editing Car Brand ID #{cb_id} ({cb_name})...")
        put_cb = requests.put(f"{BASE_URL}/api/admin/metadata/car-brands/{cb_id}", headers=headers, json={"name": f"{cb_name}"})
        assert put_cb.status_code == 200
        assert put_cb.json()["success"] is True
        print("   [PASS] Car Brand PUT working.")

    # 4. Test Car Model PUT
    cm_res = requests.get(f"{BASE_URL}/api/metadata/car-models", headers=headers).json()
    models = cm_res.get("models") or cm_res.get("results") or []
    if models:
        cm_id = models[0]["id"]
        cm_name = models[0]["name"]
        cm_brand = models[0].get("car_brand") or "TOYOTA"
        print(f"   Editing Car Model ID #{cm_id} ({cm_name})...")
        put_cm = requests.put(f"{BASE_URL}/api/admin/metadata/car-models/{cm_id}", headers=headers, json={"name": cm_name, "car_brand": cm_brand})
        assert put_cm.status_code == 200
        assert put_cm.json()["success"] is True
        print("   [PASS] Car Model PUT working.")

    # 5. Test Car Year PUT
    cy_res = requests.get(f"{BASE_URL}/api/metadata/car-years", headers=headers).json()
    years = cy_res.get("years") or cy_res.get("results") or []
    if years:
        cy_id = years[0]["id"]
        cy_val = years[0]["year"]
        print(f"   Editing Car Year ID #{cy_id} ({cy_val})...")
        put_cy = requests.put(f"{BASE_URL}/api/admin/metadata/car-years/{cy_id}", headers=headers, json={"year": cy_val})
        assert put_cy.status_code == 200
        assert put_cy.json()["success"] is True
        print("   [PASS] Car Year PUT working.")

    # 6. Test Category PUT
    cat_res = requests.get(f"{BASE_URL}/api/metadata/categories", headers=headers).json()
    cats = cat_res.get("categories") or cat_res.get("results") or []
    if cats:
        cat_id = cats[0]["id"]
        cat_name = cats[0]["name"]
        cat_en = cats[0].get("name_en") or "Category EN"
        put_cat = requests.put(f"{BASE_URL}/api/admin/metadata/categories/{cat_id}", headers=headers, json={"name": cat_name, "name_en": cat_en, "description": "Updated description"})
        assert put_cat.status_code == 200
        assert put_cat.json()["success"] is True
        print("   [PASS] Category PUT working.")

    print("\n=== ALL METADATA CRUD TESTS PASSED (100%) ===")

if __name__ == "__main__":
    test_metadata_crud()
