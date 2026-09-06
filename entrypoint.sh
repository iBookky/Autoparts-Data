#!/bin/bash
set -e

# Automatically ensure SQLite data directory and database files have read-write permissions
DATA_DIR=$(dirname "${DB_PATH:-/app/data/parts_cross_ref.db}")
if [ -n "$DATA_DIR" ] && [ "$DATA_DIR" != "." ]; then
    mkdir -p "$DATA_DIR"
    chmod 777 "$DATA_DIR" 2>/dev/null || true
    if [ -d "$DATA_DIR" ]; then
        chmod -R 777 "$DATA_DIR" 2>/dev/null || true
    fi
fi

# Execute main server process
exec python main.py
