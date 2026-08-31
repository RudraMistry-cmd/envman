# Phase 2: Service Expansion — Task Breakdown

**Goal:** Add 8 new services with real health checks (no tcp_port placeholders)
**Scope:** sqlite, couchdb, kafka, nats, elasticsearch, meilisearch, typesense, minio

---

## Architecture Decisions (FLAGGED)

### Decision 1: Inline Pattern vs Plugin Pattern

**Current state (repo):** All health checks are inline functions in `verifier.py` (342 lines), dispatched by `health_check_type` string via `HEALTH_CHECK_DISPATCH` map.

**Spec state (TECHNICAL_SPEC.md Part 2E):** Proposes a `verifier_plugins/` directory with one file per service, using abstract `HealthCheckPlugin` base class.

**Recommendation: Keep inline pattern for Phase 2.**
- Adding 8 new health check types is ~150 lines of new code (HTTP check function is reusable across 5 services).
- `verifier.py` would grow to ~500 lines — manageable, not bloated.
- Plugin refactor is a separate concern (Phase 1 tech debt, not Phase 2 scope).
- Inline pattern matches existing codebase conventions — no new abstractions needed.

**If verifier.py exceeds 800 lines in future:** Extract to `verifier_plugins/` as a separate task.

### Decision 2: mongo → mongodb Naming

**Current state:** Registry has `id="mongo"`, `image="mongo"`, config files reference `mongo`.

**Spec state:** Uses `id="mongodb"`, `image="mongo:{version}"`.

**Recommendation: Keep `id="mongo"` in registry, fix health check only.**
- Renaming would break existing `envman.yaml` configs referencing `mongo`.
- The `id` is a user-facing identifier — changing it is a breaking change.
- Fix: Update `health_check_type` from `"tcp_port"` to `"mongo_ping"` and add real mongosh health check.
- The spec's `MongoHealthCheck` class (spec line 1839) already works with the `mongo` image — only the registry `id` differs.

### Decision 3: SQLite as Container Service

**Current state:** Not in registry.

**Spec state:** Defines `sqlite` with `docker_image_template="sqlite:latest"`, `default_port=0`.

**Recommendation: Add as a special-case entry with `health_check_type="sqlite_version"`.**
- SQLite IS a valid service in EnvMan's context — devs need to know it's available.
- No daemon to health-check — verification just confirms the CLI binary is present inside the container.
- Health check: `docker exec <container> sqlite3 --version` (command check, not TCP/HTTP).
- If user provides a custom SQLite container image, the version check still works.
- Mark `default_port=None` (no network port).

---

## Discrepancy: Schema Divergence (Spec vs Repo)

The TECHNICAL_SPEC.md defines a much richer `ServiceDefinition` (with `HealthCheckConfig`, `VolumeMount`, `description`, `available_versions`, etc.) than what exists in the repo (simple `health_check_type` string).

**Phase 2 does NOT address this.** The spec schema is aspirational; the repo schema is the working implementation. Phase 2 adds services to the existing schema. Schema alignment is a separate Phase 1 tech-debt task.

---

## Task Breakdown

### Task 1: Add 8 New ServiceDefinitions to services.py
**File:** `backend/app/registry/services.py`
**Depends on:** Nothing (parallel-safe with all other tasks)
**Estimated effort:** Small (list append operations)

Add 8 new `ServiceDefinition` entries to the `SERVICES` list:

| id | name | category | image | default_port | health_check_type |
|----|------|----------|-------|-------------|-------------------|
| `sqlite` | SQLite | database | `sqlite` | None | `sqlite_version` |
| `couchdb` | CouchDB | database | `couchdb` | 5984 | `http_get` |
| `kafka` | Kafka | message_broker | `confluentinc/cp-kafka` | 9092 | `kafka_api_version` |
| `nats` | NATS | message_broker | `nats` | 4222 | `http_get` (port 8222) |
| `elasticsearch` | Elasticsearch | search | `elasticsearch` | 9200 | `http_get` |
| `meilisearch` | MeiliSearch | search | `getmeili/meilisearch` | 7700 | `http_get` |
| `typesense` | Typesense | search | `typesense/typesense` | 8108 | `http_get_with_api_key` |
| `minio` | MinIO | storage | `minio/minio` | 9000 | `http_get` |

**Also fix:** Update existing `mongo` entry's `health_check_type` from `"tcp_port"` to `"mongo_ping"`.

