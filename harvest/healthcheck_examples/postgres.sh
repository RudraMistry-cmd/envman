#!/usr/bin/env bash
# Postgres readiness probe — non-blocking, timeout-bounded.
# Sources:
#  - https://docs.docker.com/compose/how-tos/startup-order/ (pg_isready healthcheck, interval 10s retries 5 start_period 30s timeout 10s)
#  - https://hub.docker.com/_/postgres (POSTGRES_PASSWORD required; trust locally, password remote)
#  - https://docs.docker.com/reference/cli/docker/container/exec/ (explicit executable + sh -c)
set -euo pipefail
C="${1:-mydb}"; U="${POSTGRES_USER:-postgres}"; D="${POSTGRES_DB:-postgres}"
timeout 12 docker exec -i "$C" sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"' || {
  rc=$?; echo "postgres NOT READY (rc=$rc): starting up | FATAL password auth | connection refused" >&2; exit $rc; }
echo "postgres READY: accepting connections"
