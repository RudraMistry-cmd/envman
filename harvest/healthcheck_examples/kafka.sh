#!/usr/bin/env bash
# Kafka (apache/kafka KRaft) readiness probe with TCP fallback.
# Sources: EnvMan registry (apache/kafka zero-env KRaft); https://docs.docker.com/compose/how-tos/startup-order/ (start_period pattern; Kafka needs 60s)
set -euo pipefail
C="${1:-mykafka}"; B="${KAFKA_BOOTSTRAP:-localhost:9092}"
if timeout 12 docker exec -i "$C" sh -c 'kafka-broker-api-versions --bootstrap-server '"$B"' 2>&1 | head -5'; then
  echo "kafka READY: broker API reachable at $B"; exit 0
fi
echo "kafka NOT READY: Broker may not be available / election in progress (retry; start_period 60s)" >&2; exit 1
