# Project Context

## Environment
- Python 3.14.5 + React 18/Vite 5/Tailwind; FastAPI backend (:8000), Vite dev (:5173)
- Backend tests: `cd backend; python -m pytest tests/ -q` (227 green as of 2026-09-06)
- Frontend build: `npm run build` in frontend/ (green)
- Docker: 14 real services verified booting with real health checks
- GitHub: RudraMistry-cmd/envman, branch main (push per section — ground rule)

## Project Type
- Local dev-environment orchestrator (plan → execute → verify), FastAPI + React + WS bus

## Structure
- backend/app: api/routes.py, api/ws.py, engine/planner|executor|verifier|coordinator|state.py, registry/schema|services|templates.py, storage/db.py (SQLite), events/bus.py, models/
- backend/tests: engine|models|registry|storage|api (test_logs, test_lifecycle, test_export_import)
- frontend/src: App.jsx, components/configure|dashboard|progress|results|layout|shared (LogPanel.jsx), hooks/
- .opencode/todo.md: hierarchical M1-M6 plan; Reviewer alone marks [x]

## Conventions (follow)
- List-based subprocess only, never shell=True; guarded idempotent SQLite migrations (PRAGMA check + ADD COLUMN)
- Verifier truthfulness: host_port only from stored value or live docker inspect, never registry default
- Results banner fails if ANY service not ready; 211→227 suite must stay green after every section
- Frontend plain JS in .jsx (no TS annotations, no Python literals); string concat preferred (a past incident stripped `${}` template literals repo-wide)

## Load-bearing (do NOT regress)
- executor safety/port-conflict/command-after-image; verifier.py truthfulness; ResultsScreen banner gating; 14-service boot fixes; mern/python-web templates; db.py migration pattern

## Current Status (2026-09-06 ~17:00)
- M1-M5: complete [x]. M6 Section 1 logs [x] (commit f53e101). Section 2 lifecycle [x] (b051527 + 879c159).
- Section 3 export/import: IMPLEMENTED + PUSHED (6415356 test commit, e964a47 feat commit). Evidence: old env→404 no-config; fresh redis export→delete→import→identical redis:7:6379 running. Reviewer task_4e729319 verifying (was RUNNING, ~13+ min); S6.3.1-3 still [ ].
- Section 4 registry richness: Worker task_79a82556 RUNNING (strict ownership: schema.py + services.py + NEW test_registry_richness.py only). Do NOT commit S4 until S3 marked.
- Suite 227/227 green; build green. Live backend server: restarted multiple times (kill stale double --reload servers first; run WITHOUT --reload for deterministic evidence). Test envs have churned (deterministic envman_redis names collide across envs).

## Pending Tasks
- T6.3 S6.3.1-3: await Reviewer mark → commit status/todo churn → push
- T6.4 S6.4.1-2: collect Worker result → verify gates → live serialization evidence → commit+push → Reviewer
- T6.5 packaging (pyproject + cli.py + StaticFiles) → T6.6 optional (smart ports, snapshots, AI/monitoring)
- Final: full-system Reviewer pass, all [x], conclude

## Active sessions/agents (may still be writing files — verify with git status/diff before trusting working tree)
- task_4e729319 Reviewer (S3 verify), task_79a82556 Worker (S4), ses_f89893120ffeuDSlJKV0gWFXL4 (S4 resume)
- Older completed: task_9c38b278/60742a93/ccd1c6e6/7885cb8e/300994b6 (S1 workers), task_b1ceeed3/87a87efe/af61d648/9e978283/b3f4b4f0 (S1 reviewers), task_bc3094a6/c249e26c/b7be559d (S2/S3 workers), task_72506199/6d81bc40/6d712839/2184f619/4e729319 (reviewers)
- WARNING: a competing/runaway session has repeatedly reverted working-tree files (routes async fix, test files, template literals) and drops junk (frontend/con, *.temp, pytest_output*.txt, backend/.opencode/). Counter: verify via git status/diff, repair, run gates, commit IMMEDIATELY to anchor known-good state in git.
- Backend server mgmt: Get-NetTCPConnection -LocalPort 8000 → kill orphans; start `venv\Scripts\python.exe -m uvicorn app.main:app --port 8000` via run_background (no --reload).
