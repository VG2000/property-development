#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done
echo "PostgreSQL is up"

# Apply migrations
python manage.py migrate

# Collect static files for WhiteNoise
python manage.py collectstatic --noinput

# Start Gunicorn with 3 workers
exec gunicorn property_development.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 60
