import requests

BASE_URL = "http://localhost:8000"

def test_owner_workflow():
    print("=== TESTING OWNER LOGIN & CALLING CLEAN DATA ===")
    
    # 1. Owner login
    res = requests.post(f"{BASE_URL}/api/saas/auth/login", json={"username": "owner", "password": "admin123"})
    assert res.status_code == 200, f"Owner login failed: {res.text}"
    token = res.json()["token"]
    role = res.json().get("role")
    assert role == "OWNER", f"Expected role OWNER, got {role}"
    headers = {"Authorization": f"Bearer {token}"}
    print("   [PASS] Owner login successful.")

    # 2. Call clean endpoint
    clean_res = requests.post(f"{BASE_URL}/api/owner/data/clean-test-data", headers=headers, json={})
    print("   [PASS] Clean Endpoint Response:", clean_res.json())

    # 3. Owner metrics overview
    metrics_res = requests.get(f"{BASE_URL}/api/owner/overview", headers=headers)
    assert metrics_res.status_code == 200
    metrics = metrics_res.json()
    print("   [PASS] Owner overview metrics after clean:", metrics["metrics"])
    assert metrics["metrics"]["mrr"] == 0
    assert metrics["metrics"]["total_organizations"] == 0
    assert metrics["metrics"]["active_subscriptions"] == 0

    # 4. SuperAdmin login
    sa_res = requests.post(f"{BASE_URL}/api/saas/auth/login", json={"username": "superadmin", "password": "admin123"})
    assert sa_res.status_code == 200
    sa_token = sa_res.json()["token"]
    sa_role = sa_res.json().get("role")
    assert sa_role == "SUPER_ADMIN"
    print("   [PASS] SuperAdmin login successful.")

    # 5. Confirm admin/staff/customer accounts were deleted
    for test_user in ["admin", "staff", "customer"]:
        u_res = requests.post(f"{BASE_URL}/api/saas/auth/login", json={"username": test_user, "password": "admin123"})
        data = u_res.json()
        assert data.get("success") is False, f"Account {test_user} should not be able to log in!"
        print(f"   [PASS] Account '{test_user}' is successfully purged ({data.get('error')}).")

    print("\n=== COMPLETE PURGE AND VERIFICATION PASSED 100% ===")

if __name__ == "__main__":
    test_owner_workflow()
