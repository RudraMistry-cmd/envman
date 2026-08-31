# EnvMan — Phase 2 Planning Learnings

## Architecture Decisions (2026-08-31)

### Inline vs Plugin Pattern
- **Decision:** Keep inline pattern in `verifier.py` for Phase 2
- **Rationale:** Adding 8 health checks = ~150 lines, total ~500 lines. Manageable.
- **Trigger for plugin refactor:** If verifier.py exceeds 800 lines
- **Spec reference:** TECHNICAL_SPEC.md Part 2E proposes `verifier_plugins/` directory

### mongo vs mongodb Naming
- **Decision:** Keep `id="mongo"` in registry, only fix health check
- **Rationale:** Renaming breaks existing `envman.yaml` configs. The `id` is user-facing.
- **Action:** Change `health_check_type` from `"tcp_port"` to `"mongo_ping"`
- **Spec uses:** `id="mongodb"` — this is a spec-repo divergence, not a bug

### SQLite as Container Service
- **Decision:** Add as special-case with `health_check_type="sqlite_version"`
- **Rationale:** SQLite IS a valid service — devs need to know it's available
- **Health check:** `docker exec <container> sqlite3 --version` (verifies binary exists)
- **No daemon:** Embedded DB has no network port, no TCP/HTTP check possible

## Schema Divergence (Spec vs Repo)

The TECHNICAL_SPEC.md defines a richer `ServiceDefinition` than the repo:
- Spec: `HealthCheckConfig`, `VolumeMount`, `description`, `available_versions`, `resource_requirements`, `tags`
- Repo: `id`, `name`, `category`, `image`, `default_port`, `default_env`, `health_check_type`

**Phase 2 does NOT address this.** Schema alignment is a separate tech-debt task.

## Health Check Patterns Discovered

### HTTP-based checks (couchdb, elasticsearch, meilisearch, minio)
- All use `curl -sf <url>` inside container
- Single reusable function: `_http_get_check(container_name, url)`
- Response: `{"success": bool, "output": str}`

### HTTP with auth (typesense)
- Needs `X-TYPESENSE-API-KEY` header
- Separate function: `_http_get_with_api_key_check(container_name, url, api_key)`

### Command-based checks (kafka, mongo)
- Kafka: `kafka-broker-api-versions --bootstrap-server localhost:9092`
- Mongo: `mongosh --eval 'db.adminCommand({ping:1})' --quiet`
- Both run via `docker exec`

### Embedded/no-op checks (sqlite)
- SQLite: `sqlite3 --version` (just confirms binary exists)

## Parallelization Insight

Tasks 1 (services.py) and 2 (verifier.py) touch DIFFERENT files → can run in parallel.
Task 3 (mongo fix) depends on both → sequential after Group 1.
Task 4 (verification) depends on all → final step.

## Risk Register

| Risk | Mitigation |
|------|-----------|
| Kafka 15-30s startup | 5 retries × 3s delay = 15s minimum |
| Elasticsearch 1Gi RAM | Document memory requirement |
| NATS needs `-m 8222` | Add monitoring port to default command |
| Typesense API key | Pass from `default_env` through dispatch |
| SQLite no official image | Handle "sqlite3 not found" gracefully |
