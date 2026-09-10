#!/usr/bin/env bash
# Source: https://docs.docker.com/compose/how-tos/startup-order/
# Quote (<=25w): "Compose does not wait until container is ready only until running"
# Purpose: canonical postgres health-gated Compose snippet EnvMan should generate/verify.
set -euo pipefail
cat > compose.healthy.yaml <<'YAML'
services:
  db:
    image: postgres:18
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-app}
      POSTGRES_DB: ${POSTGRES_DB:-appdb}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]
      interval: 10s
      retries: 5
      start_period: 30s
      timeout: 10s
  web:
    build: .
    depends_on:
      db:
        condition: service_healthy
        restart: true
YAML
docker compose -f compose.healthy.yaml up -d --wait --wait-timeout 120
docker inspect --format='{{.State.Health.Status}}' "$(docker compose -f compose.healthy.yaml ps -q db)"
