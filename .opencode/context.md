# Project Context

## Environment
- Language: Python 3.14.5 + Node/React 18 (Vite 5, Tailwind)
- Backend: FastAPI + uvicorn + pydantic v2, pytest 9.1.1 (211 tests green 2026-09-06)
- Frontend: Vite dev on :5173, backend on :8000, CORS allows localhost:5173/:3000 + tauri
- Package Manager: pip (backend/requirements.txt) + npm (frontend/package-lock.json)
- Docker: 14 real services, all verified booting with real health checks

## Project Type
- [x] Application (local dev-environment orchestrator: plan → execute → verify)
- Backend API (FastAPI) + React dashboard + WebSocket progress bus

## Infrastructure
- Container: Docker CLI via list-based subprocess (never shell=True)
- CI/CD: none detected
- Cloud: none (local-only)

## Structure
- Source: backend/app (api/routes.py, api/ws.py, engine/planner|executor|verifier|coordinator|state.py, registry/schema|services|templates.py, storage/db.py SQLite, events/bus.py, models/environment|plan|step.py)
- Tests: backend/tests (engine, models, registry, storage) — `cd backend; python -m pytest tests/ -q`
- Frontend: frontend/src (App.jsx, components/configure|dashboard|progress|results|layout|shared, hooks/useWebSocket.js) — `npm run build` / `npm run dev`
- Entry: backend/app/main.py (FastAPI app); frontend/frontend/src/main.jsx

## Conventions (OBSERVED — follow these)
- Backend: snake_case, absolute imports (from app.xxx), list-based subprocess, module docstring WHY/WHAT/HOW, guarded idempotent SQLite migrations (ALTER TABLE ADD COLUMN only if missing — see db.py init_db)
- Verifier truthfulness: NEVER present registry default_port as verified; host_port only from stored value or live `docker inspect` HostPort; build_connection_info reports honestly (see verifier.py + db.py _inspect_host_port docstrings)
- Coordinator: run_setup plans → executes → verifies → emits WS events; on step failure tears down via delete_environment
- Frontend: dark glass-card UI, API const 'http://localhost:8000', copy-to-clipboard with fallback, results banner fails if ANY service not ready (see ResultsScreen.jsx `failed` gating)
- Tests: pytest tiered (pure logic fast + real-Docker); suite must stay 211+ green after every section

## Load-bearing (DO NOT REGRESS)
- executor.py safety pattern (list-based, no shell=True), port-conflict fail-clearly, command-after-image threading
- verifier.py get_actual_host_port + build_connection_info truthfulness
- ResultsScreen banner aggregation (failed = hasError || !allReady)
- 14-service registry boot fixes (postgres PASSWORD, mysql ALLOW_EMPTY, apache/kafka, ES single-node, minio creds+command, couchdb creds, typesense --data-dir + tcp checks, node/python tail keep-alive)
- templates.py mern + python-web (registry-pinned {id,version} only)
- db.py containers host_port/connection_string migration pattern

## Current State (2026-09-06)
- Uncommitted work: backend/app/api/routes.py has container-logs endpoint (fetch-on-demand, env-membership validated) NOT yet committed/tested/wired to UI
- Empty (0 bytes): events/schemas.py, core/config.py, core/platform.py, engine/compatibility.py
- Missing: lifecycle stop/start/restart, per-service control, export/import, log UI, registry richness fields, packaging (no pyproject.toml, no cli.py), smart ports, snapshots, AI gen, monitoring
- Phase 4 Collaboration explicitly OUT OF SCOPE
