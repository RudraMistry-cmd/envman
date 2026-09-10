# Secrets Practices (practical; not legal advice)
Sources: Engine security (https://docs.docker.com/engine/security/ "only trusted users should control daemon"); bind mounts (https://docs.docker.com/engine/storage/bind-mounts/); Compose startup health (https://docs.docker.com/compose/how-tos/startup-order/); postgres Hub auth (https://hub.docker.com/_/postgres); redis-cli auth (https://redis.io/docs/latest/develop/tools/cli/); ES password/token/cert (https://www.elastic.co/docs/deploy-manage/deploy/self-managed/install-elasticsearch-docker-basic).

1. **Never bake secrets in images**: use runtime `-e`/`--env-file` (0600) or Compose `env_file:`; keep `.env` gitignored; EnvMan must redact in logs/UI.
2. **Prefer Docker secrets/volume mounts for files**: passwords/certs as mounted files (`/run/secrets/*`), not `-e` visible in `docker inspect`/shell history.
3. **Least privilege**: `docker exec` inherits env at create; pass per-probe `-e` minimally; `read-only` mounts; `--cap-drop ALL` + add-backs (Engine security capabilities).
4. **OS keychains**: dev convenience via `docker-credential-helpers` (Desktop credStore) — never plaintext `~/.docker/config.json`.
5. **Rotation**: support `reset-password`/`create-enrollment-token` flows (ES pattern); restart dependents (`depends_on restart:true`).
6. **Enterprise**: SSO-gated registries (`allowing private registry` Codespaces pattern https://docs.github.com/en/codespaces); audit who pulled what; Scout SBOM per build (https://docs.docker.com/scout/).
7. **Anti-patterns that kill**: `.env` committed; `POSTGRES_HOST_AUTH_METHOD=trust`; `REDISCLI_AUTH` in argv (use env); TLS verify off (`-k`) outside dev; daemon TCP without TLS.
