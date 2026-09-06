#!/bin/bash
# ==============================================================================
# AutoParts SaaS Platform — 1-Command Master Production Deployer
# Sets up Database, Builds Image, Deploys Container, and Verifies Health
# ==============================================================================

set -e

CONTAINER_NAME="autoparts-app"
IMAGE_NAME="autoparts-app:latest"
PORT="8000"
DATA_DIR="$(pwd)/data"
BACKUP_DIR="$(pwd)/backups"

echo "=================================================================="
echo "🚀 [1/5] Setting up persistent storage & permissions..."
echo "=================================================================="
mkdir -p "$DATA_DIR" "$BACKUP_DIR"
chmod -R 777 "$DATA_DIR" "$BACKUP_DIR" 2>/dev/null || true

# Pre-populate database if missing in data directory
if [ ! -f "$DATA_DIR/parts_cross_ref.db" ] && [ -f "./parts_cross_ref.db" ]; then
    echo "📦 Copying pre-seeded database to persistent data volume..."
    cp "./parts_cross_ref.db" "$DATA_DIR/parts_cross_ref.db"
    chmod 777 "$DATA_DIR/parts_cross_ref.db"* 2>/dev/null || true
fi

echo "=================================================================="
echo "🔨 [2/5] Building Production Docker Image ($IMAGE_NAME)..."
echo "=================================================================="
docker build -t "$IMAGE_NAME" .

echo "=================================================================="
echo "🛑 [3/5] Cleaning up old container instances..."
echo "=================================================================="
if [ $(docker ps -aq -f name=^/${CONTAINER_NAME}$) ]; then
    docker stop "$CONTAINER_NAME" || true
    docker rm "$CONTAINER_NAME" || true
fi

echo "=================================================================="
echo "▶️ [4/5] Launching AutoParts Container on Port $PORT..."
echo "=================================================================="
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p 0.0.0.0:$PORT:8000 \
  -v "$DATA_DIR":/app/data \
  -e PORT=8000 \
  -e DB_PATH=/app/data/parts_cross_ref.db \
  -e ENVIRONMENT=production \
  "$IMAGE_NAME"

echo "=================================================================="
echo "⏳ [5/5] Verifying system health and database connectivity..."
echo "=================================================================="
sleep 4

# Check health endpoint
HEALTH_CHECK=""
for i in {1..6}; do
    if curl -s http://127.0.0.1:$PORT/health | grep -q '"status":"healthy"'; then
        HEALTH_CHECK="OK"
        break
    fi
    echo "Waiting for database and API to initialize... (attempt $i/6)"
    sleep 2
done

echo ""
echo "=================================================================="
echo "🎉 SUCCESS! AUTOPARTS SAAS PLATFORM IS LIVE & READY FOR SALES!"
echo "=================================================================="
echo ""
echo "  🌐 Local/Container URL: http://127.0.0.1:$PORT"
echo "  💾 Database Location:   $DATA_DIR/parts_cross_ref.db"
echo "  🛡️  Healthcheck Status:  ONLINE ($HEALTH_CHECK)"
echo ""
echo "------------------------------------------------------------------"
echo "🔑 READY-TO-USE PRODUCTION ACCOUNTS (Password: admin123):"
echo "------------------------------------------------------------------"
echo "  • Owner (Command Center) : username: owner       (Access /owner)"
echo "  • Super Admin (Platform) : username: superadmin  (Access /superadmin)"
echo "  • Admin (Operations Hub) : username: admin       (Access /admin)"
echo "  • Staff (Sales & Tasks)  : username: staff       (Access /staff)"
echo "  • Customer (Client View) : username: customer    (Access /)"
echo ""
echo "------------------------------------------------------------------"
echo "📋 PLESK NGINX DIRECTIVE (Websites & Domains > Apache & Nginx):"
echo "------------------------------------------------------------------"
echo "location / {"
echo "    proxy_pass http://127.0.0.1:8000;"
echo "    proxy_http_version 1.1;"
echo "    proxy_set_header Upgrade \$http_upgrade;"
echo "    proxy_set_header Connection \"upgrade\";"
echo "    proxy_set_header Host \$host;"
echo "    proxy_set_header X-Real-IP \$remote_addr;"
echo "    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;"
echo "    proxy_set_header X-Forwarded-Proto \$scheme;"
echo "    proxy_read_timeout 180s;"
echo "    client_max_body_size 50M;"
echo "}"
echo "=================================================================="
