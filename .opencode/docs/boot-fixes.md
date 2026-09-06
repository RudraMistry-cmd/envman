# Boot fixes research (2026-09-06, Commander direct - Planner unavailable)

## Decision: kafka -> apache/kafka (image switch, zero env)
- Official apache/kafka image boots standalone KRaft combined-mode with NO env:
  `docker run -d --name broker apache/kafka:latest` (quickstart, verified doc).
- cp-kafka alternative requires CLUSTER_ID generation + full KRaft env set -
  fragile vs image default. Switch wins on reliability.
- Source: https://hub.docker.com/r/apache/kafka (cached .opencode/docs/hub_docker_com_r_apache_kafka.md)
- Explicit combined-mode env set (for reference only, NOT used):
  KAFKA_NODE_ID=1, KAFKA_PROCESS_ROLES=broker,controller,
  KAFKA_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093,
  KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092,
  KAFKA_CONTROLLER_LISTENER_NAMES=CONTROLLER,
  KAFKA_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT,
  KAFKA_CONTROLLER_QUORUM_VOTERS=1@localhost:9093,
  KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1,
  KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR=1,
  KAFKA_TRANSACTION_STATE_LOG_MIN_ISR=1, KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS=0
- Frontend kafka version: 7.5.16 (Confluent numbering) -> 3.8.0 (Apache numbering).
- OPEN: health-check binary path - verifier runs `kafka-broker-api-versions`
  (cp-kafka wrapper name). apache/kafka ships /opt/kafka/bin/*.sh, PATH
  uncertain. E2E must confirm; fix to full path if needed.
- Tests referencing confluentinc/cp-kafka:7.5.16 must move to apache/kafka:3.8.0
  (test_service_definitions.py x2, test_verifier.py x1).

## mysql: MYSQL_ALLOW_EMPTY_PASSWORD=yes
- Official image REFUSES boot without one of MYSQL_ROOT_PASSWORD /
  MYSQL_ALLOW_EMPTY_PASSWORD / MYSQL_RANDOM_ROOT_PASSWORD.
- `yes` gives blank root password - matches app's mysql://root@localhost:PORT/.
- Source: https://hub.docker.com/_/mysql (cached .opencode/docs/hub_docker_com___mysql.md)

## elasticsearch 8.14 single-node, security off
- default_env: {"discovery.type": "single-node", "xpack.security.enabled": "false"}.
- 8.x still honors both (discovery.type needed to skip bootstrap checks;
  xpack flag restores plain-http 9200 so the app's http_get health check works).
- No heap override (memory pressure slows boot, doesn't exit).
- OPEN: pullability of `elasticsearch:8.14.0` from Docker Hub (official
  images moved to docker.elastic.co). E2E pull proves it; fallback is
  docker.elastic.co/elasticsearch/elasticsearch:8.14.3 + registry prefix update.

## minio: command required + creds
- Official: `server /data --console-address ":9001"` (command args AFTER image).
  Without a command the image prints help and exits.
- Expose 9000 (API + health /minio/health/live). 9001 console stays internal
  (ServiceSpec supports one port).
- default_env explicit MINIO_ROOT_USER/MINIO_ROOT_PASSWORD=minioadmin
  (== image defaults, documents creds).
- Source: https://hub.docker.com/r/minio/minio (cached .opencode/docs/hub_docker_com_r_minio_minio.md)

## postgres: POSTGRES_PASSWORD REQUIRED (found live 2026-09-06)
- Fresh `postgres:16` exits: "Database is uninitialized and superuser
  password is not specified... You must specify POSTGRES_PASSWORD".
- Prior "observed working" claims were wrong for fresh boots (old containers
  were all exited too). Fix: default_env POSTGRES_PASSWORD=postgres +
  PGPASSWORD=postgres in verifier's psql exec (pg_isready needs no password).

## couchdb: admin user REQUIRED (found live 2026-09-06)
- CouchDB 3.x exits: 'will no longer run in "Admin Party" mode. You *MUST*
  specify an admin user and password' via COUCHDB_USER/COUCHDB_PASSWORD.
- Fix: default_env both =admin. /_up readability with auth on: proven by E2E.

## nats: no curl, NO SHELL -> host-side tcp probe (found live 2026-09-06)
- nats:2 image has no curl (code 127) AND no sh/bash at all, so the old
  docker-exec bash /dev/tcp check can never run there either.
- Fix: _tcp_port_check rewritten as backend host-side socket connect to the
  verified HostPort (uniform for mysql/rabbitmq/nats; also directly proves
  host reachability). health_check_type=tcp_port on 4222.
- Same crash exposed a second bug: _http_get_check result had no "error"
  key, so EVERY failed http check raised KeyError instead of reporting
  failed. Fixed (both http helpers now return error key).

## typesense: needs --data-dir /tmp + has no curl (found live 2026-09-06)
- TYPESENSE_DATA_DIR env alone insufficient: /data doesn't exist in image.
  Working combo: default_command=["--data-dir", "/tmp"] + TYPESENSE_API_KEY
  env. /health 200 {"ok":true} proven from host with key header.
- No curl in image -> health_check_type=tcp_port on 8108.

## kafka on apache/kafka: zero-env boot + .sh binary path (found live 2026-09-06)
- apache/kafka:3.8.0 boots standalone with NO env (KRaft combined defaults);
  broker id 1 answers localhost:9092, real 9092 binding.
- Health check fixed: cp-kafka's bare `kafka-broker-api-versions` wrapper
  doesn't exist; use `bash /opt/kafka/bin/kafka-broker-api-versions.sh`.

## E2E 14-table (fresh boots, 2026-09-06, registry-sourced env/command)
| service | boots/stays running 10s+ | health check | notes |
|---|---|---|---|
| node | NO (REPL EOF, exits) | n/a not_running | by design; needs follow-up (sleep infinity?) |
| python | NO (same) | n/a not_running | same |
| postgres | YES | pg_isready P + query P | POSTGRES_PASSWORD fix |
| mysql | YES | tcp P (host probe) | ALLOW_EMPTY_PASSWORD fix |
| mongo | YES | mongo_ping P | no change needed |
| redis | YES | redis_ping P | no change needed |
| rabbitmq | YES | tcp P (host probe) | no change needed |
| couchdb | YES | http_get P (/_up public) | admin creds fix |
| nats | YES | tcp P (host probe) | tcp_port switch; no shell in image |
| elasticsearch | YES | http_get P, host green | 2-env fix; image pulls fine |
| meilisearch | YES | http_get P | curl present; no change |
| typesense | YES | tcp P; host /health 200 ok:true | --data-dir /tmp command; no curl |
| minio | YES | http_get P | server /data command works end-to-end |
| kafka | YES (id 1, KRaft) | kafka_api_version P | apache/kafka zero-env; .sh path fix |
All Ports columns showed real 0.0.0.0:port->port bindings matching the app's
reported host ports. E2E containers removed afterwards.

## node/python keep-alive (follow-up mission, proven 2026-09-06)
- Bare node/python images launch a REPL that hits EOF under `docker run -d`
  and exits, so version checks ran against dead containers.
- Fix: default_command=["tail", "-f", "/dev/null"] (not sleep infinity:
  tail exists even on slim/busybox). Proven via REAL /setup flow (not manual
  docker): envman_node running 18s+, node -v v20.20.2; envman_python running
  13s+, python3 3.12.14. Both envs deleted afterwards via API.

## containers-table migration (found live 2026-09-06)
- T1.5 added host_port/connection_string columns to CREATE TABLE + writer,
  but CREATE TABLE IF NOT EXISTS never migrates the existing 5-col table,
  so EVERY save_container failed ("no column named host_port", swallowed by
  try/except) and DELETE orphaned running containers.
- Fix: PRAGMA-guarded ALTER TABLE ADD COLUMN in init_db (idempotent).
- Proven: post-migration /setup persisted the row, dashboard listed it,
  DELETE removed the container.

## Spot-checks (to be proven by E2E table, not assumed)
- postgres: starts passwordless with warning only. mongo: no-auth default.
- redis: no-auth default. rabbitmq: guest/guest local-only, tcp check ok.
- couchdb 3.x: admin-party mode, /_up 200. nats: 4222 + 8222/healthz defaults.
- meilisearch: /health open without MASTER_KEY. typesense: TYPESENSE_API_KEY
  env + keyed health check already wired. node/python: no ports, version checks.
- All 8 confirmed by the E2E 14-table (fresh boot each), not by assumption.
