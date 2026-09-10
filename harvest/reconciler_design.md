# Reconciler Design: Desired State (DB) vs Docker State (daemon)
Sources & quotes:
- K8s controllers: "control loops that watch the state of your cluster, then make changes ... move current closer to desired" + "spec field represents desired state" — https://kubernetes.io/docs/concepts/architecture/controller/
- Compose lifecycle: `up` (re)creates on config/image change; `--force-recreate`, `--no-recreate`, `--remove-orphans`, `--renew-anon-volumes`, `--wait` — https://docs.docker.com/reference/cli/docker/compose/up/
- Exec/inspect truth: `docker exec` needs running container — https://docs.docker.com/reference/cli/docker/container/exec/; mounts tied to host — https://docs.docker.com/engine/storage/bind-mounts/
- Engine API version negotiation (client/daemon skew) — https://docs.docker.com/engine/api/

## Recommended pattern for EnvMan (lightweight, no K8s)
1. **Level-triggered polling reconciler** (K8s-style) over event-based: every N sec (default 10s, backoff to 60s when stable) compare DB rows vs `docker ps/inspect`. Events (WS/log streams) are best-effort hints only — polling is source of truth (handles daemon restarts, manual `docker rm`, reboot).
2. **Desired record**: `environments(id, spec_json, status)` + `containers(env_id, service, image, ports, mounts, desired_state=running|stopped)`.
3. **Observed**: `docker ps -a --format json` + `docker inspect` (Running, Health, HostPort, Mounts, ImageDigest).
4. **Diff → actions** (idempotent, ordered): create-missing → start-stopped → recreate-drifted (image/config digest change, like `up --force-recreate`) → remove-orphans (container not in DB, labeled `envman.env=<id>`) → re-verify (service_healthy). Never delete data volumes without explicit flag (mirror `--renew-anon-volumes` guard).
5. **Ownership**: label every container `envman.env`, `envman.service` (K8s note: "controllers only pay attention to resources linked to their controlling resource" via labels).
6. **Drift detection à la Terraform**: `plan` = diff desired vs observed (no changes); `apply` = execute actions; store `last_applied_digest` per service to avoid flapping.
7. **Version skew**: preflight `docker version` (Engine API negotiation); if daemon older, degrade (no `--wait`, poll manually).
8. **Safety**: dry-run output first; rate-limit restarts (max 3/5min); quarantine CrashLoop (mark `degraded`, stop retrying, surface logs incl. pre_start hook label check).
