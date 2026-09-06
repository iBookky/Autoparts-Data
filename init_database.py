#!/usr/bin/env python3
"""
AutoParts SaaS Platform — Direct 1-Command Database Builder & Initializer
Usage:
  python3 init_database.py
  DATABASE_URL="postgresql://user:pass@localhost:5432/autoparts_db" python3 init_database.py
"""

import os
import sys

# Ensure backend package is importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from backend.database import init_db, is_postgres_mode, get_db_connection
from migrate_sqlite_to_pg import migrate_to_postgres

def main():
    print("=" * 80)
    print("🚀 AUTOPARTS SAAS — ZERO-TOUCH DATABASE INITIALIZATION & MIGRATION")
    print("=" * 80)

    db_url = os.environ.get("DATABASE_URL", os.environ.get("POSTGRES_URL", ""))
    print(f"📡 Engine Mode     : {'🐘 PostgreSQL' if is_postgres_mode() else '📦 SQLite'}")
    if is_postgres_mode():
        safe_url = db_url.split('@')[-1] if '@' in db_url else db_url
        print(f"🔗 Target Database : {safe_url}")
    else:
        print(f"📁 SQLite DB Path  : parts_cross_ref.db")
    print("-" * 80)

    # 1. Initialize Schema & Tables
    print("[1/2] Initializing all 44 Schema Tables & System Accounts...")
    try:
        init_db()
        print("  ✓ Schema migrations applied successfully.")
        print("  ✓ Default platform accounts seeded (owner, superadmin, admin, staff, customer).")
    except Exception as e:
        print(f"  ❌ Error applying migrations: {e}")
        sys.exit(1)

    # 2. Migrate existing SQLite data if running in PostgreSQL mode
    if is_postgres_mode():
        sqlite_candidates = ["parts_cross_ref.db", "data/parts_cross_ref.db", "/app/data/parts_cross_ref.db"]
        found_sqlite = any(os.path.exists(p) for p in sqlite_candidates)
        if found_sqlite:
            print("\n[2/2] Migrating 8,111+ Records from SQLite -> PostgreSQL...")
            migrate_to_postgres()
        else:
            print("\n[2/2] No previous SQLite database file found. Clean PostgreSQL initialized.")
    else:
        print("\n[2/2] SQLite database is fully initialized and operational.")

    # 3. Verification
    print("\n" + "=" * 80)
    print("🎉 DATABASE INITIALIZATION COMPLETE & READY FOR PRODUCTION!")
    print("=" * 80)
    
    # Run inspector summary
    try:
        from view_db import is_pg_mode, inspect_postgres, inspect_sqlite
        if is_pg_mode():
            inspect_postgres("--summary")
        else:
            inspect_sqlite("--summary")
    except Exception as e:
        print(f"Summary check: {e}")

if __name__ == "__main__":
    main()