### Task 2: Add Health Check Functions to verifier.py
**File:** `backend/app/engine/verifier.py`
**Depends on:** Nothing (parallel-safe with services.py changes)
**Estimated effort:** Medium (~150 lines of new code)

#### 2a: Add `_http_get_check` (shared by couchdb, elasticsearch, meilisearch, minio)
```python
async def _http_get_check(container_name: str, url: str, timeout: int = 5) -> Dict[str, Any]:
    """HTTP GET health check — runs curl inside container."""
    result = await run_command([
        "docker", "exec", container_name,
        "curl", "-sf", "--max-time", str(timeout), url
    ])
    return {
        "success": result["code"] == 0,
        "output": result["stdout"] if result["code"] == 0 else result["stderr"],
    }
```

#### 2b: Add `_http_get_with_api_key_check` (for typesense)
```python
async def _http_get_with_api_key_check(container_name: str, url: str, api_key: str) -> Dict[str, Any]:
    """HTTP GET with API key header — for typesense."""
    result = await run_command([
        "docker", "exec", container_name,
        "curl", "-sf", "-H", f"X-TYPESENSE-API-KEY: {api_key}", url
    ])
    return {
        "success": result["code"] == 0,
        "output": result["stdout"] if result["code"] == 0 else result["stderr"],
    }
```

#### 2c: Add `_mongo_ping` (real mongosh check, replaces tcp_port)
```python
async def _mongo_ping(container_name: str) -> Dict[str, Any]:
    """Check MongoDB responds to ping via mongosh."""
    result = await run_command([
        "docker", "exec", container_name,
        "mongosh", "--eval", "db.adminCommand({ping:1})", "--quiet"
    ])
    return {
        "success": result["code"] == 0,
        "output": result["stdout"] if result["code"] == 0 else result["stderr"],
    }
```

#### 2d: Add `_kafka_api_version` (broker API version probe)
```python
async def _kafka_api_version(container_name: str) -> Dict[str, Any]:
    """Check Kafka broker is ready via API version probe."""
    result = await run_command([
        "docker", "exec", container_name,
        "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"
    ])
    return {
        "success": result["code"] == 0,
        "output": result["stdout"][:200] if result["code"] == 0 else result["stderr"],
    }
```

#### 2e: Add `_sqlite_version` (embedded DB — just confirms binary exists)
```python
async def _sqlite_version(container_name: str) -> Dict[str, Any]:
    """Check SQLite CLI is available in the container."""
    result = await run_command([
        "docker", "exec", container_name, "sqlite3", "--version"
    ])
    return {
        "success": result["code"] == 0,
        "version": result["stdout"].strip() if result["code"] == 0 else None,
    }
```

#### 2f: Update HEALTH_CHECK_DISPATCH map
```python
HEALTH_CHECK_DISPATCH = {
    "pg_isready": "_pg_is_ready",
    "redis_ping": "_redis_ping",
    "node_version": "_node_version",
    "tcp_port": "_tcp_port_check",
    # Phase 2 additions:
    "mongo_ping": "_mongo_ping",
    "http_get": "_http_get_check",
    "http_get_with_api_key": "_http_get_with_api_key_check",
    "kafka_api_version": "_kafka_api_version",
    "sqlite_version": "_sqlite_version",
}
```

#### 2g: Update `_verify_service` dispatch logic
Add `elif` branches for each new health check type in the `_verify_service` function (lines 227-280).

### Task 3: Fix mongo Health Check (Upgrade from tcp_port)
**File:** `backend/app/registry/services.py` + `backend/app/engine/verifier.py`
**Depends on:** Task 1 + Task 2 (needs both new service entry and new health function)
**Estimated effort:** Trivial (change one string in services.py, add dispatch branch in verifier.py)

Change mongo's `health_check_type` from `"tcp_port"` to `"mongo_ping"`.

### Task 4: Verify No Regressions (Existing Services)
**File:** None (verification only)
**Depends on:** Tasks 1-3
**Estimated effort:** Small

Confirm that existing 7 services (node, python, postgres, mysql, redis, mongo, rabbitmq) still work correctly after changes. Run:
- `python -c "from app.registry.services import get_all_services; print(len(get_all_services()))"` — should return 15
- `python -c "from app.engine.verifier import HEALTH_CHECK_DISPATCH; print(list(HEALTH_CHECK_DISPATCH.keys()))"` — should include all new types

---

## Service Health Check Specifications

