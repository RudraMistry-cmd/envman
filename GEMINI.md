# EnvMan — Project Rules for Antigravity Agents

## Non-negotiable rules for every task in this project

1. **Never touch or regress what's already working without explicit
   instruction to change it.** Load-bearing, already-verified: the 14
   registered services' boot fixes (registry/services.py default_env and
   command fields), the port-exposure/connection-string truthfulness
   logic (verifier.py's get_actual_host_port — it must NEVER return a
   registry default as if it were a verified real port binding), the
   results-banner aggregation fix (frontend ResultsScreen.jsx — the
   overall "ready" state must require ALL services' ALL checks to pass,
   never just "setup didn't error"), and the container-name convention
   (stored container names are already the full `envman_<service>` form —
   never re-prefix them).

2. **The backend pytest suite (backend/tests/) must stay green.** Run it
   before considering any task done. It currently passes at 227 tests;
   note the real count you see and don't let it silently drop.

3. **Every claim of "done" needs real evidence** — actual command output,
   actual `docker ps`, an actual passing test run, an actual screenshot or
   browser verification. Not a description of what the code should do.
   Use your browser subagent to actually verify frontend changes render
   correctly, don't just confirm the code compiles.

4. **If TECHNICAL_SPEC.md contradicts what already exists in this repo, or
   is ambiguous about an implementation detail, stop and ask the user
   directly.** Don't guess and don't silently pick the easier
   interpretation.

5. **Cite the actual TECHNICAL_SPEC.md section you're implementing.**
   Don't invent structure the spec doesn't describe, and don't assume
   what a section says — read it.

6. **Known deliberate simplifications from this repo's history — don't
   "fix" these back to the full spec without being asked:**
   - ServiceDefinition (registry/schema.py) is simplified vs. the spec's
     richer version — no volume_mounts field exists yet, and that's fine.
   - Only node and python exist as runtimes. No java/go/rust/ruby/php/
     dotnet. Templates or features assuming those runtimes exist are out
     of scope unless a task explicitly adds those runtimes first.
   - Collaboration (spec Phase 4) is explicitly excluded — no multi-user
     features. Not an oversight, a deliberate call.

## Where things stand (verify against the actual repo before starting,
this may drift)

Done: Phase 1-2 core loop, all 14 services verified booting for real, host
port exposure + truthful connection strings, results banner correctly
gates on all checks, 2 templates (mern, python-web), log viewing
(fetch-on-demand), environment stop/start, config export/import. 227
backend tests passing.

Not done: registry schema richness (available_versions,
resource_requirements, platform_support fields), packaging (no
pyproject.toml/CLI entry point — still requires cloning + two dev
servers), smart port auto-reassignment (only fail-clearly-on-conflict
exists), environment snapshots, AI config generation, resource
monitoring.

Known minor gap, fix if you touch this code: POST /environments/{id}/stop
marks a container's DB status as "stopped" without checking whether
`docker stop` actually succeeded (no returncode check) — same class of
silent-failure bug already fixed elsewhere in this codebase.