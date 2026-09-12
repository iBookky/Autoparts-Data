-- PostgreSQL Migration: 006_payment_gateway_settings.sql

CREATE TABLE IF NOT EXISTS payment_gateway_settings (
    id SERIAL PRIMARY KEY,
    gateway_provider VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(150) NOT NULL,
    is_enabled INTEGER NOT NULL DEFAULT 0,
    environment VARCHAR(20) NOT NULL DEFAULT 'SANDBOX',
    public_key TEXT,
    secret_key TEXT,
    merchant_id VARCHAR(100),
    webhook_secret TEXT,
    bank_name VARCHAR(150),
    bank_account_number VARCHAR(100),
    bank_account_name VARCHAR(150),
    promptpay_id VARCHAR(50),
    fee_percentage NUMERIC(5,2) DEFAULT 0.00,
    fee_fixed NUMERIC(10,2) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'THB',
    supported_methods TEXT,
    instructions TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Seed Default Payment Gateways
INSERT INTO payment_gateway_settings (
    gateway_provider, display_name, is_enabled, environment,
    public_key, secret_key, merchant_id, webhook_secret,
    bank_name, bank_account_number, bank_account_name, promptpay_id,
    fee_percentage, fee_fixed, currency, supported_methods, instructions
) VALUES 
(
    'PROMPTPAY', 'PromptPay QR (สแกนจ่ายทันที)', 1, 'PRODUCTION',
    '', '', '', '',
    'ธนาคารกสิกรไทย (KBANK)', '098-2-34567-8', 'บจก. สยาม ออโต้พาร์ท แพลตฟอร์ม', '0812345678',
    0.00, 0.00, 'THB', '["PROMPTPAY", "QR_CODE"]',
    'สแกน QR Code ด้วยแอปธนาคารทุกแห่งในไทย เงินเข้าบัญชีทันที อัปเดตสถานะอัตโนมัติ'
),
(
    'STRIPE', 'Stripe Payments (บัตรเครดิต/เดบิต สากล)', 0, 'SANDBOX',
    'pk_test_sample_stripe_public_key', 'sk_test_sample_stripe_secret_key', '', 'whsec_sample_webhook_secret',
    '', '', '', '',
    2.90, 10.00, 'THB', '["CREDIT_CARD", "VISA", "MASTERCARD", "JCB"]',
    'รองรับบัตรเครดิตและเดบิตทั้งในไทยและต่างประเทศ พร้อมระบบตัดรอบบิล Recurring อัตโนมัติ'
),
(
    'OMISE', 'Omise Payment (Opn Payments)', 0, 'SANDBOX',
    'pkey_test_sample_omise_public', 'skey_test_sample_omise_secret', '', '',
    '', '', '', '',
    3.65, 0.00, 'THB', '["CREDIT_CARD", "PROMPTPAY", "TRUE_MONEY", "MOBILE_BANKING"]',
    'เกตเวย์ชั้นนำของไทย รองรับบัตรเครดิต, PromptPay, TrueMoney Wallet และ Mobile Banking'
),
(
    'GB_PRIME_PAY', 'GB Prime Pay', 0, 'SANDBOX',
    'gbp_pub_sample_key', 'gbp_sec_sample_key', 'SAMPLE_MERCHANT_ID', '',
    '', '', '', '',
    3.00, 0.00, 'THB', '["CREDIT_CARD", "PROMPTPAY", "QR_CASH"]',
    'ระบบรับชำระเงินมาตรฐานธนาคารแห่งประเทศไทย รองรับทั้ง QR รายการ และบัตรเครดิต'
),
(
    'BANK_TRANSFER', 'โอนเงินผ่านบัญชีธนาคาร (Manual Transfer)', 1, 'PRODUCTION',
    '', '', '', '',
    'ธนาคารไทยพาณิชย์ (SCB)', '123-4-56789-0', 'บจก. สยาม ออโต้พาร์ท แพลตฟอร์ม', '0105566000000',
    0.00, 0.00, 'THB', '["BANK_TRANSFER", "DIRECT_DEPOSIT"]',
    'โอนเงินเข้าบัญชีบริษัทโดยตรง และแนบสลิปผ่านระบบ รอ Owner กดอนุมัติเปิดใช้งาน 1 คลิก'
)
ON CONFLICT (gateway_provider) DO NOTHING;
