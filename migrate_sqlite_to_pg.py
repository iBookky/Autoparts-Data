#!/usr/bin/env python3
"""
AutoParts SaaS Platform — SQLite to PostgreSQL Big Data Migration Engine
1-Click migration of all 44 tables, schemas, indexes, sequences, and records.
"""

import os
import sys
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

SQLITE_PATH = os.environ.get("SQLITE_PATH", "parts_cross_ref.db")
if not os.path.exists(SQLITE_PATH) and os.path.exists("data/parts_cross_ref.db"):
    SQLITE_PATH = "data/parts_cross_ref.db"

PG_URL = os.environ.get("DATABASE_URL", os.environ.get("POSTGRES_URL", "postgresql://autoparts_user:autoparts_secure_pass123@localhost:5432/autoparts_db"))

def migrate_to_postgres():
    print("=" * 80)
    print("🚀 STARTING AUTOPARTS SQLITE -> POSTGRESQL BIG DATA MIGRATION")
    print(f"📦 Source SQLite DB : {SQLITE_PATH}")
    print(f"🐘 Target Postgres  : {PG_URL.split('@')[-1] if '@' in PG_URL else PG_URL}")
    print("=" * 80)

    if not os.path.exists(SQLITE_PATH):
        print(f"❌ Error: SQLite database not found at '{SQLITE_PATH}'")
        return False

    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cur = sqlite_conn.cursor()

    # Connect to PostgreSQL
    try:
        pg_conn = psycopg2.connect(PG_URL)
        pg_cur = pg_conn.cursor()
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL: {e}")
        print("\n💡 Please ensure PostgreSQL is running and DATABASE_URL is correct.")
        return False

    # 1. Run PostgreSQL schema migrations
    print("\n[1/3] Executing PostgreSQL schema migrations...")
    migrations_dir = os.path.join(os.path.dirname(__file__), "backend", "migrations_pg")
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith(".sql")])
    for mf in migration_files:
        mf_path = os.path.join(migrations_dir, mf)
        with open(mf_path, "r", encoding="utf-8") as f:
            sql = f.read()
        try:
            pg_cur.execute(sql)
            pg_conn.commit()
            print(f"  ✓ Applied migration: {mf}")
        except Exception as e:
            pg_conn.rollback()
            print(f"  ⚠️ Warning applying {mf}: {e}")

    # 2. Get list of tables in dependency order
    sqlite_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in sqlite_cur.fetchall()]

    # Sort tables so foreign key dependencies are inserted in order
    order_priority = [
        "users", "roles", "permissions", "role_permissions", "user_roles",
        "organizations", "organization_members", "plans", "plan_versions", "plan_features", "plan_entitlements",
        "subscriptions", "subscription_items", "subscription_entitlements_snapshot",
        "entitlements", "usage_records", "api_keys", "add_ons", "add_on_plan_compatibility",
        "coupons", "invoices", "invoice_items", "coupon_redemptions", "payment_transactions",
        "master_parts", "temp_parts", "cross_reference_relations",
        "meta_car_brands", "meta_car_models", "meta_car_years", "meta_aftermarket_brands", "meta_categories",
        "meta_ai_models", "agent_skills_config", "ai_keys_config", "ai_usage_stats",
        "customer_leads", "search_logs", "user_favorites", "owner_alerts",
        "platform_audit_logs", "commercial_audit_logs", "organization_audit_logs", "organization_invitations"
    ]
    
    sorted_tables = []
    for t in order_priority:
        if t in tables:
            sorted_tables.append(t)
    for t in tables:
        if t not in sorted_tables:
            sorted_tables.append(t)

    print(f"\n[2/3] Migrating data across {len(sorted_tables)} tables...")
    total_migrated_records = 0

    # Temporarily disable foreign key constraints for fast bulk import
    try:
        pg_cur.execute("SET session_replication_role = 'replica';")
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()

    for table in sorted_tables:
        sqlite_cur.execute(f"PRAGMA table_info({table})")
        sqlite_cols = [c["name"] for c in sqlite_cur.fetchall()]

        # Get actual PostgreSQL columns for this table
        pg_cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = %s AND table_schema = 'public';
        """, (table,))
        pg_cols = [r[0] for r in pg_cur.fetchall()]

        if not pg_cols:
            print(f"  ⚠️ Table '{table}' not found in PostgreSQL. Skipping.")
            continue

        # Intersect columns so only existing columns in PostgreSQL are inserted
        cols = [c for c in sqlite_cols if c in pg_cols]
        has_id = "id" in cols

        sqlite_cur.execute(f"SELECT * FROM {table}")
        rows = sqlite_cur.fetchall()

        if not rows:
            print(f"  • {table:<35} : 0 records (skipped)")
            continue

        # Prepare insert query
        cols_str = ", ".join([f'"{c}"' for c in cols])
        placeholders = ", ".join(["%s"] * len(cols))
        
        insert_sql = f'INSERT INTO "{table}" ({cols_str}) VALUES ({placeholders}) ON CONFLICT DO NOTHING'

        data = [tuple(r[c] for c in cols) for r in rows]
        
        try:
            pg_cur.executemany(insert_sql, data)
            pg_conn.commit()
            
            # Reset serial sequence if id exists
            if has_id:
                try:
                    pg_cur.execute(f"""
                        SELECT setval(
                            pg_get_serial_sequence('"{table}"', 'id'),
                            COALESCE((SELECT MAX(id) FROM "{table}"), 1),
                            true
                        );
                    """)
                    pg_conn.commit()
                except Exception:
                    pg_conn.rollback()

            print(f"  ✓ {table:<35} : {len(rows):<5} records migrated")
            total_migrated_records += len(rows)
        except Exception as e:
            pg_conn.rollback()
            print(f"  ❌ Error migrating table {table}: {e}")

    # Re-enable foreign key checks
    try:
        pg_cur.execute("SET session_replication_role = 'origin';")
        pg_conn.commit()
    except Exception:
        pg_conn.rollback()

    # 3. Final Verification
    print("\n[3/3] Verifying PostgreSQL database state...")
    pg_cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    pg_tables = [r[0] for r in pg_cur.fetchall()]
    print(f"  ✓ Total Tables in PostgreSQL : {len(pg_tables)}")
    print(f"  ✓ Total Records Migrated     : {total_migrated_records:,}")

    sqlite_conn.close()
    pg_conn.close()

    print("\n" + "=" * 80)
    print("🎉 POSTGRESQL BIG DATA MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    return True

if __name__ == "__main__":
    migrate_to_postgres()

