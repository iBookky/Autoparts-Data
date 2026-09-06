# ==========================================================
# AutoParts Cross-Reference SaaS Platform - Production Dockerfile
# Base: Python 3.11 Slim Linux
# ==========================================================

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    DB_PATH=/app/data/parts_cross_ref.db \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 -m -s /bin/bash appuser

# Set working directory
WORKDIR $APP_HOME

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY docs/ ./docs/
COPY index.html ./
COPY main.py ./
COPY scraper.py ./
COPY sheets_helper.py ./
COPY entrypoint.sh ./
COPY parts_cross_ref.db ./parts_cross_ref.db

# Create data directory for SQLite persistence and grant read/write permissions
RUN mkdir -p /app/data && \
    chmod +x /app/entrypoint.sh && \
    chmod -R 777 /app/data

# Expose HTTP port
EXPOSE 8000

# Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

