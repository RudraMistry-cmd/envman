# EnvMan Project Context

## Project Overview
- **Repo**: https://github.com/RudraMistry-cmd/envman
- **Stack**: Python FastAPI backend + React/Vite/Tailwind frontend
- **Purpose**: Developer environment setup tool - Docker container orchestration

## Completed Work

### Phase 1: Multi-Service Support (Done)
- `backend/app/storage/db.py` - SQLite persistence (environments, containers tables)
- `backend/app/models/environment.py` - ServiceSpec model, legacy format validator
- `backend/app/models/plan.py` - Added network_name field
- `backend/app/engine/state.py` - Persistence hooks for containers/environments
- `backend/app/engine/executor.py` - Network creation, volume/env support
- `backend/app/engine/planner.py` - Async plan_environment, arbitrary services
- `backend/app/engine/coordinator.py` - Wired persistence, returns env_id
- `backend/app/registry/schema.py` - ServiceDefinition model (simplified)

### Phase 2: Service Expansion (Done)
- 15 services registered: node, python, postgres, mysql, mongo, sqlite, couchdb, redis, rabbitmq, kafka, nats, elasticsearch, meilisearch, typesense, minio
- 10 health check types: pg_isready, redis_ping, node_version, python_version, tcp_port, mongo_ping, http_get, http_get_with_api_key, kafka_api_version, sqlite_version
- `backend/app/registry/services.py` - All service definitions
- `backend/app/engine/verifier.py` - Registry-driven health check dispatch

### QA Fixes Applied (5 issues fixed)
1. **CRITICAL**: Python health_check_type `node_version` → `python_version` (added `_python_version()` function)
2. **CRITICAL**: Typesense `default_env` now has `TYPESENSE_API_KEY: xyz`
3. **CRITICAL**: `_tcp_port_check` wrapped in `asyncio.to_thread` (was blocking event loop)
4. **HIGH**: `get_service_by_image()` changed from substring to prefix matching
5. **HIGH**: `verify_environment()` now has Docker discovery fallback for server restarts

## Current State
- **Branch**: main (up to date with origin)
- **Last commit**: `f693544` - "fix: 5 QA issues..."
- **Services**: 15 registered
- **Health checks**: 10 types in dispatch map
- **Backend**: Loads correctly, all imports work
- **Tests**: No test files exist (manual verification only)

## Known Limitations (Not Fixed - Deferred)
- Frontend `totalExpected=4` hardcoded (should use backend's total_steps)
- Frontend only shows 2/15 services (Node, Postgres only)
- No cleanup/teardown mechanism for failed setups
- Dead code: `ServiceSpec.validate_name()`, empty stub files
- No test coverage

## Key Files
```
backend/
├── app/
│   ├── main.py                    # FastAPI entry point
│   ├── api/routes.py              # POST /setup, GET /health, GET /registry/services
│   ├── api/ws.py                  # WebSocket handler
│   ├── models/environment.py      # ServiceSpec, EnvironmentConfig
│   ├── models/plan.py             # Plan model
│   ├── models/step.py             # Step model
│   ├── engine/planner.py          # Creates execution plan
│   ├── engine/executor.py         # Docker command execution
│   ├── engine/coordinator.py      # Orchestrates setup flow
│   ├── engine/verifier.py         # Health checks (10 types)
│   ├── engine/state.py            # In-memory container registry
│   ├── registry/services.py       # 15 service definitions
│   ├── registry/schema.py         # ServiceDefinition model
│   ├── storage/db.py              # SQLite persistence
│   └── events/bus.py              # WebSocket event pub/sub
frontend/
├── src/App.jsx                    # Main React component
└── src/components/                # UI components
```

## Tech Details
- **Python**: 3.14 (via pyenv)
- **Node**: Available
- **Docker**: Windows container mode
- **Database**: SQLite (envman.db in app/storage/)
- **API**: FastAPI on port 8000
- **Frontend**: Vite dev server on port 5173
