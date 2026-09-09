# ==========================================================
# AutoParts Cross-Reference SaaS Platform - Production Dockerfile
# Base: Python 3.11 Slim Linux
# ==========================================================

FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PORT=8000

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -u 1000 -m -s /bin/bash appuser

# Set working directory
WORKDIR $APP_HOME

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files and pre-seeded database
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY docs/ ./docs/
COPY uploads/ ./uploads/
COPY index.html ./
COPY main.py ./
COPY scraper.py ./
COPY view_db.py ./
COPY migrate_sqlite_to_pg.py ./
COPY init_database.py ./
COPY tests/ ./tests/
COPY entrypoint.sh ./

# Create uploads directory for persistence and grant read-write permissions
RUN mkdir -p /app/uploads/logos && \
    chmod +x /app/entrypoint.sh && \
    chmod -R 777 /app/uploads 2>/dev/null || true



# Expose HTTP port
EXPOSE 8000

# Container Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Production Entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

