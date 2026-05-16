#!/bin/sh
set -e
if [ ! -f dummy/medassist.db ]; then
  echo "[entrypoint] No dummy/medassist.db — running seed..."
  python dummy/seed.py
fi
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
