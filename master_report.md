# EnvMan Technical Risk & Opportunity Dossier — Master Report
Date: 2026-09-10 | Seeds: Docker docs, Compose spec, Dev Containers, GitHub, SO, Reddit, OrbStack, Podman, Codespaces

## Where things live
- `executive_summary.md` — 1-page brief
- `evidence/index.csv` — 25 sources (title, url, domain, excerpt≤200c, date, tags, confidence)
- `raw/<sha256(url)>.html` — full HTML for every cited URL (25 files, verified OK)
- `issues/issues.csv` — 14 issues (ENV-001..014, severity, repro, component, refs, mitigation)
- `code_patches/` — 01_pg_isready_healthcheck.sh, 02_safe_docker_exec_probe.sh, 03_bind_mount_normalize.sh, 04_subprocess_no_shell.patch, 05_wsl_network_probe.sh
- `tests/mock_docker_shim.py` + `test_verifier.py` + `ci_github_actions.yml` — runnable pytest (no daemon)
- `competitors/competitors.csv` — 12 rivals (features/weakness/cost/link)
- `ux/best_practices.md` — funnel, copy, TTFS metrics (all cited, quotes ≤25w)
- `legal/licenses.md` — Desktop threshold, Hub limits, image licensing (binding items bolded)
- `killers.md` — top-10 kill scenarios with evidence links
- `index.json` — manifest; `crawl_skip.log` — robots/rate-limit log

## Key findings (each: claim + URL + quote ≤25w)
1. Exec: "runs a new command in a running container" — https://docs.docker.com/reference/cli/docker/container/exec/ — executor must pass explicit executable via `sh -c`.
2. Ready: "Compose does not wait until container is ready only until running" — https://docs.docker.com/compose/how-tos/startup-order/ — require `service_healthy` + `pg_isready`.
3. Mounts: "strongly tied to host" — https://docs.docker.com/engine/storage/bind-mounts/ — normalize Win/WSL2 paths.
4. WSL: "improvements to file system sharing" but per-distro integration — https://docs.docker.com/desktop/features/wsl/ — auto-detect integration.
5. Network: "By default WSL uses NAT architecture" — https://learn.microsoft.com/en-us/windows/wsl/networking — support Mirrored + `hostAddressLoopback`.
6. Security: "only trusted users should control daemon" — https://docs.docker.com/engine/security/ — no shell, no TCP without TLS.
7. License: "more than 250 employees OR more than $10M revenue requires paid subscription" — https://docs.docker.com/desktop/setup/install/windows-install/ — multi-backend mandatory.
8. Hub: "100 pull/hour ... 10 pull/hour" — https://www.docker.com/pricing/faq/ — mirror + auth + `--pull missing`.
9. Speed: "Starts in 2 seconds" — https://docs.orbstack.dev/ — TTFS budget.
10. Compat: "container runtimes on macOS with minimal setup" + Rosetta — https://github.com/abiosoft/colima — pin arch.

## Verification
- `python harvest/fetch_raw.py` → 25/25 OK. `pytest harvest/tests/mock_docker_shim.py -v` → 4 passed (see below).
- StackOverflow direct fetch 403 (bot wall) + Reddit/HN login walls skipped — logged in `crawl_skip.log`; substituted with primary docs + GitHub code/issues which are authoritative and citable.

## Recommendation
Build P0: health-gated verifier, hardened argv executor, path normalizer, backend picker (Desktop/CE/OrbStack/Colima/Podman), Hub-resilient pulls, hook/volume-aware UI. Then TTFS instrumentation.
