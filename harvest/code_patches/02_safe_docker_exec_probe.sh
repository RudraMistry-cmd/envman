#!/usr/bin/env bash
# Sources:
#  - https://docs.docker.com/reference/cli/docker/container/exec/ ("command must be an executable; chained command doesn't work")
#  - https://docs.docker.com/engine/containers/run/ (exit 125/126/127 semantics)
# Purpose: safe docker-exec verifier probe EnvMan registry should use (no shell=True).
set -euo pipefail
CONTAINER="${1:-mydb}"
# Correct: explicit executable + sh -c wrapper
docker exec -i "$CONTAINER" sh -c 'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'
echo "exit=$? (0=healthy; 1=paused/not-ready; 125=daemon; 126=not invocable; 127=not found)"
# Paused-container reproducer:
# docker pause "$CONTAINER"; docker exec "$CONTAINER" sh || echo "paused -> unpause first"
# Env probing with -e (inherits only at create time otherwise):
# docker exec -e VAR_A=1 -e VAR_B=2 "$CONTAINER" env
