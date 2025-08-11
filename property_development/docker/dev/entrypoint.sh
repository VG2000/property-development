#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
  sleep 1
done
echo "PostgreSQL is up"

# Apply migrations
python manage.py migrate

# Collect static files (needed for Leaflet map in admin!)
python manage.py collectstatic --noinput

python manage.py ensure_dev_superuser

# Run development server
exec python manage.py runserver 0.0.0.0:8000
