#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
if [ ! -f .local-db.env ]; then
  umask 077
  .venv/bin/python - <<'PY'
import secrets
from pathlib import Path
password=secrets.token_hex(24)
Path('.local-db.env').write_text('POSTGRES_PASSWORD='+password+'\nDATABASE_URL=postgresql://atom:'+password+'@127.0.0.1:54329/atom\n')
PY
fi
set -a
source .local-db.env
set +a
if ! docker container inspect atom-postgres >/dev/null 2>&1; then
  docker run -d --name atom-postgres --env-file .local-db.env -e POSTGRES_USER=atom -e POSTGRES_DB=atom -p 127.0.0.1:54329:5432 -v atom-postgres-data:/var/lib/postgresql/data postgres:17 >/dev/null
else
  docker start atom-postgres >/dev/null
fi
for attempt in {1..30}; do
  if docker exec atom-postgres pg_isready -U atom -d atom >/dev/null 2>&1; then break; fi
  sleep 1
done
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py seed_demo
.venv/bin/python manage.py collectstatic --noinput
if [ "${1:-}" = setup ]; then exit 0; fi
exec .venv/bin/python manage.py runserver 0.0.0.0:8000 --noreload
