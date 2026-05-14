#!/bin/sh
set -e

regenerate() {
  echo "Regenerating templates/index.html at $(date -u)"
  python index.py > templates/_index.html
  mv templates/_index.html templates/index.html
  echo "Finished regenerating templates/index.html at $(date -u)"
}

seconds_until_0016_utc() {
  python - <<'PY'
from datetime import datetime, timedelta, timezone

now = datetime.now(timezone.utc)
target = now.replace(hour=0, minute=16, second=0, microsecond=0)

if target <= now:
    target += timedelta(days=1)

print(int((target - now).total_seconds()))
PY
}

daily_regenerate_loop() {
  while true; do
    sleep "$(seconds_until_0016_utc)"
    regenerate || echo "Failed regenerating templates/index.html at $(date -u)"
  done
}

regenerate || echo "Startup regeneration failed at $(date -u); continuing with existing templates/index.html"

daily_regenerate_loop &

exec "$@"