### sqlite
- **Type:** `sqlite_version`
- **Implementation:** `docker exec <container> sqlite3 --version`
- **Why not HTTP/TCP:** Embedded DB — no daemon, no network port. Verifies the CLI binary is present.
- **Port:** None
- **Retry:** No (instant check)

### couchdb
- **Type:** `http_get`
- **URL:** `http://localhost:5984/_up`
- **Why:** CouchDB exposes a `_up` endpoint returning JSON `{"status":"ok"}`.
- **Port:** 5984
- **Retry:** 3 attempts, 2s delay (CouchDB starts fast)

### kafka
- **Type:** `kafka_api_version`
- **Command:** `kafka-broker-api-versions --bootstrap-server localhost:9092`
- **Why:** Official Kafka readiness check — proves broker accepts connections and responds.
- **Port:** 9092
- **Retry:** 5 attempts, 3s delay (Kafka takes 15-30s to start)

### nats
- **Type:** `http_get`
- **URL:** `http://localhost:8222/healthz`
- **Why:** NATS monitoring port (8222) exposes `/healthz` returning `200 OK`.
- **Port:** 4222 (service), 8222 (monitoring)
- **Note:** Requires NATS started with `-m 8222` flag (monitoring port)

### elasticsearch
- **Type:** `http_get`
- **URL:** `http://localhost:9200/_cluster/health`
- **Why:** Returns JSON with `"status":"green"` or `"status":"yellow"`. Both are healthy.
- **Port:** 9200
- **Retry:** 5 attempts, 5s delay (ES takes 20-30s to start)

### meilisearch
- **Type:** `http_get`
- **URL:** `http://localhost:7700/health`
- **Why:** Returns `{"status":"available"}` when ready.
- **Port:** 7700
- **Retry:** 3 attempts, 2s delay

### typesense
- **Type:** `http_get_with_api_key`
- **URL:** `http://localhost:8108/health`
- **API Key Header:** `X-TYPESENSE-API-KEY: <key>`
- **Why:** Typesense requires API key for all endpoints including health.
- **Port:** 8108
- **Note:** API key must be passed from service's `default_env` (`TYPESENSE_API_KEY`)

### minio
- **Type:** `http_get`
- **URL:** `http://localhost:9000/minio/health/live`
- **Why:** MinIO's liveness probe — returns 200 when ready.
- **Port:** 9000
- **Retry:** 3 attempts, 2s delay

---

## Parallelization Strategy

```
┌─────────────────────────────────────────────────────────┐
│  PARALLEL GROUP 1 (no dependencies)                     │
│  ├── Task 1: Add services to services.py                │
│  └── Task 2: Add health checks to verifier.py           │
│      (2a-2g can all be done in one pass of verifier.py) │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  PARALLEL GROUP 2 (depends on Group 1)                  │
│  └── Task 3: Fix mongo health check (trivial)           │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  FINAL: Task 4: Verify no regressions                   │
└─────────────────────────────────────────────────────────┘
```

**Key insight:** Tasks 1 and 2 touch different files (`services.py` vs `verifier.py`) so they can run in parallel. Task 3 needs both files updated first. Task 4 is verification only.

---

## Risks & Gotchas

1. **Kafka startup time:** 15-30 seconds. Health check retries must accommodate this. Use 5 retries × 3s = 15s minimum wait.
2. **Elasticsearch memory:** Requires 1Gi+ RAM. May fail on low-memory machines. Document this.
3. **NATS monitoring port:** Must be enabled via `-m 8222` in container command. The registry entry should include `default_env` or `command` to enable it.
4. **Typesense API key:** Health check needs the API key from `default_env`. The dispatch must pass this through.
5. **SQLite image:** There's no official `sqlite` Docker image. Users will typically install sqlite inside their own containers. The health check should handle "sqlite3 not found" gracefully.
6. **mongo naming:** Existing configs reference `mongo` — DO NOT rename to `mongodb`. Only fix the health check type.

---

## Verification Checklist

After implementation, confirm:
- [ ] `get_all_services()` returns 15 services (7 existing + 8 new)
- [ ] `HEALTH_CHECK_DISPATCH` has 9 entries (4 existing + 5 new)
- [ ] mongo uses `mongo_ping` not `tcp_port`
- [ ] No service uses `tcp_port` as a placeholder (mysql and rabbitmq still use it legitimately — they have real TCP services)
- [ ] All HTTP-based health checks use `curl -sf` (silent + fail-fast)
- [ ] Kafka check retries at least 5 times with 3s delay
- [ ] SQLite check handles missing binary gracefully
