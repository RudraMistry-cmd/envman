#!/usr/bin/env bash
# Redis readiness probe.
# Source: https://redis.io/docs/latest/develop/tools/cli/ (redis-cli -h -p PING -> PONG; -a/REDISCLI_AUTH)
set -euo pipefail
C="${1:-myredis}"; H="${REDIS_HOST:-127.0.0.1}"; P="${REDIS_PORT:-6379}"
ARGS=(redis-cli -h "$H" -p "$P" ping)
if [ -n "${REDISCLI_AUTH:-}" ]; then ARGS=(redis-cli -h "$H" -p "$P" ping); fi
OUT="$(timeout 7 docker exec -i "$C" "${ARGS[@]}" 2>&1)" || { echo "redis NOT READY: $OUT" >&2; exit 1; }
case "$OUT" in *PONG*) echo "redis READY: PONG";; *LOADING*) echo "redis LOADING (retry)" >&2; exit 2;; *NOAUTH*) echo "redis NOAUTH (set REDISCLI_AUTH)" >&2; exit 3;; *) echo "redis UNEXPECTED: $OUT" >&2; exit 4;; esac
