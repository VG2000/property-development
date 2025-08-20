#!/usr/bin/env bash
set -euo pipefail

# Optional: wait for Postgres (compose v3 no longer supports depends_on: condition)
python - <<'PY'
import os, time, psycopg2
from urllib.parse import urlparse

url = os.environ["DATABASE_URL"]
p = urlparse(url)
for _ in range(30):
    try:
        psycopg2.connect(dbname=p.path.lstrip('/'), user=p.username, password=p.password,
                         host=p.hostname, port=p.port or 5432).close()
        break
    except Exception:
        time.sleep(2)
else:
    raise SystemExit("Postgres not available")
PY

# Run Django maintenance
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start gunicorn with sensible defaults (adjust workers for your vCPU count)
exec gunicorn property_development.wsgi:application \
  --bind 0.0.0.0:8003 \
  --workers ${GUNICORN_WORKERS:-3} \
  --threads ${GUNICORN_THREADS:-2} \
  --graceful-timeout 30 \
  --timeout 60 \
  --keep-alive 5 \
  --access-logfile - \
  --error-logfile - \
  --max-requests 1000 \
  --max-requests-jitter 200 \
  --preload
