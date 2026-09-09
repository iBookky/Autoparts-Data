#!/bin/bash
set -e

# ==============================================================================
# AutoParts SaaS Platform — PostgreSQL-Only Bootstrapper
# ==============================================================================

# 1. Wait for PostgreSQL readiness
echo "⏳ [Bootstrap] Waiting for PostgreSQL to be ready..."
for i in $(seq 1 30); do
    if python3 -c "from backend.database import get_db_connection; conn = get_db_connection(); conn.close()" 2>/dev/null; then
        echo "✅ [Bootstrap] PostgreSQL connected successfully!"
        break
    fi
    echo "  Attempt $i/30: PostgreSQL not ready, retrying in 2s..."
    sleep 2
done

# 2. Run PostgreSQL Schema Initialization & Migration
echo "🐘 [Bootstrap] Initializing & Verifying PostgreSQL Database..."
python3 init_database.py || true

# 3. Launch FastAPI Application Server
echo "🚀 [Bootstrap] Launching AutoParts SaaS Engine on port ${PORT:-8000}..."
exec python3 main.py
