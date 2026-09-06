# Mission: Host-reachable environments - expose ports + connection strings

## M1: Host-reachable environments | status: completed
### T1.1: Frontend ConfigureScreen port wiring | agent:Worker
- [x] S1.1.1: Update handleStart to include port from registryEntry.default_port when present, omit for node/python | size:S
- [x] S1.1.2: Verify payload shape matches ServiceSpec port:int and registry fetch includes default_port | size:S
### T1.2: Backend port-conflict clear failure | agent:Worker
- [x] S1.2.1: Add is_host_port_in_use helper (socket bind check) + unit tests | size:S
- [x] S1.2.2: Pre-check in executor _start_container before docker run, fail step with specific error naming conflicting port | size:M
- [x] S1.2.3: Ensure coordinator propagates step_failed with port conflict message | size:S
### T1.3: Backend verifier host_port + connection_string | agent:Worker
- [x] S1.3.1: Add build_connection_info helper mapping service id -> host_port + connection string | size:M
- [x] S1.3.2: Include host_port, connection_string, connection_type in _verify_service return and verify_environment results | size:S
- [x] S1.3.3: Resolve actual host port via docker inspect HostPort fallback + registry default_port | size:S
### T1.4: Frontend ServiceCard display + copy | agent:Worker
- [x] S1.4.1: Display host_port and connection_string in ServiceCard with copy-to-clipboard button + fallback when absent | size:S
- [x] S1.4.2: Verify ResultsScreen passes through new fields | size:S
### T1.5: Dashboard connection info | agent:Worker | depends:T1.3
- [x] S1.5.1: Enrich GET /environments response with host_port/connection_string per container | size:M
- [x] S1.5.2: Update EnvironmentsDashboard.jsx to show same connection info + copy button | size:S
### T1.6: Full system verification | agent:Reviewer | depends:T1.1,T1.2,T1.3,T1.4,T1.5
- [x] S1.6.1: Run pytest Tier1, verify no regressions | size:S
- [x] S1.6.2: E2E 3+ services host reachability from host shell on shown host:port | size:M
## M2: Service boot fixes (mysql/kafka/ES/minio + command support) | status: completed
(delivered direct - Planner/Worker pool unavailable; evidence: pytest 202 + live docker per-service table in .opencode/docs/boot-fixes.md)
### T2.1: Registry default_env fixes
- [x] S2.1.0: postgres POSTGRES_PASSWORD=postgres + verifier PGPASSWORD (fresh init REFUSES without it - proven live) | size:S
- [x] S2.1.1: mysql MYSQL_ALLOW_EMPTY_PASSWORD=yes | size:S
- [x] S2.1.2: kafka SWITCHED to apache/kafka (zero-env KRaft boot, proven live) instead of cp-kafka env vars; frontend 3.8.0; test refs updated | size:M
- [x] S2.1.3: elasticsearch discovery.type=single-node + xpack.security.enabled=false (green, host-reachable) | size:S
- [x] S2.1.4: minio explicit root creds | size:S
- [x] S2.1.5: couchdb COUCHDB_USER/PASSWORD=admin (3.x refuses admin-party - proven live) | size:S
- [x] S2.1.6: typesense --data-dir /tmp command + tcp check (exits without data dir; no curl in image - proven live) | size:S
### T2.2: Container command support
- [x] S2.2.1: ServiceSpec.command Optional[List[str]] | size:S
- [x] S2.2.2: planner threads registry default_command + service.command | size:S
- [x] S2.2.3: executor appends command AFTER image + default_command field (minio, typesense, node, python) | size:M
- [x] S2.2.4: Tier-1 command threading tests | size:S
### T2.3: Health-check mechanics + audit
- [x] S2.3.1: kafka .sh binary path for apache/kafka (proven live) | size:S
- [x] S2.3.2: nats/typesense -> tcp_port (no curl/shell in images) + host-side socket probe + http error key + dead api-key branch removed | size:M
- [x] S2.3.3: 14-service audit - empirical per-service table, docs in boot-fixes.md | size:M
### T2.4: Verification
- [x] S2.4.1: pytest 202/202 green | size:S
- [x] S2.4.2: 14-service fresh-boot table (12 bootable running+healthy, node/python then exiting - fixed in M3) | size:L

## M3: Runtime keep-alive + persistence migration | status: completed
### T3.1: node/python keep-alive
- [x] S3.1.1: registry default_command tail -f /dev/null for node + python | size:S
- [x] S3.1.2: real /setup E2E both (running 10s+, node v20.20.2 / python 3.12.14) + DELETE cleanup | size:S
### T3.2: containers-table migration
- [x] S3.2.1: ALTER TABLE ADD COLUMN migration (saves were failing, deletes orphaned) | size:S
- [x] S3.2.2: full-loop proof (persist -> dashboard -> DELETE removes container) | size:S

