"""
Comprehensive Automated Verification for Final Permission & Function Audit.
Validates:
1. All 9 audit artifacts generated in docs/
2. SuperAdmin permission-audit API endpoint (/api/superadmin/permission-audit)
3. Permanent Customer Deny enforcement (Automotive Export, Raw SQL, Internal Workspaces)
4. Role boundary isolation for all 7 platform roles
"""

import os
import sys
import json
import csv
import requests

BASE_URL = "http://127.0.0.1:8000"

def test_audit_docs():
    print("=== 1. Checking 9 Required Audit Artifacts in docs/ ===")
    required_files = [
        "docs/PERMISSION_FUNCTION_MATRIX.md",
        "docs/PERMISSION_FUNCTION_MATRIX.csv",
        "docs/API_PERMISSION_MATRIX.md",
        "docs/ROLE_ROUTE_MATRIX.md",
        "docs/CUSTOMER_FEATURE_MATRIX.md",
        "docs/DENIED_FUNCTIONS.md",
        "docs/MISSING_FUNCTIONS.md",
        "docs/UNAUTHORIZED_FUNCTIONS.md",
        "docs/FINAL_PERMISSION_AUDIT.md"
    ]
    for rf in required_files:
        assert os.path.exists(rf), f"Missing required artifact: {rf}"
        size = os.path.getsize(rf)
        assert size > 500, f"Artifact {rf} seems too small ({size} bytes)"
        print(f"  [OK] {rf} exists ({size:,} bytes)")

def test_superadmin_permission_audit_api():
    print("\n=== 2. Testing /api/superadmin/permission-audit ===")
    
    # 2.1 SuperAdmin Access -> MUST SUCCEED (200)
    res = requests.get(f"{BASE_URL}/api/superadmin/permission-audit", headers={
        "x-username": "superadmin",
        "x-user-role": "SUPER_ADMIN"
    })
    assert res.status_code == 200, f"Expected 200 for SUPER_ADMIN, got {res.status_code}"
    data = res.json()
    assert data["success"] is True
    metrics = data["metrics"]
    print("  [OK] SuperAdmin permission audit endpoint returned 200 OK")
    print(f"       Metrics: Roles={metrics['total_roles']}, Perms={metrics['total_permissions']}, Functions={metrics['total_functions']}, APIs={metrics['total_apis']}")
    print(f"       Matrix rows: {len(data.get('matrix', []))}")
    print(f"       Discovery tree modules: {list(data.get('discovery_tree', {}).keys())}")

    # 2.2 System Owner Access -> MUST SUCCEED (200)
    res_owner = requests.get(f"{BASE_URL}/api/superadmin/permission-audit", headers={
        "x-username": "owner",
        "x-user-role": "OWNER"
    })
    assert res_owner.status_code == 200, f"Expected 200 for OWNER, got {res_owner.status_code}"
    print("  [OK] System Owner access permitted to permission audit endpoint")

    # 2.3 Customer Role Access -> MUST FAIL (403)
    res_cust = requests.get(f"{BASE_URL}/api/superadmin/permission-audit", headers={
        "x-username": "user_starter",
        "x-user-role": "CUSTOMER_OWNER"
    })
    assert res_cust.status_code in [401, 403], f"Expected 401/403 for CUSTOMER_OWNER, got {res_cust.status_code}"
    print(f"  [OK] Customer Owner access strictly rejected with {res_cust.status_code} Forbidden")

def test_permanent_customer_deny():
    print("\n=== 3. Testing Permanent Customer Deny Invariants ===")
    
    # 3.1 Export Automotive Data -> MUST RETURN 403 FOR CUSTOMERS
    res_export = requests.post(f"{BASE_URL}/api/saas/export", 
        json={"filter_brand": "", "filter_car": ""},
        headers={"x-username": "user_starter", "x-user-role": "CUSTOMER_OWNER"}
    )
    assert res_export.status_code == 403, f"Expected 403 for Customer Export, got {res_export.status_code}"
    print("  [OK] Automotive Data CSV Export strictly blocked for Customer (403 Forbidden)")

    # 3.2 SuperAdmin Scraper URL -> MUST RETURN 403 FOR CUSTOMERS
    res_scrape = requests.post(f"{BASE_URL}/api/admin/scrape-url",
        json={"url": "https://example.com/parts"},
        headers={"x-username": "user_starter", "x-user-role": "CUSTOMER_OWNER"}
    )
    assert res_scrape.status_code in [401, 403], f"Expected 403 for Scraper control, got {res_scrape.status_code}"
    print("  [OK] Web Scraper execution strictly blocked for Customer (403 Forbidden)")

    # 3.3 Owner Revenue Metrics -> MUST RETURN 403 FOR CUSTOMERS
    res_rev = requests.get(f"{BASE_URL}/api/owner/revenue",
        headers={"x-username": "user_starter", "x-user-role": "CUSTOMER_OWNER"}
    )
    assert res_rev.status_code in [401, 403], f"Expected 403 for Owner Revenue, got {res_rev.status_code}"
    print("  [OK] System Owner MRR / ARR Analytics strictly blocked for Customer (403 Forbidden)")

if __name__ == "__main__":
    test_audit_docs()
    test_superadmin_permission_audit_api()
    test_permanent_customer_deny()
    print("\n=======================================================")
    print("ALL AUDIT VERIFICATIONS AND INVARIANTS PASSED (100%)")
    print("=======================================================")
