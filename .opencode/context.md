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

## Current Status (2026-09-10 ~16:05)
- Mission todos: ~70/72. Remaining [ ]: S6.5.3 (clean-checkout E2E), S6.6.3 (optional AI/monitoring) + parent lines (gate reports 65/72). S6.6.1/6.2 marked via parallel pipeline. Zero sync issues.
- My spawned agents (8) all no-op/empty: task_27e7c6e0, task_7ff79691, task_7c8a0723, task_c4136c30 (cancelled), task_08553125, task_782d9110, task_f3a7f127. Marks came from parallel session (task_9ece6f0b, task_3b020d60, task_0cb8f09e).
- User ordered STOP; gate keeps firing stale 65/72. Do NOT spawn until user says resume.
- Harvest DONE: output/envman_internet_harvest.zip (77 files/1.77MB, 35 raw, 36 evidence) + master_report.md. All tracks: base, executor audit, verifier, fs, reconciler, competitor UX, secrets/CVE, CI.
- Executor audit DONE (run envman-executor-audit-20260910-1555): security_audit/, recommended_patches.diff (apply --check PASS, LF-only — never edit with edit-tool without CRLF normalize), tests/test_executor_security.py (8/8 green on patched tree), tests/mock_docker_shim.py, evidence/index.csv (19), raw/ x19, audit_report.md, ZIP output/envman_executor_audit_20260910.zip (29 entries, ok). Findings: R1 verifier 300s default (HIGH), R2 secrets in argv+logs (HIGH), R3-R5 validation gaps (MED).
- Repo hygiene: backend/ clean; .opencode/docs/ restored 2x after parallel session deletions (git checkout -- .opencode/docs/). Untracked harvest/audit outputs only.

## Pending Tasks
- T6.5.3 + T6.6.3 verification marks (await user resume; Reviewer-only).
- Final full-system Reviewer pass, all [x], conclude (blocked on above).

## Active sessions/agents
- Mine (all DONE/empty or cancelled — do not resume; sessions may be stale): task_27e7c6e0, task_7ff79691, task_7c8a0723, task_c4136c30, task_08553125 (ses_f755a86c7ffe8k7ESp75soGdIv), task_782d9110 (ses_f755301bbffetOuwY0JCMxElW0), task_f3a7f127 (ses_f7536dd94ffejOoClSbgpuxdBp).
- Parallel session (working): task_9ece6f0b, task_3b020d60, task_0cb8f09e. WARNING stands: it deletes .opencode/docs/*.md — restore via git checkout, never store sole-copy evidence there (raw/ + ZIPs hold it).
- Temp scratch: $TEMP/opencode/{audit,diffwork} (patched executor/verifier copies).
