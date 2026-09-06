#!/bin/bash
# ==============================================================================
# AutoParts SaaS - 1-Click Build & Run Script for Plesk Server (Docker Extension)
# ==============================================================================

set -e

CONTAINER_NAME="autoparts-app"
IMAGE_NAME="autoparts-app:latest"
PORT="8000"
DATA_DIR="$(pwd)/data"
BACKUP_DIR="$(pwd)/backups"

echo "=================================================="
echo "🚀 Starting AutoParts Docker Deployment for Plesk"
echo "=================================================="

# 1. Create persistent storage folders
echo "[1/5] Setting up persistent data directories..."
mkdir -p "$DATA_DIR" "$BACKUP_DIR"
chmod 777 "$DATA_DIR"

# 2. Build Docker image
echo "[2/5] Building Docker Image ($IMAGE_NAME)..."
docker build -t "$IMAGE_NAME" .

# 3. Stop and remove existing container if running
if [ $(docker ps -aq -f name=^/${CONTAINER_NAME}$) ]; then
    echo "[3/5] Stopping and removing existing container ($CONTAINER_NAME)..."
    docker stop "$CONTAINER_NAME" || true
    docker rm "$CONTAINER_NAME" || true
fi

# 4. Run new container
echo "[4/5] Launching container on port 127.0.0.1:$PORT..."
docker run -d \
  --name "$CONTAINER_NAME" \
  --restart unless-stopped \
  -p 127.0.0.1:$PORT:8000 \
  -v "$DATA_DIR":/app/data \
  -e PORT=8000 \
  -e DB_PATH=/app/data/autoparts.db \
  -e ENVIRONMENT=production \
  "$IMAGE_NAME"

# 5. Verify Healthcheck
echo "[5/5] Waiting for service to become healthy..."
sleep 4
if docker ps | grep "$CONTAINER_NAME"; then
    echo "=================================================="
    echo "✅ DEPLOYMENT SUCCESSFUL!"
    echo "Container: $CONTAINER_NAME is running on 127.0.0.1:$PORT"
    echo "Persistent DB: $DATA_DIR/autoparts.db"
    echo ""
    echo "Next steps in Plesk:"
    echo "1. Go to Websites & Domains > Your Domain > Docker Proxy Rules"
    echo "2. Add Rule -> Container: $CONTAINER_NAME, Port: 8000"
    echo "3. Open your domain with HTTPS and start using the app!"
    echo "=================================================="
else
    echo "❌ Error: Container failed to start. View logs with: docker logs $CONTAINER_NAME"
    exit 1
fi
