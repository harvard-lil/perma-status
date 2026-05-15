#!/bin/sh
set -e

regenerate() {
  echo "Regenerating templates/index.html at $(date -u)"

  tmp_file="templates/_index.html"
  final_file="templates/index.html"

  if python index.py > "$tmp_file"; then
    mv "$tmp_file" "$final_file"
    echo "Finished regenerating templates/index.html at $(date -u)"
    return 0
  else
    rm -f "$tmp_file"
    echo "Failed regenerating templates/index.html at $(date -u)"
    return 1
  fi
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
    if regenerate; then
      echo "Reloading Gunicorn after template regeneration at $(date -u)"
      kill -HUP 1
    fi
  done
}

regenerate || echo "Startup regeneration failed at $(date -u); continuing with existing templates/index.html"

daily_regenerate_loop &

exec "$@"
