"""
AutoParts SaaS Platform — Enterprise PostgreSQL Adapter Layer
Provides high-concurrency Big Data PostgreSQL connection pooling,
parameter normalization, schema migrations, and seamless SQLite-compatible API.

Key improvements:
- ThreadedConnectionPool for thread-safe concurrent access
- Connection health checks before returning from pool
- Auto-reconnect on stale/dead connections
- Context manager support for automatic connection lifecycle
"""

import os
import re
import threading
import psycopg2
from psycopg2 import pool, OperationalError
from psycopg2.extras import RealDictCursor, DictCursor
from dotenv import load_dotenv

load_dotenv()

def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", os.environ.get("POSTGRES_URL", ""))

_pg_pool = None
_pg_pool_lock = threading.Lock()

def get_pg_pool():
    global _pg_pool
    db_url = get_database_url()
    if _pg_pool is None and db_url and (db_url.startswith("postgresql://") or db_url.startswith("postgres://")):
        with _pg_pool_lock:
            # Double-check inside lock
            if _pg_pool is not None:
                return _pg_pool
            try:
                url = db_url
                if url.startswith("postgres://"):
                    url = url.replace("postgres://", "postgresql://", 1)
                # ThreadedConnectionPool is thread-safe (vs SimpleConnectionPool)
                # min=2, max=20 — conservative to avoid hitting PG max_connections
                _pg_pool = psycopg2.pool.ThreadedConnectionPool(
                    2, 20, url,
                    # TCP keepalive to detect dead connections
                    keepalives=1,
                    keepalives_idle=30,
                    keepalives_interval=10,
                    keepalives_count=5,
                    # Connection timeout
                    connect_timeout=10,
                )
                print(f"[PG Pool] ThreadedConnectionPool created (min=2, max=20)")
            except Exception as e:
                print(f"Error creating PostgreSQL connection pool: {e}")
                raise e
    return _pg_pool


def _reset_pool():
    """Reset the pool (e.g. after all connections become stale)."""
    global _pg_pool
    with _pg_pool_lock:
        if _pg_pool is not None:
            try:
                _pg_pool.closeall()
            except Exception:
                pass
            _pg_pool = None


class PGCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor
        self.lastrowid = None

    def _convert_query(self, sql: str, params=None) -> tuple:
        converted_sql = sql

        # 1. Convert SQLite named parameters (:param) to PostgreSQL (%(param)s)
        if isinstance(params, dict):
            # Replace :param_name with %(param_name)s
            converted_sql = re.sub(r':([a-zA-Z_][a-zA-Z0-9_]*)', r'%(\1)s', converted_sql)
        else:
            # Replace ? with %s
            converted_sql = re.sub(r'(?<!\w)\?(?!\w)', '%s', converted_sql)

        # 2. Convert SQLite date/time functions to PostgreSQL
        # datetime('now', '-48 hours') -> (CURRENT_TIMESTAMP - INTERVAL '48 hours')
        converted_sql = re.sub(
            r"datetime\s*\(\s*'now'\s*,\s*'-(\d+)\s*hours?'\s*\)",
            r"(CURRENT_TIMESTAMP - INTERVAL '\1 hours')",
            converted_sql,
            flags=re.IGNORECASE
        )
        converted_sql = re.sub(
            r"datetime\s*\(\s*'now'\s*,\s*'([+-]?\d+)\s*(days?|hours?|months?|years?|minutes?)'\s*\)",
            r"(CURRENT_TIMESTAMP + INTERVAL '\1 \2')",
            converted_sql,
            flags=re.IGNORECASE
        )
        converted_sql = re.sub(
            r"datetime\s*\(\s*'now'\s*\)",
            r"CURRENT_TIMESTAMP",
            converted_sql,
            flags=re.IGNORECASE
        )
        # datetime(created_at) -> created_at
        converted_sql = re.sub(
            r"datetime\s*\(\s*([a-zA-Z_][a-zA-Z0-9_\.]*)\s*\)",
            r"\1",
            converted_sql,
            flags=re.IGNORECASE
        )

        # SQLite DDL types to PostgreSQL
        converted_sql = re.sub(r'INTEGER\s+PRIMARY\s+KEY\s+AUTOINCREMENT', 'SERIAL PRIMARY KEY', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'DATETIME\s+DEFAULT\s+CURRENT_TIMESTAMP', 'TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP', converted_sql, flags=re.IGNORECASE)
        converted_sql = re.sub(r'\bDATETIME\b', 'TIMESTAMP WITH TIME ZONE', converted_sql, flags=re.IGNORECASE)

        # 3. Convert INSERT OR IGNORE INTO
        if "INSERT OR IGNORE INTO" in converted_sql.upper():
            converted_sql = re.sub(r'INSERT\s+OR\s+IGNORE\s+INTO', 'INSERT INTO', converted_sql, flags=re.IGNORECASE)
            if "ON CONFLICT" not in converted_sql.upper():
                converted_sql = converted_sql.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"

        # 4. Convert INSERT OR REPLACE INTO
        if "INSERT OR REPLACE INTO" in converted_sql.upper():
            if re.search(r'INSERT\s+OR\s+REPLACE\s+INTO\s+master_parts', converted_sql, re.IGNORECASE):
                converted_sql = re.sub(r'INSERT\s+OR\s+REPLACE\s+INTO\s+master_parts', 'INSERT INTO master_parts', converted_sql, flags=re.IGNORECASE)
                if "ON CONFLICT" not in converted_sql.upper():
                    conflict_clause = (
                        " ON CONFLICT (brand, part_number, oem_number, car_brand, car_model) "
                        "DO UPDATE SET "
                        "product_name_th = EXCLUDED.product_name_th, "
                        "product_name_en = EXCLUDED.product_name_en, "
                        "category = EXCLUDED.category, "
                        "year_start = EXCLUDED.year_start, "
                        "year_end = EXCLUDED.year_end, "
                        "engine = EXCLUDED.engine, "
                        "fuel = EXCLUDED.fuel, "
                        "transmission = EXCLUDED.transmission, "
                        "description = EXCLUDED.description, "
                        "cost_unit = EXCLUDED.cost_unit, "
                        "notes = EXCLUDED.notes, "
                        "updated_at = CURRENT_TIMESTAMP"
                    )
                    converted_sql = converted_sql.rstrip().rstrip(";") + conflict_clause
            elif re.search(r'INSERT\s+OR\s+REPLACE\s+INTO\s+organization_members', converted_sql, re.IGNORECASE):
                converted_sql = re.sub(r'INSERT\s+OR\s+REPLACE\s+INTO\s+organization_members', 'INSERT INTO organization_members', converted_sql, flags=re.IGNORECASE)
                if "ON CONFLICT" not in converted_sql.upper():
                    converted_sql = converted_sql.rstrip().rstrip(";") + " ON CONFLICT (org_id, user_id) DO UPDATE SET org_role = EXCLUDED.org_role, status = EXCLUDED.status, updated_at = CURRENT_TIMESTAMP"
            elif re.search(r'INSERT\s+OR\s+REPLACE\s+INTO\s+add_ons', converted_sql, re.IGNORECASE):
                converted_sql = re.sub(r'INSERT\s+OR\s+REPLACE\s+INTO\s+add_ons', 'INSERT INTO add_ons', converted_sql, flags=re.IGNORECASE)
                if "ON CONFLICT" not in converted_sql.upper():
                    converted_sql = converted_sql.rstrip().rstrip(";") + " ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, code = EXCLUDED.code, description = EXCLUDED.description, price_monthly = EXCLUDED.price_monthly, price_yearly = EXCLUDED.price_yearly, currency = EXCLUDED.currency, status = EXCLUDED.status, entitlement_type = EXCLUDED.entitlement_type, quota_increase = EXCLUDED.quota_increase, user_increase = EXCLUDED.user_increase"
            elif re.search(r'INSERT\s+OR\s+REPLACE\s+INTO\s+subscriptions', converted_sql, re.IGNORECASE):
                converted_sql = re.sub(r'INSERT\s+OR\s+REPLACE\s+INTO\s+subscriptions', 'INSERT INTO subscriptions', converted_sql, flags=re.IGNORECASE)
                if "ON CONFLICT" not in converted_sql.upper():
                    converted_sql = converted_sql.rstrip().rstrip(";") + " ON CONFLICT (org_id) DO UPDATE SET plan_id = EXCLUDED.plan_id, status = EXCLUDED.status, billing_cycle = EXCLUDED.billing_cycle, current_period_start = EXCLUDED.current_period_start, current_period_end = EXCLUDED.current_period_end"
            elif re.search(r'INSERT\s+OR\s+REPLACE\s+INTO\s+roles', converted_sql, re.IGNORECASE):
                converted_sql = re.sub(r'INSERT\s+OR\s+REPLACE\s+INTO\s+roles', 'INSERT INTO roles', converted_sql, flags=re.IGNORECASE)
                if "ON CONFLICT" not in converted_sql.upper():
                    converted_sql = converted_sql.rstrip().rstrip(";") + " ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name, portal_access = EXCLUDED.portal_access, tier_level = EXCLUDED.tier_level, is_system_role = EXCLUDED.is_system_role, description = EXCLUDED.description"
            else:
                converted_sql = re.sub(r'INSERT\s+OR\s+REPLACE\s+INTO', 'INSERT INTO', converted_sql, flags=re.IGNORECASE)
                if "ON CONFLICT" not in converted_sql.upper():
                    converted_sql = converted_sql.rstrip().rstrip(";") + " ON CONFLICT DO NOTHING"

        # 5. Handle lastrowid via RETURNING id for single INSERT statements
        is_insert = bool(re.match(r'^\s*INSERT\s+INTO', converted_sql, re.IGNORECASE))
        has_returning = "RETURNING" in converted_sql.upper()
        has_on_conflict_do_nothing = "ON CONFLICT DO NOTHING" in converted_sql.upper()
        if is_insert and not has_returning and not has_on_conflict_do_nothing:
            converted_sql = converted_sql.rstrip().rstrip(";") + " RETURNING id"

        return converted_sql, params


    def execute(self, sql: str, params=None):
        clean_check = sql.strip().upper()
        if clean_check.startswith("PRAGMA"):
            return self

        converted_sql, final_params = self._convert_query(sql, params)
        self.lastrowid = None
        try:
            if final_params is not None:
                if isinstance(final_params, dict):
                    self.cursor.execute(converted_sql, final_params)
                else:
                    self.cursor.execute(converted_sql, list(final_params))
            else:
                self.cursor.execute(converted_sql)
            
            # If RETURNING id was used, grab lastrowid
            if "RETURNING ID" in converted_sql.upper() and self.cursor.description:
                try:
                    row = self.cursor.fetchone()
                    if row and "id" in row:
                        self.lastrowid = row["id"]
                except Exception:
                    pass
        except Exception as e:
            # Fallback if RETURNING id failed on a table without id
            if "RETURNING id" in converted_sql:
                clean_sql = converted_sql.replace(" RETURNING id", "")
                if final_params is not None:
                    if isinstance(final_params, dict):
                        self.cursor.execute(clean_sql, final_params)
                    else:
                        self.cursor.execute(clean_sql, list(final_params))
                else:
                    self.cursor.execute(clean_sql)
            else:
                raise e
        return self

    def executemany(self, sql: str, params_seq):
        converted_sql, _ = self._convert_query(sql)
        self.cursor.executemany(converted_sql, params_seq)
        return self

    def executescript(self, sql_script: str):
        statements = [s.strip() for s in sql_script.split(';') if s.strip()]
        for stmt in statements:
            try:
                self.execute(stmt)
                if self.cursor and self.cursor.connection:
                    self.cursor.connection.commit()
            except Exception:
                try:
                    if self.cursor and self.cursor.connection:
                        self.cursor.connection.rollback()
                except Exception:
                    pass
        return self

    def fetchone(self):
        try:
            row = self.cursor.fetchone()
            return row if row is not None else None
        except Exception:
            return None

    def fetchall(self):
        try:
            rows = self.cursor.fetchall()
            return list(rows) if rows else []
        except Exception:
            return []

    def fetchmany(self, size=None):
        try:
            rows = self.cursor.fetchmany(size)
            return list(rows) if rows else []
        except Exception:
            return []

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def close(self):
        try:
            self.cursor.close()
        except Exception:
            pass

