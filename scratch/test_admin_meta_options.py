import json
from fastapi.testclient import TestClient
from main import app
from backend.database import get_db_connection

client = TestClient(app)

admin_headers = {
    "x-user-role": "ADMIN",
    "x-username": "admin"
}

def test_metadata_public_endpoints():
    endpoints = [
        "/api/metadata/aftermarket-brands",
        "/api/metadata/car-brands",
        "/api/metadata/car-models",
        "/api/metadata/car-years",
        "/api/metadata/categories",
        "/api/metadata/ai-models"
    ]
    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200, f"Failed on {ep}: {res.text}"
        data = res.json()
        assert data.get("success") is True
        assert isinstance(data.get("results"), list)
        print(f"GET {ep} -> {len(data['results'])} items (OK)")

def test_aftermarket_brand_crud():
    brand_name = "TEST_BRAND_999"
    # Create
    res = client.post("/api/admin/metadata/aftermarket-brands", json={"name": brand_name}, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    brand_id = data.get("id")

    # Verify present
    res = client.get("/api/metadata/aftermarket-brands")
    results = res.json()["results"]
    assert any(b["id"] == brand_id and b["name"] == brand_name for b in results)
    print(f"Aftermarket Brand CRUD: Created ID {brand_id} (OK)")

    # Delete
    res = client.delete(f"/api/admin/metadata/aftermarket-brands/{brand_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json().get("success") is True

    # Verify deleted
    res = client.get("/api/metadata/aftermarket-brands")
    results = res.json()["results"]
    assert not any(b["id"] == brand_id for b in results)
    print("Aftermarket Brand CRUD: Deleted (OK)")

def test_car_brand_crud():
    brand_name = "TEST_MAKE_999"
    # Create
    res = client.post("/api/admin/metadata/car-brands", json={"name": brand_name}, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    brand_id = data.get("id")

    # Verify present
    res = client.get("/api/metadata/car-brands")
    results = res.json()["results"]
    assert any(b["id"] == brand_id and b["name"] == brand_name for b in results)
    print(f"Car Brand CRUD: Created ID {brand_id} (OK)")

    # Delete
    res = client.delete(f"/api/admin/metadata/car-brands/{brand_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json().get("success") is True

    # Verify deleted
    res = client.get("/api/metadata/car-brands")
    results = res.json()["results"]
    assert not any(b["id"] == brand_id for b in results)
    print("Car Brand CRUD: Deleted (OK)")

def test_category_crud():
    cat_name = "ทดสอบหมวดหมู่_999"
    cat_name_en = "Test Category 999"
    # Create
    res = client.post("/api/admin/metadata/categories", json={"name": cat_name, "name_en": cat_name_en}, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    cat_id = data.get("id")

    # Verify present
    res = client.get("/api/metadata/categories")
    results = res.json()["results"]
    assert any(c["id"] == cat_id and c["name"] == cat_name for c in results)
    print(f"Category CRUD: Created ID {cat_id} (OK)")

    # Delete
    res = client.delete(f"/api/admin/metadata/categories/{cat_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json().get("success") is True

    # Verify deleted
    res = client.get("/api/metadata/categories")
    results = res.json()["results"]
    assert not any(c["id"] == cat_id for c in results)
    print("Category CRUD: Deleted (OK)")

def test_car_model_crud():
    car_brand = "TOYOTA"
    model_name = "Test_Model_999"
    # Create
    res = client.post("/api/admin/metadata/car-models", json={"car_brand": car_brand, "name": model_name}, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    model_id = data.get("id")

    # Verify present
    res = client.get(f"/api/metadata/car-models?car_brand={car_brand}")
    results = res.json()["results"]
    assert any(m["id"] == model_id and m["name"] == model_name for m in results)
    print(f"Car Model CRUD: Created ID {model_id} (OK)")

    # Delete
    res = client.delete(f"/api/admin/metadata/car-models/{model_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json().get("success") is True

    # Verify deleted
    res = client.get(f"/api/metadata/car-models?car_brand={car_brand}")
    results = res.json()["results"]
    assert not any(m["id"] == model_id for m in results)
    print("Car Model CRUD: Deleted (OK)")

def test_car_year_crud():
    year_val = "2049"
    # Create
    res = client.post("/api/admin/metadata/car-years", json={"year": year_val}, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    year_id = data.get("id")

    # Verify present
    res = client.get("/api/metadata/car-years")
    results = res.json()["results"]
    assert any(y["id"] == year_id and str(y["year"]) == year_val for y in results)
    print(f"Car Year CRUD: Created ID {year_id} (OK)")

    # Delete
    res = client.delete(f"/api/admin/metadata/car-years/{year_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json().get("success") is True

    # Verify deleted
    res = client.get("/api/metadata/car-years")
    results = res.json()["results"]
    assert not any(y["id"] == year_id for y in results)
    print("Car Year CRUD: Deleted (OK)")

def test_ai_model_crud():
    model_name = "test-ai-gpt-999"
    provider = "OpenAI Test"
    desc = "Unit test custom AI model"
    # Create
    res = client.post("/api/admin/metadata/ai-models", json={"model_name": model_name, "provider": provider, "description": desc}, headers=admin_headers)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data.get("success") is True
    model_id = data.get("id")

    # Verify present
    res = client.get("/api/metadata/ai-models")
    results = res.json()["results"]
    assert any(m["id"] == model_id and m["model_name"] == model_name for m in results)
    print(f"AI Model CRUD: Created ID {model_id} (OK)")

    # Delete
    res = client.delete(f"/api/admin/metadata/ai-models/{model_id}", headers=admin_headers)
    assert res.status_code == 200
    assert res.json().get("success") is True

    # Verify deleted
    res = client.get("/api/metadata/ai-models")
    results = res.json()["results"]
    assert not any(m["id"] == model_id for m in results)
    print("AI Model CRUD: Deleted (OK)")

if __name__ == "__main__":
    test_metadata_public_endpoints()
    test_aftermarket_brand_crud()
    test_car_brand_crud()
    test_category_crud()
    test_car_model_crud()
    test_car_year_crud()
    test_ai_model_crud()
    print("\n>>> ALL 6 METADATA OPTIONS CRUD TESTS PASSED PERFECTLY! <<<")
