#!/bin/bash
# Run every service's pytest suite inside its own container.
# Usage: scripts/run-tests.sh  (postgres is started automatically)
set -euo pipefail
cd "$(dirname "$0")/.."

status=0
for service in user-service post-service timeline-service; do
  echo "=== $service ==="
  docker compose run --rm --no-TTY "$service" sh -c \
    "pip install -q -r /deps/shared/requirements-dev.txt && python -m pytest -q" \
    || status=1
done
exit $status
