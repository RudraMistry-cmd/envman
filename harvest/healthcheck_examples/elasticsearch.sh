#!/usr/bin/env bash
# Elasticsearch readiness probe (host-side TLS + auth).
# Source: https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic
#   (curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200 ; _cat/nodes)
set -euo pipefail
PW="${ELASTIC_PASSWORD:?set ELASTIC_PASSWORD}"; CERT="${ES_CERT:-http_ca.crt}"; PORT="${ES_PORT:-9200}"
OUT="$(curl -s --max-time 10 --cacert "$CERT" -u "elastic:$PW" "https://localhost:$PORT" 2>&1)" || { echo "ES NOT READY: curl failed (JVM bootstrap 60-90s?)" >&2; exit 1; }
echo "$OUT" | grep -q '"cluster_name"' && echo "ES READY: cluster reachable" || { echo "ES NOT READY: $OUT" >&2; exit 2; }
curl -s --max-time 10 --cacert "$CERT" -u "elastic:$PW" "https://localhost:$PORT/_cat/health?h=status" || true
