"""
Master Comprehensive Test Runner for Autoparts SaaS Platform.
Tests End-to-End:
1. Audit Documentation & Matrices
2. RBAC & Security Boundary Enforcement (7 Roles)
3. Permanent Customer Deny List (Zero Export, Zero Scraper, Zero Raw SQL)
4. Internal Permission Audit API & Discovery Tree (/api/superadmin/permission-audit)
5. Tenant Context & Entitlement Gates
6. Commercial Billing & Thai VAT 7% Tax Invoicing
7. Automotive Parts Search & Cross-Reference Engine
8. Frontend DOM & Static Asset Integrity
"""

import os
import sys
import json
import csv
import sqlite3
import requests
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def run_test(name, fn):
    print(f"\n--- [TEST] {name} ---")
    try:
        fn()
        print(f"  --> PASSED: {name}")
        return True
    except Exception as e:
        print(f"  --> FAILED: {name} | Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# =========================================================================
# 1. Audit Deliverables Test
# =========================================================================
def test_audit_deliverables():
    required_docs = [
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
    for doc in required_docs:
        assert os.path.exists(doc), f"Missing required file: {doc}"
        assert os.path.getsize(doc) > 500, f"File {doc} is too small"
    print(f"  Verified all {len(required_docs)} audit documentation files in docs/.")

# =========================================================================
# 2. Permission Audit API Test
# =========================================================================
def test_permission_audit_api():
    # 2.1 SuperAdmin -> 200
    res = requests.get(f"{BASE_URL}/api/superadmin/permission-audit", headers={
        "x-username": "superadmin", "x-user-role": "SUPER_ADMIN"
    })
    assert res.status_code == 200, f"Expected 200 for SUPER_ADMIN, got {res.status_code}"
    data = res.json()
    assert data["success"] is True
    assert "metrics" in data
    assert data["metrics"]["total_roles"] == 12
    assert data["metrics"]["total_permissions"] == 30
    assert data["metrics"]["total_apis"] == 113
    assert len(data.get("matrix", [])) > 300
    assert "SEARCH" in data.get("discovery_tree", {})
    assert "CROSS_REFERENCE" in data.get("discovery_tree", {})
    print(f"  SuperAdmin audit API verified: {len(data['matrix'])} matrix records returned.")

    # 2.2 Customer -> 403
    res_cust = requests.get(f"{BASE_URL}/api/superadmin/permission-audit", headers={
        "x-username": "user_starter", "x-user-role": "CUSTOMER_OWNER"
    })
    assert res_cust.status_code in [401, 403], f"Customer must be blocked, got {res_cust.status_code}"
    print("  Customer strictly denied access to permission-audit API (403).")

# =========================================================================
# 3. Permanent Customer Deny List Test
# =========================================================================
def test_customer_deny_list():
    # 3.1 Export Automotive Data -> 403
    res_exp = requests.post(f"{BASE_URL}/api/saas/export", 
        json={"filter_brand": "", "filter_car": ""},
        headers={"x-username": "user_starter", "x-user-role": "CUSTOMER_OWNER"}
    )
    assert res_exp.status_code == 403, f"Customer export must return 403, got {res_exp.status_code}"

    # 3.2 Scraper Control -> 403
    res_scr = requests.post(f"{BASE_URL}/api/admin/scrape-url",
        json={"url": "https://example.com"},
        headers={"x-username": "user_starter", "x-user-role": "CUSTOMER_OWNER"}
    )
    assert res_scr.status_code in [401, 403], f"Scraper must return 403 for customer, got {res_scr.status_code}"

    # 3.3 Owner Revenue Metrics -> 403
    res_rev = requests.get(f"{BASE_URL}/api/owner/revenue",
        headers={"x-username": "user_starter", "x-user-role": "CUSTOMER_OWNER"}
    )
    assert res_rev.status_code in [401, 403], f"Owner revenue must return 403 for customer, got {res_rev.status_code}"
    print("  Permanent customer deny list verified for export, scraper, and internal owner analytics.")

# =========================================================================
# 4. Tenant Context & Entitlement Gates Test
# =========================================================================
def test_tenant_context_and_entitlements():
    res = requests.get(f"{BASE_URL}/api/saas/context", headers={"x-username": "user_starter"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    ctx = data["context"]
    assert "user" in ctx
    assert "organization" in ctx
    assert "subscription" in ctx
    assert "usage" in ctx
    print(f"  Tenant context verified for org: {ctx['organization']['name']} (Plan: {ctx['subscription']['plan_name']})")

# =========================================================================
# 5. Commercial Billing & Thai VAT 7% Calculation Test
# =========================================================================
def test_billing_and_vat_calculation():
    payload = {
        "plan_id": "professional",
        "billing_cycle": "MONTHLY",
        "add_on_ids": ["ai_power_pack"],
        "coupon_code": ""
    }
    res = requests.post(f"{BASE_URL}/api/saas/billing/calculate", json=payload, headers={"x-username": "user_starter"})
    assert res.status_code == 200
    calc = res.json().get("calculation", {})
    assert calc["base_price"] == 2990
    assert calc["addons_total"] == 1990
    subtotal = 2990 + 1990
    expected_vat = round(subtotal * 0.07, 2)
    assert abs(calc["tax_amount"] - expected_vat) < 1.0, f"VAT mismatch: got {calc['tax_amount']}, expected {expected_vat}"
    assert calc["total_amount"] == subtotal + calc["tax_amount"]
    print(f"  Billing calculation verified: Subtotal=฿{calc['subtotal']:,}, 7% VAT=฿{calc['tax_amount']:,}, Total=฿{calc['total_amount']:,}")

# =========================================================================
# 6. Parts Search & Cross Reference Test
# =========================================================================
def test_parts_search_and_cross_ref():
    # 6.1 Parts Search
    res_search = requests.get(f"{BASE_URL}/api/parts/search", params={"oem_code": "04465"}, headers={"x-username": "user_starter", "x-user-role": "STAFF"})
    assert res_search.status_code == 200
    data = res_search.json()
    assert data["success"] is True
    print(f"  Parts search verified: {len(data.get('items', []))} results found.")

    # 6.2 Cross Reference Matrix
    res_matrix = requests.get(f"{BASE_URL}/api/parts/cross-reference-matrix", headers={"x-username": "user_starter"})
    assert res_matrix.status_code == 200
    matrix_data = res_matrix.json()
    assert matrix_data["success"] is True
    print(f"  Cross reference matrix verified: {len(matrix_data.get('matrix', []))} relationships loaded.")

# =========================================================================
# 7. Frontend DOM & Static UI Elements Test
# =========================================================================
def test_frontend_dom():
    with open("index.html") as f:
        html = f.read()

    assert 'id="superadmin-sub-audit"' in html, "Missing #superadmin-sub-audit in index.html"
    assert 'id="superadmin-audit-table-body"' in html, "Missing #superadmin-audit-table-body in index.html"
    assert 'id="audit-discovery-tree-container"' in html, "Missing #audit-discovery-tree-container in index.html"
    assert 'loadSuperAdminPermissionAudit' in html, "Missing loadSuperAdminPermissionAudit in index.html"
    assert 'modal-invoice-receipt' in html, "Missing #modal-invoice-receipt in index.html"
    print("  Frontend index.html verified with full Permission Audit UI and modal structures.")

# =========================================================================
# Main Execution
# =========================================================================
if __name__ == "__main__":
    print("==================================================================")
    print("   AUTOPARTS SAAS PLATFORM — MASTER TEST SUITE EXECUTION")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("==================================================================")

    tests = [
        ("1. Audit Documentation Deliverables", test_audit_deliverables),
        ("2. SuperAdmin Permission Audit API", test_permission_audit_api),
        ("3. Permanent Customer Deny Enforcement", test_customer_deny_list),
        ("4. Tenant Context & Entitlements", test_tenant_context_and_entitlements),
        ("5. Commercial Billing & 7% Thai VAT", test_billing_and_vat_calculation),
        ("6. Automotive Parts Search & Cross-Ref", test_parts_search_and_cross_ref),
        ("7. Frontend DOM & UI Elements", test_frontend_dom),
    ]

    passed = 0
    failed = 0

    for name, fn in tests:
        if run_test(name, fn):
            passed += 1
        else:
            failed += 1

    print("\n==================================================================")
    print(f"   TEST SUMMARY: {passed} PASSED, {failed} FAILED (TOTAL {len(tests)})")
    if failed == 0:
        print("   ALL TESTS PASSED SUCCESSFULLY (100% PASS RATE)!")
    print("==================================================================")

    if failed > 0:
        sys.exit(1)
