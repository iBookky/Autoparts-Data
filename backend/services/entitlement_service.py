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
        custom_aftermarket = [r["entitlement_value"] for r in ent_rows if r["entitlement_type"] == "AFTERMARKET_BRAND"]

        # Derive allowed brands (Vehicle makes are universally available unless custom-restricted)
        if custom_brands:
            allowed_brands = custom_brands
        else:
            allowed_brands = ['*']

        # Derive allowed categories (Customer must have explicit purchased categories or unlimited plan)
        if custom_cats:
            allowed_categories = custom_cats
        elif max_c == -1 or plan_id in ['business', 'enterprise']:
            allowed_categories = ['*']  # All categories allowed for unlimited plans
        else:
            allowed_categories = []

        # Derive allowed aftermarket brands (Governed by plan aftermarket entitlements if configured)
        if custom_aftermarket:
            allowed_aftermarket_brands = custom_aftermarket
        else:
            allowed_aftermarket_brands = ['*']  # Default open if no specific aftermarket restrictions configured

        conn.close()

        return {
            "status": sub["status"],
            "plan_id": plan_id,
            "allowed_brands": allowed_brands,
            "allowed_categories": allowed_categories,
            "allowed_aftermarket_brands": allowed_aftermarket_brands,
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
        category: Optional[str] = None,
        aftermarket_brand: Optional[str] = None
    ) -> Tuple[bool, Optional[Dict[str, Any]], Dict[str, Any]]:
        """
        Validates whether the user's organization is entitled to perform this search.
        Returns: (is_allowed, locked_payload_or_none, tenant_context)
        """
        # Privileged system operator / system owner accounts have unrestricted access across all functions
        norm_user = (username or "").strip().lower()
        norm_role = (user_role or "").strip().upper()
        is_unrestricted = (
            norm_role in ["OWNER", "SUPER_ADMIN", "ADMIN"]
            or norm_user in ["owner", "superadmin", "admin"]
        )
        if is_unrestricted:
            ctx = get_user_tenant_context(username) or {}
            org = ctx.get("organization") or {"id": 1, "name": "Platform Master HQ", "slug": "default", "plan_tier": "ENTERPRISE"}
            sub = ctx.get("subscription") or {"status": "ACTIVE", "plan_name": "SYSTEM OWNER (UNLIMITED)", "plan_id": "enterprise"}
            usage = ctx.get("usage") or {"searches_used": 0, "searches_quota": 999999999}
            
            sub["status"] = "ACTIVE"
            sub["plan_id"] = "enterprise"
            sub["plan_name"] = "SYSTEM OWNER (UNLIMITED)"
            sub["monthly_search_quota"] = 999999999
            sub["max_brands"] = -1
            sub["max_categories"] = -1
            sub["max_users"] = -1
            sub["vin_search_enabled"] = 1
            sub["api_access_enabled"] = 1
            sub["export_enabled"] = 1
            sub["ai_search_enabled"] = 1
            usage["searches_quota"] = 999999999
            
            ctx["organization"] = org
            ctx["subscription"] = sub
            ctx["usage"] = usage
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
        if '*' not in whitelist["allowed_categories"] and len(whitelist["allowed_categories"]) == 0:
            locked = {
                "locked": True,
                "reason": "CATEGORY_LOCKED",
                "locked_entity_type": "CATEGORY",
                "message": "No product categories have been assigned to your subscription. Please select or purchase product categories to access automotive parts data.",
                "action": "ADD_CATEGORY",
                "plan_id": whitelist["plan_id"],
                "allowed_categories": []
            }
            return False, locked, ctx

        if category and '*' not in whitelist["allowed_categories"]:
            matched_cat = any(c.lower() in category.strip().lower() or category.strip().lower() in c.lower() for c in whitelist["allowed_categories"])
            if not matched_cat:
                locked = {
                    "locked": True,
                    "reason": "CATEGORY_LOCKED",
                    "locked_entity_type": "CATEGORY",
                    "locked_entity_name": category,
                    "message": f"Data for category '{category}' is not included in your purchased product categories.",
                    "action": "ADD_CATEGORY",
                    "plan_id": whitelist["plan_id"],
                    "upgrade_price_thb": 500,
                    "allowed_categories": whitelist["allowed_categories"]
                }
                return False, locked, ctx

        # 5. Aftermarket Brand Whitelist Check
        if aftermarket_brand and '*' not in whitelist.get("allowed_aftermarket_brands", ['*']):
            matched_ab = any(b.lower() == aftermarket_brand.strip().lower() for b in whitelist["allowed_aftermarket_brands"])
            if not matched_ab:
                locked = {
                    "locked": True,
                    "reason": "AFTERMARKET_BRAND_LOCKED",
                    "locked_entity_type": "AFTERMARKET_BRAND",
                    "locked_entity_name": aftermarket_brand,
                    "message": f"Data for aftermarket brand '{aftermarket_brand}' is not included in your {whitelist['plan_id'].upper()} plan.",
                    "action": "ADD_AFTERMARKET_BRAND",
                    "plan_id": whitelist["plan_id"],
                    "upgrade_price_thb": 500,
                    "allowed_aftermarket_brands": whitelist["allowed_aftermarket_brands"]
                }
                return False, locked, ctx

        return True, None, ctx

    @staticmethod
    def validate_product_access(username: str, user_role: str, part_id: int, source: str = "MASTER") -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Validates whether the customer is entitled to view a specific product's full technical specs.
        Prevents direct URL manipulation (e.g. /products/123).
        """
        norm_user = (username or "").strip().lower()
        norm_role = (user_role or "").strip().upper()
        is_unrestricted = (
            norm_role in ["OWNER", "SUPER_ADMIN", "ADMIN"]
            or norm_user in ["owner", "superadmin", "admin"]
        )
        if is_unrestricted:
            return True, None

        conn = get_db_connection()
        cursor = conn.cursor()
        table = "master_parts" if source.upper() == "MASTER" else "temp_parts"
        cursor.execute(f"SELECT brand, car_brand, category FROM {table} WHERE id = ?", (part_id,))
        row = cursor.fetchone()
        if not row and source.upper() == "MASTER":
            cursor.execute("SELECT brand, car_brand, category FROM temp_parts WHERE id = ?", (part_id,))
            row = cursor.fetchone()
        conn.close()

        if not row:
            return False, {"locked": True, "reason": "NOT_FOUND", "message": "Product not found."}

        brand = row["car_brand"]
        cat = row["category"]
        part_brand = row["brand"]
        allowed, locked_payload, _ = EntitlementService.validate_search_access(
            username, user_role, car_brand=brand, category=cat, aftermarket_brand=part_brand
        )
        return allowed, locked_payload
