# Verifier Patterns: Service-Readiness Probes (cited)
Date: 2026-09-10

Source URLs & quotes (<=25w):
- Compose startup order: "Compose does not wait until container is ready only until running" — https://docs.docker.com/compose/how-tos/startup-order/
- Compose healthcheck example: `pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}` interval 10s retries 5 start_period 30s timeout 10s — https://docs.docker.com/compose/how-tos/startup-order/
- Exec semantics: "command must be an executable" use `sh -c` wrapper — https://docs.docker.com/reference/cli/docker/container/exec/
- Compose up: `--wait` waits for running|healthy; `--wait-timeout` — https://docs.docker.com/reference/cli/docker/compose/up/
- redis-cli: `redis-cli -h <host> -p <port> PING` returns PONG; `-a` auth / REDISCLI_AUTH — https://redis.io/docs/latest/develop/tools/cli/
- Postgres Hub: `POSTGRES_PASSWORD` required, must not be empty; trust locally, password remote — https://hub.docker.com/_/postgres
- Elasticsearch: verify via `curl --cacert http_ca.crt -u elastic:$ELASTIC_PASSWORD https://localhost:9200` and `_cat/nodes` — https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic
- Hook/volume: pre_start hook retained on failure; `--renew-anon-volumes` — https://docs.docker.com/reference/cli/docker/compose/up/

## P1. Golden rule: running != ready
Always gate on `service_healthy` (Compose) + registry verifier poll of `Health.Status`, never `docker ps Up`. Compose long syntax:
```yaml
depends_on:
  db: {condition: service_healthy, restart: true}
```

## P2. Recommended configs (copy-paste defaults)
| Service | Test (exec, explicit exe) | interval | timeout | retries | start_period |
|---|---|---|---|---|---|
| Postgres | `["sh","-c",'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"']` | 10s | 10s | 5 | 30s |
| Redis | `["redis-cli","-h","127.0.0.1","-p","6379","ping"]` expect `PONG` (use `-a`/`REDISCLI_AUTH` when protected) | 5s | 5s | 10 | 10s |
| Kafka (apache/kafka KRaft) | `["sh","-c",'cub kafka-ready -b localhost:9092 1 30 || kafka-broker-api-versions --bootstrap-server localhost:9092']` (fallback: TCP connect 9092) | 10s | 10s | 12 | 60s |
| Elasticsearch | host-side `curl -k -u elastic:$PW https://localhost:9200` expect 200 + `cluster_name`; container-side `_cat/health?h=status` | 15s | 10s | 12 | 90s |
| Generic HTTP | `wget -qO- http://localhost:PORT/healthz` expect 2xx within timeout | 5s | 5s | 12 | 20s |
| Generic TCP | host socket connect (no curl in image, e.g. nats/typesense) | 5s | 5s | 12 | 20s |

Why: Postgres needs initdb + WAL replay (Hub: password required, first init slow); Redis fast but `LOADING`/`NOAUTH` transient; Kafka KRaft controller election 30-60s; ES JVM + bootstrap 60-90s + TLS cert.

## P3. Non-blocking probe mechanics
- Executor: `subprocess.run([...], shell=False, timeout=inner+5)` per probe; run verifiers concurrently (thread pool), never serial 4x90s.
- Layer checks: 1) `docker inspect State.{Running,Health.Status,OOMKilled,ExitCode}` 2) port TCP 3) app protocol (pg_isready/PING/curl). Return first failing layer with exact stderr.
- `compose up --wait --wait-timeout 120` for CLI parity; then `docker inspect --format={{.State.Health.Status}}`.

## P4. Real failure messages to match (race library)
- `connection refused` (app before db ready) | `FATAL: password authentication failed` (missing PGPASSWORD/-e) | `the database system is starting up` (pg replay) | `NOAUTH Authentication required` / `LOADING Redis is loading` | `Broker may not be available / Connection to node -1 could not be established` (Kafka election) | `curl: (7) Failed to connect` / `security_exception missing authentication` (ES TLS/auth) | `Container ... is paused, unpause before exec` (exec on paused) | `invalid mount config ... bind source path does not exist` (WSL path).

## P5. EnvMan registry mapping
Each registry entry: `{probe: {kind: exec|tcp|http, argv|port|url, expect}, timing: {interval, timeout, retries, start_period}, auth: {env vars}}`. Verifier polls until healthy/deadline, surfaces `attempt n/m + last stderr`.
