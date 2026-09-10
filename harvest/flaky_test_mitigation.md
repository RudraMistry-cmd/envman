# Flaky-Test Mitigation (compose-in-CI patterns)
Sources: compose `--wait/--wait-timeout` (https://docs.docker.com/reference/cli/docker/compose/up/); health gating (https://docs.docker.com/compose/how-tos/startup-order/); Hub limits (https://www.docker.com/pricing/faq/); Scout (https://docs.docker.com/scout/).

1. **Gate on healthy, not sleep**: `up -d --wait --wait-timeout 120` + poll `Health.Status`; fixed `sleep 30` is the #1 flake.
2. **Bounded retries with start_period**: mirror per-service timing (ES 90s, Kafka 60s, pg 30s); fail fast with last-stderr artifact.
3. **Auth in CI**: Hub login (100/hr vs 10/hr/IP); mirror to GHCR; `--pull missing`; retry `toomanyrequests` with backoff.
4. **Isolate**: `--remove-orphans`, unique project `-p ci-$GITHUB_RUN_ID`, `-V` only on purpose; `down` in `always()`.
5. **Quarantine + rerun**: retry failed integration once (`pytest --lf --maxfail=1`); tag `flaky` + auto-file issue with `compose logs --tail 200` + `docker inspect`.
6. **Timeouts everywhere**: job 25m, probe 5-15s, `curl --max-time 10`, `timeout(1)` wrappers; `after_script` log dump.
7. **Deterministic images**: pin `tag@digest`; Scout SBOM gate blocks CVE-flakes.
8. **No daemon unit tests**: mock shim (`harvest/tests/mock_docker_shim.py`) for PRs; real compose only on `integration` job.
