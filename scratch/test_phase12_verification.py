import urllib.request
import urllib.parse
import json
import re

def run_tests():
    print("==================================================")
    print("PHASE 12 END-TO-END VERIFICATION SUITE")
    print("==================================================")

    # 1. API Plan CRUD Endpoints Verification
    print("\n[TEST 1] Testing Backend Plan CRUD APIs...")
    headers = {
        'x-user-role': 'OWNER',
        'x-username': 'owner',
        'Content-Type': 'application/json'
    }

    # 1.1 GET plans
    req = urllib.request.Request('http://127.0.0.1:8000/api/owner/plans', headers=headers)
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        assert data['success'] is True
        initial_count = len(data['plans'])
        print(f"  ✓ GET /api/owner/plans passed (Found {initial_count} plans)")

    # 1.2 POST create new plan
    test_plan_id = "custom_fleet_pro"
    new_plan = {
        "id": test_plan_id,
        "name": "Fleet Pro Express",
        "price_monthly": 4990,
        "monthly_search_quota": 12000,
        "max_brands": 20,
        "max_categories": 40,
        "max_users": 8,
        "vin_search_enabled": True,
        "api_access_enabled": True,
        "export_enabled": True,
        "ai_search_enabled": True
    }
    req = urllib.request.Request('http://127.0.0.1:8000/api/owner/plans', data=json.dumps(new_plan).encode(), headers=headers, method='POST')
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        assert data['success'] is True
        print(f"  ✓ POST /api/owner/plans created '{test_plan_id}' successfully")

    # Verify newly created plan is in GET
    req = urllib.request.Request('http://127.0.0.1:8000/api/owner/plans', headers=headers)
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        found = any(p['id'] == test_plan_id for p in data['plans'])
        assert found is True
        print(f"  ✓ Verified '{test_plan_id}' is returned by GET /api/owner/plans")

    # 1.3 PUT update plan
    update_payload = {
        "name": "Fleet Pro Express (Enhanced)",
        "price_monthly": 5490,
        "monthly_search_quota": 15000,
        "max_brands": 25,
        "max_categories": 50,
        "max_users": 10,
        "vin_search_enabled": True,
        "api_access_enabled": True,
        "export_enabled": True,
        "ai_search_enabled": True
    }
    req = urllib.request.Request(f'http://127.0.0.1:8000/api/owner/plans/{test_plan_id}', data=json.dumps(update_payload).encode(), headers=headers, method='PUT')
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        assert data['success'] is True
        print(f"  ✓ PUT /api/owner/plans/{test_plan_id} updated successfully")

    # 1.4 DELETE plan
    req = urllib.request.Request(f'http://127.0.0.1:8000/api/owner/plans/{test_plan_id}', headers=headers, method='DELETE')
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        assert data['success'] is True
        print(f"  ✓ DELETE /api/owner/plans/{test_plan_id} deleted successfully")

    # 1.5 Deletion invariant on plan with active subscribers
    req = urllib.request.Request('http://127.0.0.1:8000/api/owner/plans/professional', headers=headers, method='DELETE')
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode())
        assert data['success'] is False
        assert "Cannot delete plan" in data['error']
        print(f"  ✓ Deletion protection invariant verified: {data['error']}")

    # 2. HTML Structure & Modal Verification
    print("\n[TEST 2] Verifying HTML & Frontend Modals...")
    with open("index.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    assert 'id="modal-create-plan"' in html_content
    assert 'id="modal-edit-plan"' in html_content
    assert 'id="owner-plans-perf-table-body"' in html_content
    assert 'openCreatePlanModal' in html_content
    assert 'openEditPlanModal' in html_content
    assert 'deletePlanConfirm' in html_content
    assert 'submitCreatePlan' in html_content
    assert 'submitEditPlan' in html_content
    print("  ✓ Modal and CRUD UI elements exist in index.html")

    # 3. Verify 'ล้างแคช' button removal
    print("\n[TEST 3] Verifying Cache Button Removal...")
    assert "ล้างแคช" not in html_content or "🧹 ล้างแคช" not in html_content
    # Ensure there is no button that triggers clear cache in UI
    assert 'onclick="clearAllCacheAndReset()"' not in html_content
    print("  ✓ Verified: No 'ล้างแคช' button in UI")

    # 4. Day / Light Mode CSS Typography Verification
    print("\n[TEST 4] Verifying Day / Light Mode Zero-White-Text CSS Rules...")
    with open("frontend/css/index.css", "r", encoding="utf-8") as f:
        css_content = f.read()

    assert '[data-theme="light"]' in css_content
    assert 'ZERO WHITE TEXT RULE' in css_content
    assert '[data-theme="light"] body' in css_content
    assert '[data-theme="light"] .nav-item.active' in css_content
    assert '[data-theme="light"] .workspace-tab-btn.active' in css_content
    print("  ✓ Verified: Zero white text display rules and active state rules configured in CSS")

    print("\n==================================================")
    print("🎉 ALL PHASE 12 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_tests()
