#!/bin/bash
set -e

# ==============================================================================
# AutoParts SaaS Platform - Zero-Touch Auto Database & Server Bootstrapper
# ==============================================================================

DATA_DIR=$(dirname "${DB_PATH:-/app/data/parts_cross_ref.db}")

# 1. Ensure persistent data directory exists with full read-write permissions
if [ -n "$DATA_DIR" ] && [ "$DATA_DIR" != "." ]; then
    mkdir -p "$DATA_DIR"
    if [ ! -f "$DATA_DIR/parts_cross_ref.db" ] && [ -f "/app/parts_cross_ref.db" ]; then
        echo "📦 [Bootstrap] Initializing database in persistent volume..."
        cp /app/parts_cross_ref.db "$DATA_DIR/parts_cross_ref.db"
    fi
    chmod -R 777 "$DATA_DIR" 2>/dev/null || true
fi

# 2. Wait for PostgreSQL Database readiness (if configured)
if [ -n "$DATABASE_URL" ] || [ -n "$POSTGRES_URL" ]; then
    echo "⏳ [Bootstrap] Waiting for PostgreSQL to be ready..."
    for i in {1..30}; do
        if python3 -c "from backend.database import get_db_connection; conn = get_db_connection(); conn.close()" 2>/dev/null; then
            echo "✅ [Bootstrap] PostgreSQL connected successfully!"
            break
        fi
        sleep 1
    done
fi

# 3. Run Zero-Touch Database Initialization & Migration (PostgreSQL / SQLite)
echo "🐘 [Bootstrap] Initializing & Verifying Database..."
python3 init_database.py || true

# 4. Launch FastAPI Application Server
echo "🚀 [Bootstrap] Launching AutoParts SaaS Engine on port ${PORT:-8000}..."
exec python3 main.py

