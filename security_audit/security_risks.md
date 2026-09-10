# EnvMan Executor Security Risks (ranked) — run envman-executor-audit-20260910-1555
Scope: backend/app/engine/executor.py (360 lines, read 2026-09-10), backend/app/engine/verifier.py (680 lines, lines 1-330 read), TECHNICAL_SPEC.md Part 1 (healthcheck/volume/port rules), README.md.
Baseline credit: executor already uses list-based argv, no shell=True (executor.py:19-23,44-52). Findings below are residual gaps.

## HIGH

### R1. Verifier probes inherit 300 s timeout — 25-minute worst-case hang (correctness/DoS)
- Exploit scenario: a wedged DB makes each `docker exec` block 300 s; 5 retries = ~25 min of hung verify with no output.
- Affected: backend/app/engine/verifier.py:89 (`pg_isready`), :117 (`psql`), :144/:158/:160/:173/:215/:231/:252 (all `run_command([...])` without timeout) via backend/app/engine/executor.py:95 (`timeout: int = 300`).
- Support: https://docs.python.org/3/library/subprocess.html — excerpt: "A timeout may be specified in seconds" (TimeoutExpired contract).
- Support: https://docs.docker.com/compose/how-tos/startup-order/ — excerpt: "Compose does not wait until container is ready only until running" (why bounded polling matters, not unbounded waits).

### R2. Secrets leak via argv + command logging
- Exploit scenario: `PGPASSWORD`/registry passwords appear in `docker exec -e` argv (visible in `ps`) and executor logs the full command including `-e KEY=secret`, persisting secrets to log files.
- Affected: backend/app/engine/executor.py:112 (`logger.info("running: %s", " ".join(cmd))`); backend/app/engine/verifier.py:117 (`"docker","exec","-e","PGPASSWORD=postgres"`); backend/app/engine/executor.py:199-204 (`-e f"{key}={value}"`).
- Support: https://redis.io/docs/latest/develop/tools/cli/ — excerpt: "provide the password automatically via the REDISCLI_AUTH environment variable" (env-file/env pattern, not argv).
- Support: https://hub.docker.com/_/postgres — excerpt: "POSTGRES_PASSWORD ... must not be empty or undefined" (password is mandatory, so its handling must be safe).

## MEDIUM

### R3. Container/image/name inputs unvalidated (allowlist missing)
- Exploit scenario: a crafted service name/image (e.g. `x; rm -rf /` or `--privileged` as image) is inert today only because argv is list-based; one future `shell=True` or string-join refactor turns it into host RCE; invalid names already cause confusing daemon errors.
- Affected: backend/app/engine/executor.py:190 (`--name`, no regex), :206 (`cmd.append(image)`), :223-228 (`name` from step.params/step.id into `docker rm -f`).
- Support: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html — excerpt: "validated against a list of allowed commands" and "Allowlist Regular Expression" e.g. `^[a-z0-9]{3,10}$` with length limits.
- Support: https://docs.docker.com/reference/cli/docker/container/exec/ — excerpt: "command must be an executable" (explicit argv atoms, never strings).

### R4. Env-var keys/values unvalidated (`KEY=value` join)
- Exploit scenario: a key containing `=`/spaces/newlines corrupts `-e` semantics or smuggles extra variables into containers; non-dict `env` strings pass through raw.
- Affected: backend/app/engine/executor.py:199-204.
- Support: https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html — excerpt: "use structured mechanisms that automatically enforce separation between data and command".
- Support: https://docs.python.org/3/library/subprocess.html — excerpt: "If env is not None, it must be mapping" (validate mapping shape, merge with os.environ, never wipe PATH).

### R5. Volume string passed raw — no WSL/Windows normalization, no existence check
- Exploit scenario: `C:\proj:/app` or a non-existent bind source fails with "invalid mount config" on WSL2/macOS, or `-v` silently auto-creates a host directory (data-loss confusion).
- Affected: backend/app/engine/executor.py:196-197 (`cmd.extend(["-v", volume])`).
- Support: https://docs.docker.com/engine/storage/bind-mounts/ — excerpt: "Containers with bind mounts strongly tied to host".
- Support: https://docs.docker.com/desktop/features/wsl/ — excerpt: "improvements to file system sharing" (per-distro integration; normalize via wslpath).

### R6. Docker daemon socket = host root; any API caller reaches it
- Exploit scenario: any authenticated API/WS caller that can start a container gets `docker run -v /:/host` host takeover; `docker-users` membership equals admin.
- Affected: backend/app/engine/executor.py (all `_run_sync` calls); backend/app/api/routes.py (setup endpoints).
- Support: https://docs.docker.com/engine/security/ — excerpt: "only trusted users should control your Docker daemon".
- Support: https://docs.docker.com/desktop/setup/install/windows-install/ — excerpt: docker-users group / admin-rights install modes.

## LOW

### R7. No argument-length caps (Windows CreateProcess/cmd.exe limits)
- Affected: executor.py:178-211 (unbounded env/command/volume growth).
- Support: https://docs.python.org/3/library/subprocess.html — excerpt: "Converting an argument sequence to a string on Windows" (platform length behavior differs; prefer `--env-file`).

### R8. Brittle substring error parsing (locale/version drift)
- Affected: executor.py:291-296 (`"port is already allocated" in stderr_lower` etc.).
- Support: https://docs.docker.com/reference/cli/docker/compose/up/ — excerpt: structured flags over string scraping (`--wait`, exit codes).

### R9. Bare `docker` binary, no preflight (`shutil.which` + `docker version`)
- Affected: executor.py:47,60-65 (FileNotFoundError message only).
- Support: https://docs.docker.com/engine/api/ — excerpt: "DOCKER_API_VERSION disables negotiation" (pin/check versions early).

### R10. Hardcoded probe credentials (registry drift breaks verifier)
- Exploit scenario: none (correctness) — registry changes user/password, verifier.py:89 (`-U postgres`) and :117-118 hardcode old values and report healthy services as failed.
- Support: https://docs.docker.com/compose/how-tos/startup-order/ — excerpt: `pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}` (thread registry values).

## INFO

### R11. Unpinned image tags (supply-chain)
- Support: https://docs.docker.com/scout/ — excerpt: "inventory of components, also known as SBOM" (scan + pin tag@digest).
