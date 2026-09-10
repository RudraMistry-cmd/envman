# PR summaries — run envman-executor-audit-20260910-1555

## Patch 1 — backend/app/engine/executor.py
- Commit message: `fix(executor): validate names/env/volumes, redact secrets in logs, cap arg lengths`
- PR fragment: "Hardens the Docker executor per OWASP command-injection guidance (parameterization + allowlist regex) and Python subprocess docs. Adds validate_name/validate_env/normalize_volume/redact_cmd helpers; build_docker_run_cmd enforces them; run_command logs redacted argv. No shell=True introduced. Fixes R2-R5,R7. Tests: tests/test_executor_security.py (8 tests, mock shim, no daemon)."

## Patch 2 — backend/app/engine/verifier.py
- Commit message: `fix(verifier): bound pg probe timeouts so readiness checks fail fast`
- PR fragment: "Bounds the two Postgres probes (pg_isready 15 s, psql query 30 s) so the 5-retry loop fails in ~2-4 min worst case instead of ~25 min. No behavior change on the happy path. Fixes R1. Tests: test_verifier_pg_probes_are_timebounded (source-guard) + existing backend suite."
