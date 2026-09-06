#!/usr/bin/env python3
"""
AutoParts SaaS Platform — Database Record Inspector CLI (Dual-Engine: PostgreSQL & SQLite)
Usage:
  python3 view_db.py                 # View all tables and total record counts
  python3 view_db.py <table_name>    # View records inside a specific table (e.g. python3 view_db.py users)
  python3 view_db.py --summary       # View summary of tables and total counts
  python3 view_db.py --table users   # View records with column names
  python3 view_db.py --export-json   # Export full database dump to JSON
"""

import os
import sys
import json

DATABASE_URL = os.environ.get("DATABASE_URL", os.environ.get("POSTGRES_URL", ""))
DB_PATHS = [
    os.environ.get("DB_PATH", ""),
    "data/parts_cross_ref.db",
    "parts_cross_ref.db",
    "/app/data/parts_cross_ref.db"
]

def is_pg_mode():
    return bool(DATABASE_URL and (DATABASE_URL.startswith("postgresql://") or DATABASE_URL.startswith("postgres://")))

def inspect_postgres(table_target=None, limit=100):
    import psycopg2
    from psycopg2.extras import RealDictCursor

    url = DATABASE_URL
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    try:
        conn = psycopg2.connect(url)
        c = conn.cursor(cursor_factory=RealDictCursor)
    except Exception as e:
        print(f"❌ Error connecting to PostgreSQL ({url}): {e}")
        return

    # Get all public tables
    c.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    tables = [r["table_name"] for r in c.fetchall()]

    if not table_target or table_target in ("--all", "--summary"):
        print("=" * 80)
        print(f"🐘 AUTOPARTS POSTGRESQL INSPECTOR: {url.split('@')[-1] if '@' in url else url}")
        print(f"📊 Total Tables: {len(tables)}")
        print("=" * 80)

        total_records = 0
        for idx, t in enumerate(tables, 1):
            c.execute(f'SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position;', (t,))
            cols = [col["column_name"] for col in c.fetchall()]
            c.execute(f'SELECT COUNT(*) as count FROM "{t}";')
            count = c.fetchone()["count"]
            total_records += count
            col_preview = ", ".join(cols[:4]) + ("..." if len(cols) > 4 else "")
            print(f" {idx:2d}. {t:<35} | Records: {count:<6} | Cols: ({len(cols)}) [{col_preview}]")

        print("=" * 80)
        print(f"✨ GRAND TOTAL RECORDS ACROSS ALL TABLES: {total_records:,}")
        print("=" * 80)
        print("💡 Tip: To view records inside a table, run:")
        print("   python3 view_db.py users")
        print("   python3 view_db.py master_parts")
        print("   python3 view_db.py organizations")
        print("=" * 80)

    elif table_target == "--export-json":
        output_data = {}
        for t in tables:
            c.execute(f'SELECT * FROM "{t}"')
            output_data[t] = [dict(r) for r in c.fetchall()]
        out_filename = "database_pg_dump.json"
        with open(out_filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ Full PostgreSQL database dump exported to '{out_filename}' ({len(tables)} tables)")

    else:
        t = table_target.strip()
        if t not in tables:
            print(f"❌ Table '{t}' not found. Available tables:")
            print(", ".join(tables))
            conn.close()
            return

        c.execute(f'SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position;', (t,))
        cols = [col["column_name"] for col in c.fetchall()]

        c.execute(f'SELECT * FROM "{t}" LIMIT %s', (limit,))
        rows = c.fetchall()

        print("=" * 80)
        print(f"📋 TABLE: {t} (Showing {len(rows)} records)")
        print("Columns: " + " | ".join(cols))
        print("-" * 80)

        for i, row in enumerate(rows, 1):
            row_dict = dict(row)
            if t == "users" and "password" in row_dict:
                row_dict["password"] = str(row_dict["password"])[:10] + "..."
            print(f"[{i:3d}] " + " | ".join(f"{k}: {v}" for k, v in row_dict.items() if v is not None and str(v) != ""))
            print("-" * 80)

    conn.close()

def inspect_sqlite(table_target=None, limit=100):
    import sqlite3
    db_file = None
    for p in DB_PATHS:
        if p and os.path.exists(p):
            db_file = p
            break
    if not db_file:
        print("❌ Error: No SQLite database file found.")
        return

    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
    tables = [r[0] for r in c.fetchall()]

    if not table_target or table_target in ("--all", "--summary"):
        print("=" * 80)
        print(f"📦 AUTOPARTS SQLITE INSPECTOR: {db_file}")
        print(f"📊 Total Tables: {len(tables)}")
        print("=" * 80)
        
        total_records = 0
        for idx, t in enumerate(tables, 1):
            c.execute(f"PRAGMA table_info({t})")
            cols = [col["name"] for col in c.fetchall()]
            c.execute(f"SELECT COUNT(*) FROM {t}")
            count = c.fetchone()[0]
            total_records += count
            col_preview = ", ".join(cols[:4]) + ("..." if len(cols) > 4 else "")
            print(f" {idx:2d}. {t:<35} | Records: {count:<6} | Cols: ({len(cols)}) [{col_preview}]")

        print("=" * 80)
        print(f"✨ GRAND TOTAL RECORDS ACROSS ALL TABLES: {total_records:,}")
        print("=" * 80)
        print("💡 Tip: To view records inside a table, run:")
        print("   python3 view_db.py users")
        print("   python3 view_db.py master_parts")
        print("   python3 view_db.py organizations")
        print("=" * 80)

    elif table_target == "--export-json":
        output_data = {}
        for t in tables:
            c.execute(f"SELECT * FROM {t}")
            output_data[t] = [dict(r) for r in c.fetchall()]
        out_filename = "database_sqlite_dump.json"
        with open(out_filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ Full SQLite database dump exported to '{out_filename}' ({len(tables)} tables)")

    else:
        t = table_target.strip()
        if t not in tables:
            print(f"❌ Table '{t}' not found. Available tables:")
            print(", ".join(tables))
            conn.close()
            return

        c.execute(f"PRAGMA table_info({t})")
        cols = [col["name"] for col in c.fetchall()]
        
        c.execute(f"SELECT * FROM {t} LIMIT ?", (limit,))
        rows = c.fetchall()

        print("=" * 80)
        print(f"📋 TABLE: {t} (Showing {len(rows)} records)")
        print("Columns: " + " | ".join(cols))
        print("-" * 80)

        for i, row in enumerate(rows, 1):
            row_dict = dict(row)
            if t == "users" and "password" in row_dict:
                row_dict["password"] = str(row_dict["password"])[:10] + "..."
            print(f"[{i:3d}] " + " | ".join(f"{k}: {v}" for k, v in row_dict.items() if v is not None and str(v) != ""))
            print("-" * 80)

    conn.close()

if __name__ == "__main__":
    target = None
    limit = 100
    if len(sys.argv) > 1:
        if sys.argv[1] == "--table" and len(sys.argv) > 2:
            target = sys.argv[2]
            if "--limit" in sys.argv:
                l_idx = sys.argv.index("--limit")
                if l_idx + 1 < len(sys.argv):
                    limit = int(sys.argv[l_idx + 1])
        elif sys.argv[1] != "--table":
            target = sys.argv[1]

    if is_pg_mode():
        inspect_postgres(target, limit)
    else:
        inspect_sqlite(target, limit)

