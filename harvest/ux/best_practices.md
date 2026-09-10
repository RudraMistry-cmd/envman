# UX & Onboarding Best Practices (cited)

Sources & quotes (<=25 words each):
- VS Code Dev Containers: "use a container as full-featured dev environment" — https://code.visualstudio.com/docs/devcontainers/containers
- Docker Desktop: "one-click-install application ... build share run" — https://docs.docker.com/desktop/
- DDEV: "launching local web development environments in minutes" — https://ddev.readthedocs.io/en/stable/
- Codespaces: "secure configurable dedicated development environment" + "prebuilds speed creation" — https://docs.github.com/en/codespaces
- OrbStack: "Starts in 2 seconds" — https://docs.orbstack.dev/

## 1. Time-to-first-success (TTFS) targets
- Best-in-class cited: OrbStack 2s start; Supabase case 17min vs 45min provision (https://orbstack.dev/). DDEV "minutes". Codespaces prebuilds for large repos.
- EnvMan goal: <5 min clone→green on sample project; <30s re-verify. Instrument TTFS funnel.

## 2. Funnel
Discover (template gallery) → Install backend check (Docker/OrbStack/Colima/Podman auto-detect) → Import (compose + devcontainer.json) → First health gate (pg_isready green) → Iterate (logs + exec terminal) → Share (export compose + env lockfile).

## 3. Copy snippets (reuse verbatim style)
- Empty state: "No healthy services yet. We'll wait until your database accepts connections — not just until the container runs."
- Health row: "db · healthy (pg_isready ok, 3/5 retries) · 12s" not just "Up".
- Error: "Container paused — unpause before exec. [Unpause & retry]" (per docker exec paused error).
- License nudge: "Docker Desktop needs a paid seat here (>250 emp / >$10M). Continue with CE/OrbStack? [Switch backend]"

## 4. Patterns to copy
- Dev Containers `devcontainer.json` + Features (one-click toolchain) — adopt as EnvMan template format for interop.
- `docker compose up --wait` + inline log tail (like Compose output aggregation).
- DDEV's per-OS requirement tables (macOS/WSL2/Win/Linux) — copy for EnvMan prereq checker.
- Codespaces machine-type picker + prebuilds — offer "small/large" resource profiles.

## 5. Metrics to track
TTFS, % first-verify green, exec-error rate, bind-mount failure rate (Win), emulation fallback rate (ARM), DAU/WAU per env.