## M6: Mega mission - remaining spec work | status: in_progress
(collab Phase 4 EXCLUDED. Commit+push per section. Suite must stay green.)
### T6.1: Section 1 log viewing | agent:Worker | status: in_progress
- [x] S6.1.1: GET container logs endpoint with env-membership validation | size:M
- [x] S6.1.2: View-logs UI on ServiceCard + dashboard with refresh, graceful empty | size:M
- [ ] S6.1.3: Tier-1 tests + pytest/build green + live-vs-terminal evidence | size:S
### T6.2: Section 2 lifecycle control | agent:Worker | depends:T6.1 | status: pending
- [ ] S6.2.1: POST stop/start env endpoints (docker stop/start, re-verify on start) + status field running/stopped | size:M
- [ ] S6.2.2: Per-service stop/start if low-cost + dashboard Stop/Start actions reflecting real state | size:M
- [ ] S6.2.3: Tier-1 tests + pytest green + docker ps stopped-not-removed then running evidence | size:S
### T6.3: Section 3 config export/import | agent:Worker | depends:T6.2 | status: pending
- [ ] S6.3.1: POST export env JSON + POST import via existing /setup flow | size:M
- [ ] S6.3.2: Dashboard Export button + configure-screen Import (paste/upload, pre-fill like template) | size:M
- [ ] S6.3.3: Export-delete-reimport round-trip evidence, same services/ports/versions | size:S
### T6.4: Section 4 registry richness ADDITIVE ONLY | agent:Worker | depends:T6.3 | status: pending
- [ ] S6.4.1: Add optional available_versions, resource_requirements, platform_support to ServiceDefinition, populate all 14 services | size:M
- [ ] S6.4.2: Existing tests pass UNMODIFIED + GET /registry/services shows new fields | size:S
### T6.5: Section 5 packaging | agent:Worker | depends:T6.4 | status: pending
- [ ] S6.5.1: npm build + StaticFiles mount at / after API/WS routers + client-routing check | size:M
- [ ] S6.5.2: pyproject.toml entry point (envman = app.cli:main) + cli.py (uvicorn.run, browser open, free-port pick) + CORS both modes | size:M
- [ ] S6.5.3: Clean-checkout evidence: pip install . + envman start opens working tab, full setup-verify E2E, no npm dev | size:L
### T6.6: Section 6 lower-priority OPTIONAL (runway-dependent, in order) | status: pending
- [ ] S6.6.1: Smart port auto-reassignment (next free port + report) | size:M
- [ ] S6.6.2: Snapshots via export/import reuse | size:M
- [ ] S6.6.3: AI config gen + resource monitoring (only with real time left) | size:L

## M5: Results trust bugs (psql + banner) | status: completed
### T5.1: Postgres query_execution failure | agent:Worker
- [x] S5.1.1: reproduced exact commands live - both pass on current code; screenshot root cause was mixed-version backend (registry WITH password + verifier WITHOUT PGPASSWORD), no socket/TCP discrepancy; NO code change needed | size:S
- [x] S5.1.2: python-web template flow proof - query_execution true, 1 row, truthful connection string | size:S
### T5.2: False success banner | agent:Worker
- [x] S5.2.1: ResultsScreen never used allReady - banner Success whenever setup had no error; now failed=hasError||(verification&&!allReady) gates hero+title | size:S
- [x] S5.2.2: forced-failure proof (stopped redis -> not_running) - banner expression evaluates FAILURE on real failed payload, READY on all-ready, FAILURE on error | size:S

## M4: One-click templates (mern, python-web only) | status: completed
(scope: registry-pinned {id,version} prefill only; NO startup ordering; NO new runtimes)
### T4.1: Backend templates registry + endpoint | agent:Worker
- [x] S4.1.1: templates.py with mern (node 20, mongo 7, redis 7) + python-web (python 3.12, postgres 16, redis 7) | size:S
- [x] S4.1.2: GET /templates endpoint | size:S
### T4.2: Frontend template picker | agent:Worker
- [x] S4.2.1: template cards pre-filling config state, manual picker untouched | size:M
### T4.3: Verification | agent:Reviewer | depends:T4.1,T4.2
- [x] S4.3.1: pytest green + frontend build green | size:S
- [x] S4.3.2: template payload E2E (same services/ports as manual picks, docker ps) | size:M
