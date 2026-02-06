#!/bin/bash

# Wait for database
echo "Waiting for database..."
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-3306}
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "Database started"

# Create logs directory
mkdir -p /app/logs

# Start server
echo "Starting server..."
# Workers = 2 * CPU + 1 (Assuming 1-2 cores safe default for cloud Basic) -> 3 workers
# Timeout = 30s to prevent long hanging requests
gunicorn OASIS.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 30 \
    --access-logfile /app/logs/gunicorn_access.log \
    --error-logfile /app/logs/gunicorn_error.log
