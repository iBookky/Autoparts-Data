import math
from typing import Optional, Dict, Any, List, Tuple
from backend.database import (
    get_plan_details,
    get_add_on_details,
    validate_coupon_for_tenant,
    get_coupon
)

class BillingCalculator:
    """
    Centralized, configuration-driven billing calculation engine.
    Calculates Base Prices, Add-ons, Discounts, VAT (7%), and Proration on Upgrades/Downgrades.
    """

    DEFAULT_TAX_RATE = 0.07  # Thai VAT 7%

    @staticmethod
    def calculate_base_price(plan_id: str, interval: str = 'MONTHLY') -> Tuple[int, Dict[str, Any]]:
        plan = get_plan_details(plan_id, interval)
        if not plan:
            raise ValueError(f"Plan '{plan_id}' with interval '{interval}' not found or inactive.")
        return int(plan["base_price"]), plan

    @staticmethod
    def calculate_add_ons(add_on_ids: List[str], interval: str = 'MONTHLY') -> Tuple[int, List[Dict[str, Any]]]:
        total_addons = 0
        items = []
        for aid in add_on_ids:
            addon = get_add_on_details(aid)
            if addon and addon["status"] == "ACTIVE":
                price = addon["price_yearly"] if interval.upper() == "YEARLY" else addon["price_monthly"]
                total_addons += price
                items.append({
                    "id": addon["id"],
                    "name": addon["name"],
                    "code": addon["code"],
                    "price": price,
                    "interval": interval.upper()
                })
        return total_addons, items

    @staticmethod
    def calculate_discount(subtotal: int, coupon: Optional[Dict[str, Any]]) -> int:
        if not coupon or not coupon.get("is_active"):
            return 0
        
        dtype = coupon["discount_type"].upper()
        dval = float(coupon["discount_value"])
        
        if dtype == "PERCENT":
            discount = int(round(subtotal * (dval / 100.0)))
        elif dtype == "FIXED":
            discount = int(dval)
        else:
            discount = 0

        # Apply maximum discount cap if specified
        max_disc = coupon.get("max_discount", -1)
        if max_disc > 0:
            discount = min(discount, int(max_disc))

        # Discount cannot exceed subtotal
        return min(discount, subtotal)

    @staticmethod
    def calculate_tax(taxable_amount: int, tax_rate: float = DEFAULT_TAX_RATE, tax_inclusive: bool = False) -> int:
        if tax_inclusive:
            # e.g. 7% included in price: vat = total - (total / 1.07)
            vat = taxable_amount - (taxable_amount / (1.0 + tax_rate))
            return int(round(vat))
        else:
            # 7% added to subtotal
            vat = taxable_amount * tax_rate
            return int(round(vat))

    @staticmethod
    def calculate_proration(
        current_sub_total: int,
        new_sub_total: int,
        days_in_period: int,
        days_remaining: int
    ) -> Dict[str, Any]:
        """
        Calculates fair prorated billing difference when upgrading or changing subscription midway.
        """
        if days_in_period <= 0 or days_remaining <= 0:
            return {
                "unused_credit": 0,
                "prorated_new_charge": 0,
                "net_proration": 0,
                "days_remaining": 0,
                "days_in_period": days_in_period
            }
        
        days_remaining = min(days_remaining, days_in_period)
        fraction = days_remaining / float(days_in_period)
        
        unused_credit = int(round(current_sub_total * fraction))
        prorated_new_charge = int(round(new_sub_total * fraction))
        net_proration = prorated_new_charge - unused_credit

        return {
            "unused_credit": unused_credit,
            "prorated_new_charge": prorated_new_charge,
            "net_proration": net_proration,
            "days_remaining": days_remaining,
            "days_in_period": days_in_period
        }

    @classmethod
    def calculate_checkout(
        cls,
        plan_id: str,
        interval: str = 'MONTHLY',
        add_on_ids: Optional[List[str]] = None,
        coupon_code: Optional[str] = None,
        org_id: Optional[int] = None,
        is_prorated: bool = False,
        current_sub_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Comprehensive checkout calculation producing full pricing breakdown, line items, VAT, and Net Total.
        """
        add_on_ids = add_on_ids or []
        base_price, plan_details = cls.calculate_base_price(plan_id, interval)
        addons_total, addon_items = cls.calculate_add_ons(add_on_ids, interval)
        
        raw_subtotal = base_price + addons_total
        
        # Coupon Discount
        coupon_dict = None
        discount_amount = 0
        if coupon_code and org_id:
            ok, msg, coupon_dict = validate_coupon_for_tenant(coupon_code, org_id, plan_id, raw_subtotal)
            if ok and coupon_dict:
                discount_amount = cls.calculate_discount(raw_subtotal, coupon_dict)

        discounted_subtotal = max(0, raw_subtotal - discount_amount)
        
        # Proration Calculation if active subscription exists
        proration_info = None
        prorated_subtotal = discounted_subtotal
        if is_prorated and current_sub_data:
            days_in_period = current_sub_data.get("days_in_period", 30)
            days_remaining = current_sub_data.get("days_remaining", 15)
            current_total = current_sub_data.get("current_total", 0)
            
            proration_info = cls.calculate_proration(
                current_sub_total=current_total,
                new_sub_total=discounted_subtotal,
                days_in_period=days_in_period,
                days_remaining=days_remaining
            )
            prorated_subtotal = max(0, proration_info["net_proration"])

        # VAT 7%
        taxable_amount = prorated_subtotal if is_prorated else discounted_subtotal
        tax_amount = cls.calculate_tax(taxable_amount, cls.DEFAULT_TAX_RATE)
        total_amount = taxable_amount + tax_amount

        # Line Items
        line_items = [
            {
                "description": f"{plan_details['plan_name']} Plan ({interval.capitalize()})",
                "item_type": "PLAN",
                "quantity": 1,
                "unit_price": base_price,
                "amount": base_price
            }
        ]

        for a in addon_items:
            line_items.append({
                "description": f"Add-on: {a['name']}",
                "item_type": "ADD_ON",
                "quantity": 1,
                "unit_price": a["price"],
                "amount": a["price"]
            })

        if discount_amount > 0:
            line_items.append({
                "description": f"Coupon Discount ({coupon_code.upper() if coupon_code else 'DISCOUNT'})",
                "item_type": "DISCOUNT",
                "quantity": 1,
                "unit_price": -discount_amount,
                "amount": -discount_amount
            })

        if proration_info and proration_info["unused_credit"] > 0:
            line_items.append({
                "description": f"Unused Credit from previous plan ({proration_info['days_remaining']} days remaining)",
                "item_type": "PRORATION_CREDIT",
                "quantity": 1,
                "unit_price": -proration_info["unused_credit"],
                "amount": -proration_info["unused_credit"]
            })

        return {
            "plan_id": plan_id,
            "plan_name": plan_details["plan_name"],
            "interval": interval.upper(),
            "currency": plan_details.get("currency", "THB"),
            "base_price": base_price,
            "addons_total": addons_total,
            "subtotal": raw_subtotal,
            "discount_amount": discount_amount,
            "tax_amount": tax_amount,
            "tax_rate": cls.DEFAULT_TAX_RATE,
            "total_amount": total_amount,
            "proration": proration_info,
            "line_items": line_items,
            "coupon_applied": coupon_code if discount_amount > 0 else None
        }
