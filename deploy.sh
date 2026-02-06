#!/bin/bash

# Deployment Script for OASIS Production
set -e

echo "🚀 Starting Deployment..."

# 1. Pull latest code
echo "📦 Pulling latest code..."
git pull origin main

# 2. Build and restart containers using Docker Compose
echo "🐳 Rebuilding and restarting containers..."
# Using --build to ensure latest code is used
# Using -d for detached mode
docker-compose up -d --build --scale backend=3

# 3. Wait for database to be ready (via healthcheck or sleep)
echo "⏳ Waiting for services to stabilize..."
sleep 10

# 4. Run Migrations
echo "🔄 Running Database Migrations..."
docker-compose exec -T backend python manage.py migrate

# 5. Collect Static Files
echo "🎨 Collecting Static Files..."
docker-compose exec -T backend python manage.py collectstatic --noinput

# 6. Cleanup unused images
echo "🧹 Cleaning up old images..."
docker image prune -f

echo "✅ Deployment Complete Successfully!"
