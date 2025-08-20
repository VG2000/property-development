#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Waiting for Postgres..."

# ---- Wait for Postgres using psycopg (v3) -----------------------------------
python - <<'PY'
import os, time, sys
try:
    import psycopg
except Exception as e:
    print("psycopg import failed:", e, file=sys.stderr)
    sys.exit(1)

retries = int(os.getenv("DB_WAIT_RETRIES", "30"))
sleep = int(os.getenv("DB_WAIT_SLEEP", "2"))

def dsn_from_env():
    url = os.getenv("DATABASE_URL")
    if url:
        return url
    # Compose-style envs:
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    db   = os.getenv("POSTGRES_DB")
    user = os.getenv("POSTGRES_USER")
    pw   = os.getenv("POSTGRES_PASSWORD")
    if not all([db, user, pw]):
        print("Missing DB envs: set POSTGRES_DB/USER/PASSWORD or DATABASE_URL", file=sys.stderr)
        sys.exit(1)
    return f"postgresql://{user}:{pw}@{host}:{port}/{db}"

dsn = dsn_from_env()
for _ in range(retries):
    try:
        with psycopg.connect(dsn, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        break
    except Exception as e:
        time.sleep(sleep)
else:
    print("Postgres not available after retries", file=sys.stderr)
    sys.exit(1)
PY


# ---- Django maintenance ------------------------------------------------------
if [ "$APPLY_MIGRATIONS" = "1" ]; then
  echo "[entrypoint] Applying migrations..."
  python manage.py migrate --noinput
fi

if [ "$RUN_COLLECTSTATIC" = "1" ]; then
  echo "[entrypoint] Collecting static..."
  python manage.py collectstatic --noinput
fi

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
