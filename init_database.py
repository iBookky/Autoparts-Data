#!/usr/bin/env python3
"""
AutoParts SaaS Platform — PostgreSQL Database Builder & Initializer
Usage:
  python3 init_database.py
  DATABASE_URL="postgresql://user:pass@localhost:5432/autoparts_db" python3 init_database.py
"""

import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Ensure backend package is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.database import init_db, get_db_connection

def main():
    print("=" * 80)
    print("🚀 AUTOPARTS SAAS — POSTGRESQL DATABASE INITIALIZATION")
    print("=" * 80)

    db_url = os.environ.get("DATABASE_URL", os.environ.get("POSTGRES_URL", ""))
    if not db_url:
        print("❌ DATABASE_URL environment variable is not set.")
        print("   Set it to: postgresql://user:pass@host:5432/dbname")
        sys.exit(1)

    safe_url = db_url.split('@')[-1] if '@' in db_url else db_url
    print(f"🐘 Engine Mode     : PostgreSQL")
    print(f"🔗 Target Database : {safe_url}")
    print("-" * 80)

    # 1. Wait for PostgreSQL readiness
    print("[1/2] Waiting for PostgreSQL to be ready...")
    for attempt in range(1, 31):
        try:
            test_conn = get_db_connection()
            test_conn.close()
            print(f"  ✅ PostgreSQL connected (attempt {attempt})")
            break
        except Exception as conn_err:
            print(f"  ⏳ Waiting for PostgreSQL (attempt {attempt}/30): {conn_err}")
            time.sleep(2)
    else:
        print("  ❌ Could not connect to PostgreSQL after 30 attempts.")
        sys.exit(1)

    # 2. Initialize Schema & Seed Data
    print("[2/2] Applying migrations and seeding system accounts...")
    try:
        init_db()
        print("  ✓ All PostgreSQL migrations applied successfully.")
        print("  ✓ Default accounts seeded: owner, superadmin")
        print("  ✓ Standard plans, roles, and permissions seeded.")
    except Exception as e:
        print(f"  ❌ Error during initialization: {e}")
        sys.exit(1)

    # 3. Done
    print("\n" + "=" * 80)
    print("🎉 DATABASE INITIALIZATION COMPLETE & READY FOR PRODUCTION!")
    print("=" * 80)

    # Quick table count check
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public'")
        row = cursor.fetchone()
        count = row[0] if row else "?"
        conn.close()
        print(f"📊 Tables created: {count} tables in public schema")
    except Exception as e:
        print(f"  Summary check: {e}")

if __name__ == "__main__":
    main()
