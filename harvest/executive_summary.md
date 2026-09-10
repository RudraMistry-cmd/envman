# EnvMan Internet Harvest — Executive Summary (1 page)

**Thesis:** EnvMan (Docker-CLI-via-subprocess + registry health verifier) is viable *iff* it treats "running ≠ ready", Windows/WSL2 paths, Desktop licensing, daemon-socket privilege, and ARM emulation as P0.

**Must-do (from primary docs):**
1. Health-gate everything: `depends_on: condition: service_healthy` + `pg_isready` (interval 10s/retries 5/start 30s) and `compose up --wait`; poll `Health.Status`, not `Running`. — https://docs.docker.com/compose/how-tos/startup-order/
2. Harden executor: argv lists, no `shell=True`, `sh -c` wrapper, name regex `[a-zA-Z0-9_.-]+`, timeouts; handle paused-container error. — https://docs.docker.com/reference/cli/docker/container/exec/
3. Normalize bind mounts per-OS (`wslpath`, `--mount type=bind`, readonly default). — https://docs.docker.com/engine/storage/bind-mounts/
4. Offer non-Desktop backends (CE/WSL2, OrbStack, Colima, Podman, Rancher) — Desktop needs paid seats >250 emp/>$10M. — https://www.docker.com/pricing/faq/
5. Pin multi-arch images; Rosetta fallback on Mac. — https://github.com/abiosoft/colima; https://docs.orbstack.dev/

**Opportunity:** No local tool combines visual Compose/dashboard + registry-driven `pg_isready`-style verifier + cross-backend picker. DevPod/Codespaces prove devcontainer.json interop; OrbStack proves users pay for speed. Ship TTFS <5min, hook-log surfacing, Hub-mirror resilience.

**Top risks:** see `killers.md` (10). Evidence: `evidence/index.csv` (25 sources, raw in `raw/sha256.html`). Patches: `code_patches/`. Tests: `tests/mock_docker_shim.py` (pytest green without daemon).
