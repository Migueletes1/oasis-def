#!/bin/bash

# Deployment Script for OASIS Production
set -e

echo "Starting Deployment..."

# 1. Pull latest code
echo "Pulling latest code..."
git pull origin main

# 2. Build containers (sin escalar aun)
echo "Building containers..."
docker-compose build

# 3. Run migrations ANTES de escalar (usa contenedor temporal one-off)
echo "Running Database Migrations..."
docker-compose run --rm backend python manage.py migrate

# 4. Collect Static Files
echo "Collecting Static Files..."
docker-compose run --rm backend python manage.py collectstatic --noinput

# 5. Levantar servicios y escalar backend
echo "Starting services and scaling backend..."
docker-compose up -d --scale backend=3

# 6. Esperar a que los servicios esten listos via healthcheck
echo "Waiting for services to stabilize..."
sleep 10

# 7. Cleanup unused images
echo "Cleaning up old images..."
docker image prune -f

echo "Deployment Complete Successfully!"
