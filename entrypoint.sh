#!/bin/bash
set -e

# ==============================================================================
# AutoParts SaaS Platform - Zero-Touch Auto Database & Server Bootstrapper
# ==============================================================================

DATA_DIR=$(dirname "${DB_PATH:-/app/data/parts_cross_ref.db}")
DB_FILE="${DB_PATH:-/app/data/parts_cross_ref.db}"

# 1. Ensure persistent data directory exists with full read-write permissions
if [ -n "$DATA_DIR" ] && [ "$DATA_DIR" != "." ]; then
    mkdir -p "$DATA_DIR"
    chmod 777 "$DATA_DIR" 2>/dev/null || true
fi

# 2. Auto-provision database: if volume is empty, copy the pre-seeded production database
if [ ! -f "$DB_FILE" ]; then
    echo "📦 [Bootstrap] Initializing production database in $DB_FILE..."
    if [ -f "/app/parts_cross_ref.db" ]; then
        cp /app/parts_cross_ref.db "$DB_FILE"
        echo "✅ [Bootstrap] Pre-seeded production database copied successfully!"
    fi
fi

# 3. Grant full read-write permissions to database, WAL, and SHM files
if [ -n "$DATA_DIR" ] && [ -d "$DATA_DIR" ]; then
    chmod -R 777 "$DATA_DIR" 2>/dev/null || true
fi

# 4. Launch FastAPI Application Server
echo "🚀 [Bootstrap] Launching AutoParts SaaS Engine on port ${PORT:-8000}..."
exec python main.py
