# EnvMan Executor Security Audit — Report (run envman-executor-audit-20260910-1555)
Scope: backend/app/engine/executor.py (360 lines) + verifier.py probes; 19 primary sources in evidence/index.csv, raw HTML in raw/.

## Top 5 risks
1. **Unbounded verifier waits (HIGH, R1)** — probes inherit the 300 s default; 5 retries ≈ 25 min hang. Fix: timeouts 15 s/30 s (patch 2).
2. **Secret leakage (HIGH, R2)** — full argv incl. `-e KEY=secret` hits logs (`executor.py:112`) and `ps`. Fix: `redact_cmd` + env-over-argv hygiene.
3. **Unvalidated names/images (MED, R3)** — safe today only via list-argv discipline; one refactor from RCE. Fix: `validate_name` allowlist `^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,63}$`.
4. **Raw env/volume passthrough (MED, R4/R5)** — `KEY=value` joins, no WSL normalization (`C:\` breaks). Fix: `validate_env`, `normalize_volume` (wslpath-aware).
5. **Daemon socket = root (MED, R6)** — any API caller can `docker run -v /:/host`. Fix process-side: read-only mounts, `--cap-drop`, preflight, Scout SBOM + pinned digests.

## Priority fixes (in recommended_patches.diff, `git apply --check`: PASS)
- P1 executor.py: helpers + enforcement + redacted logging. P2 verifier.py: bounded probe timeouts. No `shell=True` anywhere.

## Migration plan
1. `git checkout -b feature/executor-hardening && git apply recommended_patches.diff`
2. `pytest tests/test_executor_security.py -q` (8 tests, mock shim, no daemon) → expect 8 passed.
3. Full backend suite `cd backend; python -m pytest tests/ -q` (regression gate).
4. Follow-ups (not in diff): `--env-file` for secrets, `docker version` preflight, digest pinning + Scout policy.

## How to run tests locally
- `pip install -r backend/requirements-dev.txt` (if absent in your checkout, fallback: `pip install -r backend/requirements.txt` + `pip install pytest` — pydantic required for `app.models.step`)
- `pytest tests/test_executor_security.py -q`
- Apply flow: `git checkout -b feature/executor-hardening` → `git apply recommended_patches.diff` → `pytest -q`
- Mock-shim PATH trick (optional isolation): `PATH="<repo>/tests:$PATH" pytest tests/test_executor_security.py -q` — the shim shadows `docker` for the test process only.

## Notes
- Substitutions: README.md for the dated README name; engine/ paths for executor/verifier; prior harvest patch superseded (see security_audit/missing_files.txt).
- Blocked pages logged in security_audit/crawl_skip.log (OWASP community 404, SO 403, Reddit login wall); primary docs substituted.
- WSL simulation: tests stub `wslpath`/subprocess at module boundary (see test comments) — no shell, Windows-safe.
