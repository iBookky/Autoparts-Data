import os
import sys
import unittest
import sqlite3
import hashlib
from datetime import datetime
from fastapi.testclient import TestClient

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from backend.database import (
    get_db_connection,
    # User CRUD
    create_db_user,
    get_user_by_username,
    get_all_db_users,
    update_db_user_role,
    delete_db_user,
    # Parts CRUD
    get_part_by_id,
    advanced_search_parts,
    insert_temp_part,
    get_temp_parts_admin,
    edit_temp_part,
    approve_temp_part,
    reject_temp_part,
    edit_master_part,
    delete_master_part,
    # Metadata CRUD
    get_meta_aftermarket_brands,
    add_meta_aftermarket_brand,
    update_meta_aftermarket_brand,
    delete_meta_aftermarket_brand,
    get_meta_car_brands,
    add_meta_car_brand,
    update_meta_car_brand,
    delete_meta_car_brand,
    get_meta_car_models,
    add_meta_car_model,
    update_meta_car_model,
    delete_meta_car_model,
    get_meta_car_years,
    add_meta_car_year,
    update_meta_car_year,
    delete_meta_car_year,
    get_meta_categories,
    add_meta_category,
    update_meta_category,
    delete_meta_category,
    # Cross Reference Relations CRUD
    add_cross_reference_relation,
    get_cross_reference_matrix,
    update_cross_reference_relation,
    delete_cross_reference_relation,
    # Org & Team CRUD
    create_organization_db,
    get_organization_by_id,
    get_all_organizations_db,
    update_organization_db,
    get_organization_members,
    invite_org_member,
    update_member_role,
    update_member_status,
    remove_organization_member,
    # Commercial Plans & Add-ons CRUD
    get_all_plans_db,
    create_plan_db,
    update_plan_db,
    delete_plan_db,
    get_all_addons_db,
    create_add_on_db,
    update_add_on_db,
    delete_add_on_db,
    # Subscriptions & Entitlements CRUD
    get_org_category_entitlements,
    update_org_category_entitlements,
    # Invoices & Billing CRUD
    generate_invoice_db,
    get_org_invoices,
    record_payment_transaction_db,
    # Coupons CRUD
    get_all_coupons_admin,
    create_coupon_db,
    validate_coupon_db,
    delete_coupon_db,
    # CRM Leads CRUD
    create_crm_lead,
    get_crm_leads_db,
    update_crm_lead_stage_db,
    # Favorites & History CRUD
    toggle_user_favorite,
    get_user_favorites,
    record_search_usage,
    get_org_search_history,
    delete_search_log,
    # API Keys CRUD
    create_api_key,
    get_api_keys,
    delete_api_key,
    # Platform Settings CRUD
    get_platform_settings,
    update_platform_settings
)

class FullSystemCRUDComprehensiveTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        cls.admin_headers = {"x-username": "admin", "x-user-role": "ADMIN"}

    # ================= 1. USER & AUTHENTICATION CRUD =================
    def test_01_user_crud(self):
        test_username = f"crud_test_user_{os.urandom(3).hex()}@example.com"
        pwd_hash = hashlib.sha256("Secret123!".encode()).hexdigest()

        # CREATE
        res = create_db_user(test_username, pwd_hash, "STAFF")
        self.assertTrue(res.get("success", False))
        u_id = res.get("user_id")
        self.assertIsNotNone(u_id)
        self.assertGreater(u_id, 0)

        # READ
        user = get_user_by_username(test_username)
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], test_username)
        self.assertEqual(user["role"], "STAFF")

        all_users = get_all_db_users()
        self.assertTrue(any(u["username"] == test_username for u in all_users))

        # UPDATE
        update_success = update_db_user_role(u_id, "CUSTOMER")
        self.assertTrue(update_success)
        user_updated = get_user_by_username(test_username)
        self.assertEqual(user_updated["role"], "CUSTOMER")

        # DELETE
        del_res = delete_db_user(u_id)
        self.assertTrue(del_res.get("success", False))
        user_deleted = get_user_by_username(test_username)
        self.assertIsNone(user_deleted)

    # ================= 2. MASTER & TEMP PARTS CRUD =================
    def test_02_master_and_temp_parts_crud(self):
        # 1. CREATE Temp Part
        pn = f"P83000_{os.urandom(3).hex()}"
        part_payload = {
            "brand": "BREMBO",
            "part_number": pn,
            "oem_number": f"04465-TEST_{os.urandom(3).hex()}",
            "product_name_th": "ผ้าเบรคหน้าทดสอบ CRUD",
            "product_name_en": "Front Brake Pads CRUD Test",
            "category": "Brake",
            "car_brand": "TOYOTA",
            "car_model": "Camry",
            "year_start": "2018",
            "year_end": "2024",
            "engine": "2.5L",
            "source_type": "ON_DEMAND",
            "status": "PENDING",
            "notes": "CRUD Verification Test Note"
        }
        temp_id = insert_temp_part(part_payload)
        self.assertIsNotNone(temp_id)
        self.assertGreater(temp_id, 0)

        # 2. READ Temp Part
        temp_parts = get_temp_parts_admin()
        found_temp = next((t for t in temp_parts if t["id"] == temp_id), None)
        self.assertIsNotNone(found_temp)
        self.assertEqual(found_temp["brand"], "BREMBO")

        # 3. UPDATE / EDIT Temp Part
        edit_success = edit_temp_part(temp_id, {
            "notes": "Updated Temp Part Note for CRUD",
            "product_name_en": "Front Brake Pads CRUD Updated"
        })
        self.assertTrue(edit_success)

        # 4. APPROVE Temp Part -> Transitions to Master Part
        approve_ok = approve_temp_part(temp_id, {
            "product_name_en": "Front Brake Pads Master Approved"
        })
        self.assertTrue(approve_ok)

        # 5. READ Master Part
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM master_parts WHERE part_number = ?", (pn,))
        master_row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(master_row)
        master_id = master_row["id"]

        master_part = get_part_by_id(master_id, source="MASTER")
        self.assertIsNotNone(master_part)
        self.assertEqual(master_part["brand"], "BREMBO")
        self.assertEqual(master_part["product_name_en"], "Front Brake Pads Master Approved")

        # 6. UPDATE Master Part
        edit_master_success = edit_master_part(master_id, {
            "notes": "Master Part Updated Successfully"
        })
        self.assertTrue(edit_master_success)
        master_part_updated = get_part_by_id(master_id, source="MASTER")
        self.assertEqual(master_part_updated["notes"], "Master Part Updated Successfully")

        # 7. DELETE Master Part
        del_master_success = delete_master_part(master_id)
        self.assertTrue(del_master_success)
        master_part_deleted = get_part_by_id(master_id, source="MASTER")
        self.assertIsNone(master_part_deleted)

    # ================= 3. METADATA CATALOG CRUD =================
    def test_03_metadata_crud_all_types(self):
        # A. Category CRUD
        cat_name = f"TestCat_{os.urandom(3).hex()}"
        res_cat = add_meta_category(cat_name, name_en="Test Cat EN")
        self.assertTrue(res_cat.get("success", False))
        cat_id = res_cat.get("id")
        self.assertIsNotNone(cat_id)
        cats = get_meta_categories()
        self.assertTrue(any(c["id"] == cat_id for c in cats))

        update_cat_success = update_meta_category(cat_id, f"{cat_name}_MOD", "Test Cat EN Updated")
        self.assertTrue(update_cat_success)

        del_cat_success = delete_meta_category(cat_id)
        self.assertTrue(del_cat_success)
        cats_after = get_meta_categories()
        self.assertFalse(any(c["id"] == cat_id for c in cats_after))

        # B. Car Brand CRUD
        brand_name = f"Brand_{os.urandom(3).hex().upper()}"
        res_b = add_meta_car_brand(brand_name)
        self.assertTrue(res_b.get("success", False))
        b_id = res_b.get("id")
        self.assertIsNotNone(b_id)
        brands = get_meta_car_brands()
        self.assertTrue(any(b["id"] == b_id for b in brands))

        update_b_success = update_meta_car_brand(b_id, f"{brand_name}_MOD")
        self.assertTrue(update_b_success)

        del_b_success = delete_meta_car_brand(b_id)
        self.assertTrue(del_b_success)

        # C. Car Model CRUD
        model_name = f"Model_{os.urandom(3).hex()}"
        res_m = add_meta_car_model("TOYOTA", model_name)
        self.assertTrue(res_m.get("success", False))
        m_id = res_m.get("id")
        self.assertIsNotNone(m_id)
        models = get_meta_car_models("TOYOTA")
        self.assertTrue(any(m["id"] == m_id for m in models))

        update_m_success = update_meta_car_model(m_id, "TOYOTA", f"{model_name}_MOD")
        self.assertTrue(update_m_success)

        del_m_success = delete_meta_car_model(m_id)
        self.assertTrue(del_m_success)

        # D. Car Year CRUD
        test_year = "2099"
        res_y = add_meta_car_year(test_year)
        self.assertTrue(res_y.get("success", False))
        y_id = res_y.get("id")
        self.assertIsNotNone(y_id)
        years = get_meta_car_years()
        self.assertTrue(any(y["id"] == y_id for y in years))

        update_y_success = update_meta_car_year(y_id, "2098")
        self.assertTrue(update_y_success)

        del_y_success = delete_meta_car_year(y_id)
        self.assertTrue(del_y_success)

        # E. Aftermarket Brand CRUD
        am_name = f"AMBrand_{os.urandom(3).hex().upper()}"
        res_am = add_meta_aftermarket_brand(am_name)
        self.assertTrue(res_am.get("success", False))
        am_id = res_am.get("id")
        self.assertIsNotNone(am_id)
        am_brands = get_meta_aftermarket_brands()
        self.assertTrue(any(a["id"] == am_id for a in am_brands))

        update_am_success = update_meta_aftermarket_brand(am_id, f"{am_name}_MOD")
        self.assertTrue(update_am_success)

        del_am_success = delete_meta_aftermarket_brand(am_id)
        self.assertTrue(del_am_success)

    # ================= 4. CROSS-REFERENCE RELATIONS CRUD =================
    def test_04_cross_reference_relations_crud(self):
        # 1. CREATE Cross-Reference Relation
        src_part = f"SRC-{os.urandom(3).hex().upper()}"
        tgt_part = f"TGT-{os.urandom(3).hex().upper()}"
        
        rel_id = add_cross_reference_relation(
            source_brand="DENSO",
            source_part_number=src_part,
            target_brand="BOSCH",
            target_part_number=tgt_part,
            relation_type="EQUIVALENT",
            confidence_score=0.98,
            notes="Automated CRUD test cross-reference relation"
        )
        self.assertIsNotNone(rel_id)
        self.assertGreater(rel_id, 0)

        # 2. READ Cross-Reference Matrix
        matrix = get_cross_reference_matrix(limit=100)
        found_rel = next((r for r in matrix if r["id"] == rel_id), None)
        self.assertIsNotNone(found_rel)
        self.assertEqual(found_rel["source_part_number"], src_part)
        self.assertEqual(found_rel["target_part_number"], tgt_part)

        # 3. UPDATE Cross-Reference Relation
        update_rel_success = update_cross_reference_relation(rel_id, {
            "confidence_score": 1.0,
            "notes": "Updated Relation Notes"
        })
        self.assertTrue(update_rel_success)

        # 4. DELETE Cross-Reference Relation
        del_rel_success = delete_cross_reference_relation(rel_id)
        self.assertTrue(del_rel_success)

    # ================= 5. ORGANIZATIONS & TEAM MEMBERS CRUD =================
    def test_05_organizations_and_team_crud(self):
        # 1. CREATE Organization
        org_name = f"Test Org {os.urandom(3).hex()}"
        org_slug = f"test-org-{os.urandom(3).hex()}"
        org_id = create_organization_db(org_name, org_slug, "STARTER")
        self.assertIsNotNone(org_id)
        self.assertGreater(org_id, 0)

        # 2. READ Organization
        org = get_organization_by_id(org_id)
        self.assertIsNotNone(org)
        self.assertEqual(org["name"], org_name)
        self.assertEqual(org["plan_tier"], "STARTER")

        all_orgs = get_all_organizations_db()
        self.assertTrue(any(o["id"] == org_id for o in all_orgs))

        # 3. UPDATE Organization
        update_org_success = update_organization_db(org_id, {
            "name": f"{org_name} Updated",
            "plan_tier": "PROFESSIONAL"
        })
        self.assertTrue(update_org_success)
        org_updated = get_organization_by_id(org_id)
        self.assertEqual(org_updated["plan_tier"], "PROFESSIONAL")

        # 4. TEAM MEMBERS CRUD
        owner_email = f"owner_{os.urandom(3).hex()}@example.com"
        pwd_hash = hashlib.sha256("Password123!".encode()).hexdigest()
        res_owner = create_db_user(owner_email, pwd_hash, "STAFF")
        owner_user_id = res_owner["user_id"]
        invite_org_member(org_id, owner_user_id, "OWNER")

        member_email = f"member_{os.urandom(3).hex()}@example.com"
        res_u = create_db_user(member_email, pwd_hash, "STAFF")
        member_user_id = res_u["user_id"]

        # Add Member
        invite_res = invite_org_member(org_id, member_user_id, "STAFF")
        self.assertTrue(invite_res.get("success", False))

        # Read Members
        members = get_organization_members(org_id)
        self.assertTrue(any(m["user_id"] == member_user_id for m in members))

        # Update Member Role & Status
        update_role_ok, _ = update_member_role(org_id, member_user_id, "MANAGER", actor_id=owner_user_id, actor_role="OWNER")
        self.assertTrue(update_role_ok)
        update_stat_ok, _ = update_member_status(org_id, member_user_id, "SUSPENDED", actor_id=owner_user_id, actor_role="OWNER")
        self.assertTrue(update_stat_ok)

        # Remove Member
        remove_ok, _ = remove_organization_member(org_id, member_user_id, actor_id=owner_user_id, actor_role="OWNER")
        self.assertTrue(remove_ok)
        members_after = get_organization_members(org_id)
        self.assertFalse(any(m["user_id"] == member_user_id for m in members_after))

        # Clean up
        delete_db_user(member_user_id)
        delete_db_user(owner_user_id)
        conn = get_db_connection()
        conn.cursor().execute("DELETE FROM organization_members WHERE org_id = ?", (org_id,))
        conn.cursor().execute("DELETE FROM organizations WHERE id = ?", (org_id,))
        conn.commit()
        conn.close()

    # ================= 6. COMMERCIAL PLANS & ADD-ONS CRUD =================
    def test_06_plans_and_addons_crud(self):
        # 1. PLAN CRUD
        plan_id = f"test_plan_{os.urandom(3).hex()}"
        create_p_res = create_plan_db({
            "id": plan_id,
            "name": "Test CRUD Plan",
            "price_monthly": 1990,
            "price_yearly": 19900,
            "max_brands": 3,
            "max_categories": 3,
            "max_users": 2,
            "monthly_search_quota": 2000,
            "vin_search_enabled": 1,
            "api_access_enabled": 0,
            "export_enabled": 0,
            "ai_search_enabled": 1
        })
        self.assertTrue(create_p_res.get("success", False))

        # Read Plans
        plans = get_all_plans_db()
        found_plan = next((p for p in plans if p["id"] == plan_id), None)
        self.assertIsNotNone(found_plan)
        self.assertEqual(found_plan["name"], "Test CRUD Plan")

        # Update Plan
        update_p_res = update_plan_db(plan_id, {
            "name": "Test CRUD Plan Updated",
            "price_monthly": 2490
        })
        self.assertTrue(update_p_res.get("success", False))

        # Delete Plan
        del_p_res = delete_plan_db(plan_id)
        self.assertTrue(del_p_res.get("success", False))

        # 2. ADD-ON CRUD
        addon_id = f"addon_{os.urandom(3).hex()}"
        create_a_res = create_add_on_db({
            "id": addon_id,
            "code": addon_id,
            "name": "Test CRUD Add-on",
            "entitlement_type": "SEARCH_QUOTA",
            "price_monthly": 490,
            "price_yearly": 4900,
            "quota_increase": 500,
            "description": "Test Add-on Description"
        })
        self.assertTrue(create_a_res.get("success", False))

        # Read Add-ons
        addons = get_all_addons_db()
        found_addon = next((a for a in addons if a["id"] == addon_id), None)
        self.assertIsNotNone(found_addon)

        # Update Add-on
        update_a_res = update_add_on_db(addon_id, {
            "name": "Test CRUD Add-on Updated",
            "price_monthly": 590
        })
        self.assertTrue(update_a_res.get("success", False))

        # Delete Add-on
        del_a_res = delete_add_on_db(addon_id)
        self.assertTrue(del_a_res.get("success", False))

    # ================= 7. COUPONS & BILLING INVOICES CRUD =================
    def test_07_coupons_and_invoices_crud(self):
        # 1. COUPON CRUD
        coupon_code = f"TEST{os.urandom(3).hex().upper()}"
        create_c_res = create_coupon_db({
            "code": coupon_code,
            "discount_type": "PERCENT",
            "discount_value": 15,
            "max_uses": 50,
            "description": "15% off test coupon"
        })
        self.assertTrue(create_c_res.get("success", False))

        # Validate Coupon
        val_res = validate_coupon_db(coupon_code, plan_id="professional", subtotal=2990)
        self.assertTrue(val_res.get("valid", False))
        self.assertGreater(val_res.get("discount_amount", 0), 0)

        # Read All Coupons
        all_coupons = get_all_coupons_admin()
        self.assertTrue(any(c["code"] == coupon_code for c in all_coupons))

        # Delete Coupon
        del_c_res = delete_coupon_db(coupon_code)
        self.assertTrue(del_c_res.get("success", False))

        # 2. INVOICES & PAYMENTS CRUD
        # Create test org for invoice
        org_id = create_organization_db(f"Inv Org {os.urandom(2).hex()}", f"inv-org-{os.urandom(2).hex()}", "STARTER")
        inv_res = generate_invoice_db({
            "org_id": org_id,
            "plan_id": "starter",
            "billing_interval": "MONTHLY",
            "subtotal": 1490,
            "discount_amount": 0,
            "tax_amount": 104,
            "total_amount": 1594,
            "payment_method": "CREDIT_CARD",
            "status": "PAID"
        })
        self.assertTrue(inv_res.get("success", False))
        inv_num = inv_res.get("invoice_number")
        self.assertIsNotNone(inv_num)

        # Read Org Invoices
        invoices = get_org_invoices(org_id)
        self.assertTrue(any(i["invoice_number"] == inv_num for i in invoices))

        # Record Payment Transaction
        pay_res = record_payment_transaction_db({
            "org_id": org_id,
            "invoice_number": inv_num,
            "amount": 1594,
            "payment_method": "CREDIT_CARD",
            "transaction_ref": f"TXN_{os.urandom(4).hex()}",
            "status": "SUCCESS"
        })
        self.assertTrue(pay_res.get("success", False))

        # Clean up
        conn = get_db_connection()
        conn.cursor().execute("DELETE FROM payment_transactions WHERE org_id = ?", (org_id,))
        conn.cursor().execute("DELETE FROM invoices WHERE org_id = ?", (org_id,))
        conn.cursor().execute("DELETE FROM organizations WHERE id = ?", (org_id,))
        conn.commit()
        conn.close()

    # ================= 8. CRM LEADS CRUD =================
    def test_08_crm_leads_crud(self):
        lead_email = f"lead_{os.urandom(3).hex()}@example.com"
        create_res = create_crm_lead({
            "company_name": "Autoparts Super Store",
            "contact_person": "Wichai Leads",
            "email": lead_email,
            "phone": "089-999-8888",
            "pipeline_stage": "LEAD",
            "interested_plan_id": "business",
            "expected_mrr": 5990,
            "notes": "Interested in 10 branches deployment"
        })
        self.assertTrue(create_res.get("success", False))
        lead_id = create_res.get("lead_id")
        self.assertIsNotNone(lead_id)

        # Read Leads
        leads = get_crm_leads_db()
        found_lead = next((l for l in leads if l["id"] == lead_id), None)
        self.assertIsNotNone(found_lead)
        self.assertEqual(found_lead["contact_person"], "Wichai Leads")

        # Update Lead Stage (using valid CHECK enum 'CONTACTED')
        update_res = update_crm_lead_stage_db(lead_id, "CONTACTED", notes="Contacted via phone, moving to demo")
        self.assertTrue(update_res.get("success", False))

        leads_updated = get_crm_leads_db()
        lead_up = next((l for l in leads_updated if l["id"] == lead_id), None)
        self.assertEqual(lead_up["pipeline_stage"], "CONTACTED")

        # Clean up
        conn = get_db_connection()
        conn.cursor().execute("DELETE FROM customer_leads WHERE id = ?", (lead_id,))
        conn.commit()
        conn.close()

    # ================= 9. FAVORITES & SEARCH HISTORY CRUD =================
    def test_09_favorites_and_search_history_crud(self):
        test_email = f"fav_user_{os.urandom(3).hex()}@example.com"
        pwd_hash = hashlib.sha256("Password123!".encode()).hexdigest()
        res_u = create_db_user(test_email, pwd_hash, "STAFF")
        u_id = res_u["user_id"]
        org_id = create_organization_db(f"Fav Org {os.urandom(2).hex()}", f"fav-org-{os.urandom(2).hex()}", "PROFESSIONAL")
        invite_org_member(org_id, u_id, "OWNER")

        # 1. Toggle Favorite (ADD)
        fav_add_res = toggle_user_favorite(u_id, org_id, 1, "MASTER", {"part_number": "CRUD-FAV-01", "brand": "TOYOTA"})
        self.assertTrue(fav_add_res.get("success", False))
        self.assertTrue(fav_add_res.get("favorited", False))

        # 2. Read Favorites
        favs = get_user_favorites(u_id, org_id)
        self.assertEqual(len(favs), 1)
        self.assertEqual(favs[0]["part_id"], 1)

        # 3. Toggle Favorite (REMOVE)
        fav_rem_res = toggle_user_favorite(u_id, org_id, 1, "MASTER")
        self.assertTrue(fav_rem_res.get("success", False))
        self.assertFalse(fav_rem_res.get("favorited", True))

        favs_empty = get_user_favorites(u_id, org_id)
        self.assertEqual(len(favs_empty), 0)

        # 4. Search Usage & History CRUD
        record_search_usage(org_id=org_id, user_id=u_id, query="Toyota Brake Pad CRUD Test", search_type="SEARCH", results_count=5)
        history = get_org_search_history(org_id, limit=10)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["search_query"], "Toyota Brake Pad CRUD Test")

        # Delete Search Log
        log_id = history[0]["id"]
        del_log_res = delete_search_log(log_id, org_id)
        self.assertTrue(del_log_res.get("success", False))

        history_empty = get_org_search_history(org_id, limit=10)
        self.assertEqual(len(history_empty), 0)

        # Clean up
        conn = get_db_connection()
        conn.cursor().execute("DELETE FROM organization_members WHERE org_id = ?", (org_id,))
        conn.cursor().execute("DELETE FROM organizations WHERE id = ?", (org_id,))
        conn.cursor().execute("DELETE FROM users WHERE id = ?", (u_id,))
        conn.commit()
        conn.close()

    # ================= 10. API KEYS CRUD =================
    def test_10_api_keys_crud(self):
        org_id = create_organization_db(f"API Org {os.urandom(2).hex()}", f"api-org-{os.urandom(2).hex()}", "BUSINESS")
        
        # 1. CREATE API Key
        key_res = create_api_key(org_id, name="Test Production API Key", rate_limit=120)
        self.assertTrue(key_res.get("success", False))
        raw_key = key_res.get("raw_key")
        self.assertIsNotNone(raw_key)

        # 2. READ API Keys
        keys = get_api_keys(org_id)
        self.assertGreater(len(keys), 0)
        key_id = keys[0]["id"]
        self.assertEqual(keys[0]["name"], "Test Production API Key")

        # 3. REVOKE / DELETE API Key
        del_res = delete_api_key(org_id, key_id)
        self.assertTrue(del_res.get("success", False))

        keys_after = get_api_keys(org_id)
        self.assertEqual(len(keys_after), 0)

        # Clean up
        conn = get_db_connection()
        conn.cursor().execute("DELETE FROM organizations WHERE id = ?", (org_id,))
        conn.commit()
        conn.close()

    # ================= 11. PLATFORM SETTINGS CRUD =================
    def test_11_platform_settings_crud(self):
        settings_before = get_platform_settings()
        self.assertIsNotNone(settings_before)

        # UPDATE Settings
        updated_payload = {
            "site_title": "AutoParts Pro Cross-Reference SaaS",
            "contact_email": "support@autoparts-saas.com",
            "vat_percentage": 7.0,
            "navbar_style": "glassmorphic"
        }
        update_res = update_platform_settings(updated_payload)
        self.assertTrue(update_res)

        # READ Settings to verify persistence
        settings_after = get_platform_settings()
        self.assertEqual(settings_after.get("site_title"), "AutoParts Pro Cross-Reference SaaS")
        self.assertEqual(settings_after.get("contact_email"), "support@autoparts-saas.com")

if __name__ == "__main__":
    unittest.main()
