#!/bin/bash
# Script to update the AF3 Input Generator Docker container

echo "--- Updating AF3 Input Generator ---"

# Stop existing container
echo "[1/3] Stopping current container..."
docker-compose down

# Rebuild the image with no cache to ensure latest code is used
echo "[2/3] Rebuilding Docker image..."
docker-compose build --no-cache

# Start the container in detached mode
echo "[3/3] Starting new container..."
docker-compose up -d

echo "--- Update Complete! ---"
echo "Access the tool at: http://localhost:19999"
