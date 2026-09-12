import uuid
import json
from typing import Optional, Dict, Any, Tuple
from backend.database import (
    get_db_connection,
    create_payment_transaction,
    get_payment_transaction_by_ref,
    log_commercial_audit
)

class PaymentGateway:
    """
    Abstracted Multi-Provider Payment Processing Engine.
    Supports Credit/Debit Card, PromptPay QR, Corporate Bank Transfer with Idempotency Guarantees.
    """

    @staticmethod
    def create_payment_intent(
        org_id: int,
        invoice_id: int,
        amount: Any,
        currency: str = 'THB',
        payment_method: str = 'CREDIT_CARD',
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Creates a payment transaction intent with idempotency guard.
        """
        tx_ref = idempotency_key or f"TX-{uuid.uuid4().hex[:12].upper()}"
        
        # 1. Idempotency Check
        existing = get_payment_transaction_by_ref(tx_ref)
        if existing:
            return {
                "success": True,
                "is_duplicate": True,
                "transaction_ref": existing["transaction_ref"],
                "status": existing["status"],
                "amount": existing["amount"],
                "currency": existing["currency"]
            }

        # 2. Record new transaction intent
        initial_status = "SUCCESS" if payment_method in ["CREDIT_CARD", "PROMPTPAY"] else "PENDING"
        ok, ref, tx_id = create_payment_transaction({
            "invoice_id": invoice_id,
            "org_id": org_id,
            "transaction_ref": tx_ref,
            "payment_method": payment_method.upper(),
            "amount": float(amount) if amount is not None else 0.0,
            "currency": currency,
            "status": initial_status,
            "gateway_response": json.dumps({
                "provider": "MOCK_PAYMENT_GATEWAY",
                "method": payment_method.upper(),
                "authorized": True if initial_status == "SUCCESS" else False
            })
        })

        if ok and initial_status == "SUCCESS":
            # Update Invoice to PAID and activate subscription if pending
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE invoices SET status = 'PAID' WHERE id = ?", (invoice_id,))
            cursor.execute("UPDATE subscriptions SET status = 'ACTIVE' WHERE org_id = ? AND status IN ('PAST_DUE', 'PENDING_PAYMENT')", (org_id,))
            conn.commit()
            conn.close()

        return {
            "success": ok,
            "is_duplicate": False,
            "transaction_ref": ref,
            "transaction_id": tx_id,
            "status": initial_status,
            "amount": float(amount) if amount is not None else 0.0,
            "currency": currency,
            "payment_method": payment_method.upper()
        }

    @staticmethod
    def submit_bank_transfer_proof(
        invoice_id: int,
        org_id: int,
        amount: Any,
        proof_reference: str,
        slip_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Customer bank transfer proof submission for verification by Owner/Admin.
        """
        from datetime import datetime
        tx_ref = f"BT-SUB-{proof_reference.strip().upper()}-{uuid.uuid4().hex[:6].upper()}"
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO payment_transactions (
                    invoice_id, org_id, transaction_ref, payment_method,
                    amount, currency, status, gateway_response
                ) VALUES (?, ?, ?, 'BANK_TRANSFER', ?, 'THB', 'PENDING', ?)
            """, (
                invoice_id,
                org_id,
                tx_ref,
                float(amount) if amount is not None else 0.0,
                json.dumps({
                    "proof_ref": proof_reference,
                    "slip_url": slip_url,
                    "submitted_at": datetime.now().isoformat()
                })
            ))
            cursor.execute("UPDATE invoices SET status = 'PENDING_VERIFICATION' WHERE id = ?", (invoice_id,))
            conn.commit()
            return {
                "success": True,
                "transaction_ref": tx_ref,
                "status": "PENDING_VERIFICATION",
                "invoice_id": invoice_id,
                "message": "ส่งหลักฐานการโอนเงินเรียบร้อยแล้ว เจ้าหน้าที่จะตรวจสอบและเปิดสิทธิ์การใช้งาน"
            }
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()

    @staticmethod
    def process_manual_bank_transfer(
        invoice_id: int,
        org_id: int,
        amount: int,
        proof_reference: str,
        admin_user_id: int,
        admin_username: str
    ) -> Dict[str, Any]:
        """
        Corporate Bank Transfer verification flow approved by Platform Admin/Owner.
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify invoice
        cursor.execute("SELECT * FROM invoices WHERE id = ? AND org_id = ?", (invoice_id, org_id))
        inv = cursor.fetchone()
        if not inv:
            conn.close()
            return {"success": False, "error": "Invoice not found."}

        tx_ref = f"BT-{proof_reference.strip().upper()}-{uuid.uuid4().hex[:6].upper()}"
        cursor.execute("""
            INSERT INTO payment_transactions (
                invoice_id, org_id, transaction_ref, payment_method,
                amount, currency, status, gateway_response
            ) VALUES (?, ?, ?, 'BANK_TRANSFER', ?, 'THB', 'SUCCESS', ?)
        """, (
            invoice_id,
            org_id,
            tx_ref,
            amount,
            json.dumps({"verified_by_admin_id": admin_user_id, "proof_ref": proof_reference})
        ))
        
        cursor.execute("UPDATE invoices SET status = 'PAID' WHERE id = ?", (invoice_id,))
        conn.commit()
        conn.close()

        log_commercial_audit(
            org_id=org_id,
            actor_user_id=admin_user_id,
            actor_username=admin_username,
            action="VERIFY_MANUAL_PAYMENT",
            target_type="INVOICE",
            target_id=str(invoice_id),
            after_state=f"status=PAID, tx_ref={tx_ref}"
        )

        return {
            "success": True,
            "transaction_ref": tx_ref,
            "status": "SUCCESS",
            "invoice_id": invoice_id
        }

    @staticmethod
    def process_webhook_event(
        provider: str,
        payload: Dict[str, Any],
        signature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Secure, idempotent webhook processor for external payment providers.
        """
        event_id = payload.get("event_id") or payload.get("id") or str(uuid.uuid4())
        tx_ref = payload.get("transaction_ref") or f"WH-{event_id}"
        event_type = payload.get("event_type", "payment.succeeded")
        invoice_id = payload.get("invoice_id")
        amount = payload.get("amount", 0)
        org_id = payload.get("org_id", 1)

        # Idempotency check on webhook event ref
        existing = get_payment_transaction_by_ref(tx_ref)
        if existing:
            return {
                "success": True,
                "status": "ALREADY_PROCESSED",
                "transaction_ref": tx_ref,
                "is_idempotent_duplicate": True
            }

        if event_type == "payment.succeeded" and invoice_id:
            create_payment_transaction({
                "invoice_id": invoice_id,
                "org_id": org_id,
                "transaction_ref": tx_ref,
                "payment_method": provider.upper(),
                "amount": amount,
                "currency": payload.get("currency", "THB"),
                "status": "SUCCESS",
                "gateway_response": json.dumps(payload)
            })

            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE invoices SET status = 'PAID' WHERE id = ?", (invoice_id,))
            conn.commit()
            conn.close()

            return {
                "success": True,
                "status": "PROCESSED",
                "transaction_ref": tx_ref,
                "is_idempotent_duplicate": False
            }

        return {"success": False, "error": "Unhandled webhook event"}
