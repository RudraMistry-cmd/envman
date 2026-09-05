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