class PGConnectionWrapper:
    """Thread-safe PostgreSQL connection wrapper with context manager support."""
    
    def __init__(self, raw_conn, pool_ref=None):
        self.conn = raw_conn
        self.pool_ref = pool_ref
        self.row_factory = None
        self._closed = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False  # Don't suppress exceptions

    def cursor(self):
        raw_cursor = self.conn.cursor(cursor_factory=DictCursor)
        return PGCursorWrapper(raw_cursor)

    def commit(self):
        self.conn.commit()

    def rollback(self):
        try:
            self.conn.rollback()
        except Exception:
            pass

    def execute(self, sql: str, params=None):
        cur = self.cursor()
        cur.execute(sql, params)
        return cur

    def executescript(self, sql_script: str):
        cur = self.cursor()
        return cur.executescript(sql_script)

    def close(self):
        if self._closed:
            return
        self._closed = True
        if self.pool_ref and self.conn:
            try:
                self.conn.rollback()
                self.pool_ref.putconn(self.conn)
            except Exception:
                # If putconn fails, the connection is likely broken
                # Try to discard it from the pool
                try:
                    self.pool_ref.putconn(self.conn, close=True)
                except Exception:
                    try:
                        self.conn.close()
                    except Exception:
                        pass
        elif self.conn:
            try:
                self.conn.close()
            except Exception:
                pass

def _check_connection_health(conn):
    """Test if a connection is alive by executing a simple query."""
    try:
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        return True
    except Exception:
        return False

def get_pg_connection():
    """Get a healthy PostgreSQL connection from the pool with auto-retry."""
    max_retries = 3
    for attempt in range(max_retries):
        pool_instance = get_pg_pool()
        if pool_instance:
            try:
                raw_conn = pool_instance.getconn()
                # Health check — if connection is stale, get a new one
                if not _check_connection_health(raw_conn):
                    print(f"[PG Pool] Stale connection detected, discarding (attempt {attempt + 1})")
                    try:
                        pool_instance.putconn(raw_conn, close=True)
                    except Exception:
                        pass
                    continue
                return PGConnectionWrapper(raw_conn, pool_instance)
            except pool.PoolError as e:
                # Pool exhausted — try to reset and recreate
                print(f"[PG Pool] Pool error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    _reset_pool()
                    continue
                raise
            except OperationalError as e:
                print(f"[PG Pool] Operational error: {e} (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    _reset_pool()
                    continue
                raise
        else:
            # Fallback: direct connection without pool
            url = get_database_url()
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            raw_conn = psycopg2.connect(url, connect_timeout=10)
            return PGConnectionWrapper(raw_conn)
    
    # Final fallback
    raise Exception("[PG Pool] Failed to get a healthy connection after all retries")
