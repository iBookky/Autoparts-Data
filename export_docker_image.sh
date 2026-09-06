#!/bin/bash
# ==============================================================================
# AutoParts SaaS - Local Docker Image Build & Export Script
# Builds the Docker Image and packages it into a .tar file for easy upload to Plesk
# ==============================================================================

set -e

IMAGE_NAME="autoparts-app:latest"
TAR_NAME="autoparts-image.tar.gz"

echo "=================================================="
echo "📦 Packaging AutoParts Docker Image for Plesk"
echo "=================================================="

# 1. Build Docker image locally
echo "[1/3] Building Docker image ($IMAGE_NAME)..."
docker build -t "$IMAGE_NAME" .

# 2. Save & Gzip Docker image
echo "[2/3] Exporting and compressing image to $TAR_NAME..."
docker save "$IMAGE_NAME" | gzip > "$TAR_NAME"

echo "[3/3] Export completed successfully!"
echo "=================================================="
echo "File created: $(pwd)/$TAR_NAME"
echo ""
echo "How to upload and run on Plesk Server:"
echo "1. Upload $TAR_NAME to your Plesk server (via SCP, SFTP, or Plesk File Manager)"
echo "2. On Plesk SSH/Terminal, run:"
echo "   docker load < $TAR_NAME"
echo "3. Run the container on Plesk:"
echo "   docker run -d --name autoparts-app --restart unless-stopped -p 127.0.0.1:8000:8000 -v /var/www/vhosts/yourdomain.com/data:/app/data autoparts-app:latest"
echo "4. In Plesk > Websites & Domains > Docker Proxy Rules > Add Rule (Port 8000)"
echo "=================================================="
