import re
from typing import Optional, Dict, Any, List, Tuple
from fastapi import HTTPException
from backend.database import (
    get_db_connection,
    get_user_tenant_context,
    get_org_subscription,
    get_org_data_coverage,
    record_search_usage
)

def normalize_part_number(val: Optional[str]) -> str:
    """
    Normalizes automotive part numbers and OEM codes by stripping
    spaces, dashes, dots, and converting to uppercase.
    Example: '90915-YZZD1' -> '90915YZZD1'
    """
    if not val:
        return ""
    return re.sub(r'[\s\-_.\/]+', '', str(val)).upper()

class EntitlementService:
    """
    Centralized Entitlement & Quota Protection Service for B2B SaaS Multi-Tenant Access.
    """

    @staticmethod
    def get_organization_whitelist(org_id: int) -> Dict[str, Any]:
        """
        Retrieves the exact database-driven whitelist for an organization:
        - allowed_brands: List of permitted car brands (or ['*'] for all)
        - allowed_categories: List of permitted categories (or ['*'] for all)
        - subscription_status: ACTIVE, TRIAL, PAST_DUE, SUSPENDED, CANCELLED, EXPIRED
        - max_brands: Limit integer (-1 for unlimited)
        - max_categories: Limit integer (-1 for unlimited)
        """
        conn = get_db_connection()
        cursor = conn.cursor()

        # 1. Fetch Subscription & Snapshot/Plan Limits
        cursor.execute("""
            SELECT s.id as sub_id, s.status, s.plan_id, s.plan_version_id, s.billing_interval,
                   s.extra_brands, s.extra_categories,
                   p.max_brands, p.max_categories, p.monthly_search_quota,
                   p.vin_search_enabled, p.api_access_enabled, p.export_enabled, p.ai_search_enabled
            FROM subscriptions s
            JOIN plans p ON p.id = s.plan_id
            WHERE s.org_id = ?
            LIMIT 1
        """, (org_id,))
        sub_row = cursor.fetchone()

        if not sub_row:
            conn.close()
            return {
                "status": "ACTIVE",
                "plan_id": "professional",
                "allowed_brands": ["Toyota", "Honda", "Isuzu", "Mitsubishi", "Ford"],
                "allowed_categories": ["ระบบเบรก", "ระบบกรอง", "ระบบช่วงล่าง"],
                "max_brands": 5,
                "max_categories": 3,
                "vin_search_enabled": True,
                "api_access_enabled": False,
                "export_enabled": False,
                "ai_search_enabled": True
            }

        sub = dict(sub_row)
        plan_id = sub["plan_id"].lower()
        sub_id = sub["sub_id"]

        # Check if an entitlements snapshot exists for this subscription
        cursor.execute("SELECT * FROM subscription_entitlements_snapshot WHERE subscription_id = ? ORDER BY id DESC LIMIT 1", (sub_id,))
        snap_row = cursor.fetchone()

        # Check attached add-ons from subscription_items
        cursor.execute("SELECT item_code FROM subscription_items WHERE subscription_id = ? AND item_type = 'ADD_ON'", (sub_id,))
        addon_codes = [r["item_code"] for r in cursor.fetchall()]

        if snap_row:
            snap = dict(snap_row)
            max_b = snap.get("max_brands", 5)
            max_c = snap.get("max_categories", 3)
            vin_enabled = bool(snap.get("vin_search_enabled", True))
            api_enabled = bool(snap.get("api_access_enabled", False)) or bool(snap.get("api_enabled", False)) or "api_access_pack" in addon_codes
            export_enabled = False  # Permanent security rule: EXPORT_AUTOMOTIVE_DATA = DENIED for customers
            ai_enabled = bool(snap.get("ai_search_enabled", True)) or bool(snap.get("ai_enabled", True)) or "ai_power_pack" in addon_codes
        else:
            max_b = sub.get("max_brands", 5) + (sub.get("extra_brands") or 0) if sub.get("max_brands", 5) != -1 else -1
            max_c = sub.get("max_categories", 3) + (sub.get("extra_categories") or 0) if sub.get("max_categories", 3) != -1 else -1
            vin_enabled = bool(sub.get("vin_search_enabled", True))
            api_enabled = bool(sub.get("api_access_enabled", False)) or bool(sub.get("api_enabled", False)) or "api_access_pack" in addon_codes
            export_enabled = False  # Permanent security rule: EXPORT_AUTOMOTIVE_DATA = DENIED for customers
            ai_enabled = bool(sub.get("ai_search_enabled", True)) or bool(sub.get("ai_enabled", True)) or "ai_power_pack" in addon_codes


        # 2. Check explicit database-driven entitlements table first
        cursor.execute("SELECT entitlement_type, entitlement_value FROM entitlements WHERE org_id = ? AND is_granted = 1", (org_id,))
        ent_rows = cursor.fetchall()

        custom_brands = [r["entitlement_value"] for r in ent_rows if r["entitlement_type"] == "BRAND"]
        custom_cats = [r["entitlement_value"] for r in ent_rows if r["entitlement_type"] == "CATEGORY"]

        # If custom entitlements are defined, use them directly
        if custom_brands or custom_cats:
            allowed_brands = custom_brands if custom_brands else ['*'] if max_b == -1 else []
            allowed_cats = custom_cats if custom_cats else ['*'] if max_c == -1 else []
        else:
            # Derive standard catalog slice based on plan limits
            if max_b == -1 or plan_id in ['business', 'enterprise']:
                allowed_brands = ['*'] # All brands allowed
            else:
                cursor.execute("SELECT name FROM meta_car_brands ORDER BY id ASC LIMIT ?", (max_b,))
                allowed_brands = [r["name"] for r in cursor.fetchall()]

            if max_c == -1 or plan_id in ['business', 'enterprise']:
                allowed_cats = ['*'] # All categories allowed
            else:
                cursor.execute("SELECT name FROM meta_categories ORDER BY id ASC LIMIT ?", (max_c,))
                allowed_cats = [r["name"] for r in cursor.fetchall()]

        conn.close()

        return {
            "status": sub["status"],
            "plan_id": plan_id,
            "allowed_brands": allowed_brands,
            "allowed_categories": allowed_cats,
            "max_brands": max_b,
            "max_categories": max_c,
            "vin_search_enabled": vin_enabled,
            "api_access_enabled": api_enabled,
            "export_enabled": export_enabled,
            "ai_search_enabled": ai_enabled
        }

    @staticmethod
    def validate_search_access(
        username: str,
        user_role: str,
        car_brand: Optional[str] = None,
        category: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Dict[str, Any]]:
        """
        Validates whether the user's organization is entitled to perform this search.
        Returns: (is_allowed, locked_payload_or_none, tenant_context)
        """
        # Privileged system operator accounts have unrestricted search access
        if user_role in ["OWNER", "SUPER_ADMIN"] or (user_role in ["ADMIN", "STAFF"] and username in ["superadmin", "admin", "staff"]):
            ctx = get_user_tenant_context(username) or {
                "organization": {"id": 1, "name": "System Operator"},
                "subscription": {"status": "ACTIVE", "plan_name": "ENTERPRISE"},
                "usage": {"searches_used": 0, "searches_quota": 999999}
            }
            return True, None, ctx

        ctx = get_user_tenant_context(username)
        if not ctx:
            raise HTTPException(status_code=401, detail="Unauthorized customer session")

        org = ctx["organization"]
        sub = ctx["subscription"]
        usage = ctx["usage"]
        whitelist = EntitlementService.get_organization_whitelist(org["id"])

        # 0. User Membership Status Check (SUSPENDED / DISABLED)
        member_status = ctx.get("membership", {}).get("status", "ACTIVE")
        if member_status in ["SUSPENDED", "DISABLED"]:
            locked = {
                "locked": True,
                "reason": "MEMBER_SUSPENDED",
                "message": f"Your team access in this organization has been {member_status.lower()}. Please contact your Organization Owner.",
                "action": "CONTACT_OWNER"
            }
            return False, locked, ctx

        # 1. Subscription Status Check
        status = whitelist["status"]
        if status in ["SUSPENDED", "CANCELLED", "CANCELED", "PAST_DUE", "EXPIRED"]:
            locked = {
                "locked": True,
                "reason": "SUBSCRIPTION_INACTIVE",
                "message": f"Your subscription is currently {status}. Please reactivate your account to search automotive parts data.",
                "action": "RENEW_SUBSCRIPTION",
                "plan_id": whitelist["plan_id"]
            }
            return False, locked, ctx

        # 2. Monthly Search Quota Check
        if usage["searches_used"] >= usage["searches_quota"]:
            locked = {
                "locked": True,
                "reason": "QUOTA_EXCEEDED",
                "message": f"You have reached your monthly search limit ({usage['searches_used']:,} / {usage['searches_quota']:,} searches used).",
                "action": "UPGRADE_QUOTA",
                "plan_id": whitelist["plan_id"],
                "upgrade_options": [
                    {"name": "+5,000 Extra Searches", "price_thb": 990},
                    {"name": "Upgrade to Business Plan", "price_thb": 5990}
                ]
            }
            return False, locked, ctx

        # 3. Brand Whitelist Check
        if car_brand and '*' not in whitelist["allowed_brands"]:
            matched_brand = any(b.lower() == car_brand.strip().lower() for b in whitelist["allowed_brands"])
            if not matched_brand:
                locked = {
                    "locked": True,
                    "reason": "BRAND_LOCKED",
                    "locked_entity_type": "BRAND",
                    "locked_entity_name": car_brand,
                    "message": f"Data for '{car_brand}' is not included in your {whitelist['plan_id'].upper()} plan.",
                    "action": "ADD_BRAND",
                    "plan_id": whitelist["plan_id"],
                    "upgrade_price_thb": 500,
                    "allowed_brands": whitelist["allowed_brands"]
                }
                return False, locked, ctx

        # 4. Category Whitelist Check
        if category and '*' not in whitelist["allowed_categories"]:
            matched_cat = any(c.lower() in category.strip().lower() or category.strip().lower() in c.lower() for c in whitelist["allowed_categories"])
            if not matched_cat:
                locked = {
                    "locked": True,
                    "reason": "CATEGORY_LOCKED",
                    "locked_entity_type": "CATEGORY",
                    "locked_entity_name": category,
                    "message": f"Data for category '{category}' is not included in your {whitelist['plan_id'].upper()} plan.",
                    "action": "ADD_CATEGORY",
                    "plan_id": whitelist["plan_id"],
                    "upgrade_price_thb": 500,
                    "allowed_categories": whitelist["allowed_categories"]
                }
                return False, locked, ctx

        return True, None, ctx

    @staticmethod
    def validate_product_access(username: str, user_role: str, part_id: int, source: str = "MASTER") -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validates whether the customer is entitled to view a specific product's full technical specs.
        Prevents direct URL manipulation (e.g. /products/123).
        """
        if user_role in ["OWNER", "SUPER_ADMIN", "ADMIN", "STAFF"]:
            return True, None

        conn = get_db_connection()
        cursor = conn.cursor()
        table = "master_parts" if source.upper() == "MASTER" else "temp_parts"
        cursor.execute(f"SELECT car_brand, category FROM {table} WHERE id = ?", (part_id,))
        row = cursor.fetchone()
        if not row and source.upper() == "MASTER":
            cursor.execute("SELECT car_brand, category FROM temp_parts WHERE id = ?", (part_id,))
            row = cursor.fetchone()
        conn.close()

        if not row:
            return False, {"locked": True, "reason": "NOT_FOUND", "message": "Product not found."}

        brand = row["car_brand"]
        cat = row["category"]
        allowed, locked_payload, _ = EntitlementService.validate_search_access(username, user_role, car_brand=brand, category=cat)
        return allowed, locked_payload
