import datetime
from typing import Optional, Dict, Any, Tuple, List
from backend.database import (
    get_db_connection,
    log_commercial_audit,
    get_plan_details,
    save_subscription_entitlements_snapshot,
    update_subscription_items
)

class SubscriptionStateMachine:
    """
    Finite State Machine for Subscription Lifecycle Management.
    Governs strict state transitions, renewal, trial expiry, cancellation, suspension, and reactivation.
    """

    ALLOWED_TRANSITIONS = {
        "TRIAL": ["ACTIVE", "EXPIRED", "SUSPENDED", "CANCELLED"],
        "TRIALING": ["ACTIVE", "EXPIRED", "SUSPENDED", "CANCELLED"],
        "ACTIVE": ["PAST_DUE", "GRACE_PERIOD", "CANCELLED", "ACTIVE"],
        "PAST_DUE": ["ACTIVE", "GRACE_PERIOD", "SUSPENDED", "EXPIRED"],
        "GRACE_PERIOD": ["ACTIVE", "SUSPENDED", "EXPIRED"],
        "SUSPENDED": ["ACTIVE", "EXPIRED"],
        "CANCELLED": ["ACTIVE", "EXPIRED"],
        "CANCELED": ["ACTIVE", "EXPIRED"],
        "EXPIRED": ["ACTIVE"]
    }

    @classmethod
    def can_transition(cls, current_state: str, target_state: str) -> bool:
        curr = current_state.upper()
        target = target_state.upper()
        return target in cls.ALLOWED_TRANSITIONS.get(curr, [])

    @classmethod
    def transition_state(
        cls,
        org_id: int,
        target_state: str,
        actor_user_id: Optional[int] = None,
        actor_username: str = "system",
        reason: Optional[str] = None
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Executes a validated state transition on the organization's subscription.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM subscriptions WHERE org_id = ?", (org_id,))
        sub = cursor.fetchone()
        if not sub:
            conn.close()
            return False, "No subscription found for this organization.", None

        current_state = sub["status"].upper()
        target = target_state.upper()

        if current_state == target:
            conn.close()
            return True, f"Subscription is already {target}.", dict(sub)

        if not cls.can_transition(current_state, target):
            conn.close()
            return False, f"Illegal state transition from {current_state} to {target}.", None

        # Execute transition updates
        updates = ["status = ?"]
        params = [target]

        if target == "CANCELLED":
            updates.append("cancel_at_period_end = 1")
            updates.append("cancelled_at = CURRENT_TIMESTAMP")
        elif target == "ACTIVE":
            updates.append("cancel_at_period_end = 0")
        elif target == "GRACE_PERIOD":
            updates.append("grace_period_end = datetime('now', '+7 days')")

        params.append(org_id)
        cursor.execute(f"UPDATE subscriptions SET {', '.join(updates)} WHERE org_id = ?", tuple(params))
        conn.commit()

        # Fetch updated subscription
        cursor.execute("SELECT * FROM subscriptions WHERE org_id = ?", (org_id,))
        updated_sub = dict(cursor.fetchone())
        conn.close()

        # Audit log
        log_commercial_audit(
            org_id=org_id,
            actor_user_id=actor_user_id,
            actor_username=actor_username,
            action=f"TRANSITION_TO_{target}",
            target_type="SUBSCRIPTION",
            target_id=str(sub["id"]),
            before_state=f"status={current_state}",
            after_state=f"status={target}, reason={reason or 'standard'}"
        )

        return True, f"Subscription transitioned from {current_state} to {target}.", updated_sub

    @staticmethod
    def execute_plan_upgrade_or_change(
        org_id: int,
        new_plan_id: str,
        interval: str = 'MONTHLY',
        add_on_ids: Optional[List[str]] = None,
        pricing_breakdown: Optional[Dict[str, Any]] = None,
        actor_user_id: Optional[int] = None,
        actor_username: str = "customer"
    ) -> Tuple[bool, str, Optional[Dict[str, Any]]]:
        """
        Executes plan upgrade or modification, itemizes line items, and takes a snapshot of new entitlements.
        """
        add_on_ids = add_on_ids or []
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM subscriptions WHERE org_id = ?", (org_id,))
        sub = cursor.fetchone()
        if not sub:
            conn.close()
            return False, "Subscription not found.", None

        sub_id = sub["id"]
        old_plan = sub["plan_id"]

        # Fetch new plan details & version
        plan_details = get_plan_details(new_plan_id, interval)
        if not plan_details:
            conn.close()
            return False, f"Plan {new_plan_id} ({interval}) not found.", None

        # Period calculation (new 30 days or 365 days)
        now = datetime.datetime.now()
        days_to_add = 365 if interval.upper() == 'YEARLY' else 30
        period_end = now + datetime.timedelta(days=days_to_add)

        base_p = pricing_breakdown.get("base_price", plan_details["base_price"]) if pricing_breakdown else plan_details["base_price"]
        disc_p = pricing_breakdown.get("discount_amount", 0) if pricing_breakdown else 0
        tax_p = pricing_breakdown.get("tax_amount", 0) if pricing_breakdown else 0
        tot_p = pricing_breakdown.get("total_amount", base_p + tax_p - disc_p) if pricing_breakdown else (base_p + tax_p - disc_p)

        cursor.execute("""
            UPDATE subscriptions SET
                plan_id = ?,
                plan_version_id = ?,
                billing_cycle = ?,
                billing_interval = ?,
                status = 'ACTIVE',
                cancel_at_period_end = 0,
                current_period_start = ?,
                current_period_end = ?,
                base_price = ?,
                discount_amount = ?,
                tax_amount = ?,
                total_amount = ?
            WHERE org_id = ?
        """, (
            new_plan_id.lower(),
            plan_details.get("id", 1),
            interval.upper(),
            interval.upper(),
            now.strftime("%Y-%m-%d %H:%M:%S"),
            period_end.strftime("%Y-%m-%d %H:%M:%S"),
            base_p,
            disc_p,
            tax_p,
            tot_p,
            org_id
        ))

        # Also update organization plan_tier display
        cursor.execute("UPDATE organizations SET plan_tier = ? WHERE id = ?", (new_plan_id.upper(), org_id))
        conn.commit()
        conn.close()

        # Update subscription item breakdown
        update_subscription_items(sub_id, new_plan_id, interval, add_on_ids)

        # Freeze effective entitlements snapshot
        snapshot = {
            "plan_version_id": plan_details.get("id", 1),
            "max_brands": plan_details.get("max_brands", -1),
            "max_categories": plan_details.get("max_categories", -1),
            "max_users": plan_details.get("max_users", 5),
            "monthly_search_quota": plan_details.get("monthly_search_quota", 5000),
            "vin_search_enabled": any(f["feature_code"] == "VIN_SEARCH" and f["is_included"] for f in plan_details.get("features", [])),
            "api_access_enabled": any(f["feature_code"] == "API" and f["is_included"] for f in plan_details.get("features", [])) or "api_access_pack" in add_on_ids,
            "export_enabled": any(f["feature_code"] == "EXPORT" and f["is_included"] for f in plan_details.get("features", [])) or "export_pack" in add_on_ids,
            "ai_search_enabled": any(f["feature_code"] == "AI" and f["is_included"] for f in plan_details.get("features", [])) or "ai_power_pack" in add_on_ids
        }
        save_subscription_entitlements_snapshot(sub_id, snapshot)

        log_commercial_audit(
            org_id=org_id,
            actor_user_id=actor_user_id,
            actor_username=actor_username,
            action="UPGRADE_PLAN",
            target_type="SUBSCRIPTION",
            target_id=str(sub_id),
            before_state=f"plan={old_plan}",
            after_state=f"plan={new_plan_id}, interval={interval}, total={tot_p}"
        )

        return True, f"Successfully upgraded subscription to {plan_details['plan_name']}.", snapshot
