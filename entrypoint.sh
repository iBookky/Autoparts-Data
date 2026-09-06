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

# 2. Launch FastAPI Application Server (Python automatically runs schema migration & seeds)
echo "🚀 [Bootstrap] Launching AutoParts SaaS Engine on port ${PORT:-8000}..."
exec python3 main.py

