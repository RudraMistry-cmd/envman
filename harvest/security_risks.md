# Executor Audit: Security Risks of Docker-via-Subprocess in Python
Date: 2026-09-10 | Scope: Windows (cmd.exe/PowerShell, native + WSL2), macOS, Linux

Every claim cites its URL. Quotes are <=25 words.

## R1. Shell-injection via `shell=True` + string concat — CRITICAL
- Source: https://docs.python.org/3/library/subprocess.html — Quote: "Providing a sequence of arguments is generally preferred, as it allows escaping"
- Source: https://docs.python.org/3/library/shlex.html — Quote: "executed by a shell: boom!" / "can open up command injection vulnerability"
- Exploit: `subprocess.run(f"docker exec {container} {cmd}", shell=True)` with `container="mydb; rm -rf /"` or `cmd="$(malicious)"` runs attacker command on HOST (not just container).
- Exact example:
  ```python
  # VULNERABLE
  subprocess.run("docker exec " + user_container + " " + user_cmd, shell=True)  # BAD
  # attacker: user_container = "c; powershell -c Invoke-Mimikatz #"
  ```
- Windows twist: `shell=True` invokes `%COMSPEC% cmd.exe` (see subprocess docs "Changed in 3.12: Windows shell search order ... cmd.exe"). Metachars differ (`& | && ^ %VAR%`), so Unix-tested escaping fails on Windows. PowerShell adds another layer (backtick escape, `;` statement sep).
- Fix: argv list + `shell=False` (see recommended_patches.diff P1).

## R2. `shlex.split`/`shlex.quote` are Unix-only — Windows bypass
- Source: https://docs.python.org/3/library/shlex.html — Quote: "only designed for Unix shells ... not guaranteed correct on Windows"
- Scenario: `shlex.quote(name)` then executed via cmd.exe/PowerShell — quotes do NOT protect (`'` is literal in cmd.exe; `"` handling differs). Leads to false sense of safety.
- Fix: NEVER rely on shlex for Windows; use list-based `subprocess.run([...], shell=False)` which bypasses shell parsing entirely (see subprocess docs "Converting an argument sequence to a string on Windows").

## R3. Chained/quoted `docker exec` misuse + arg-splitting
- Source: https://docs.docker.com/reference/cli/docker/container/exec/ — Quote: "command must be an executable ... chained or quoted command doesn't work"
- Failures observed: `["docker","exec",c,"echo a && echo b"]` fails (tries binary literally named `echo a && echo b`); correct is `["docker","exec",c,"sh","-c","echo a && echo b"]`.
- Long-command failure: Windows `CreateProcess` 32,767-char limit; `cmd.exe` 8,191-char limit — long `docker run -e ...` via string silently truncates/fails. List form + response-file/env-file (`--env-file`) avoids it.
- Fix: explicit executable + `sh -c` wrapper only inside container, never host shell (patch P2).

## R4. Environment / PATH / permission errors
- Sources:
  - https://docs.python.org/3/library/subprocess.html — Quote: "If env is not None, it must be mapping ... used instead of inheriting"
  - https://docs.docker.com/desktop/setup/install/windows-install/ — WSL2 backend, docker-users group, admin rights
  - https://docs.docker.com/engine/security/ — Quote: "only trusted users should control your Docker daemon"
- Scenarios:
  1. `FileNotFoundError: docker` — bare `docker` not on PATH (Windows Store shim, WSL interop, venv service). Passing `env={}` wipes PATH.
  2. `permission denied /var/run/docker.sock` (Linux) or `docker-users` group (Windows) — equivalent to admin (daemon socket = root; `docker run -v /:/host` host takeover).
  3. `DOCKER_HOST`/`DOCKER_API_VERSION` stale (see https://docs.docker.com/engine/api/ — version negotiation; env var disables negotiation) → client-newer-than-daemon 404s.
  4. Env inheritance leak: `docker exec` inherits env only at create time; `POSTGRES_PASSWORD` missing at exec → pg_isready auth fail (use `-e`/`--env-file`).
- Fixes: resolve `shutil.which("docker")`, merge `env={**os.environ, ...}`, timeout + `TimeoutExpired` kill, preflight `docker version` (patch P3/P4).

## R5. Windows-specific gotchas (cmd.exe vs PowerShell vs WSL)
- Sources:
  - https://docs.python.org/3/library/subprocess.html (Windows Popen Helpers, shell search order)
  - https://docs.docker.com/desktop/features/wsl/ — Quote: "WSL 2 provides improvements to file system sharing"
  - https://learn.microsoft.com/en-us/windows/wsl/networking — Quote: "By default WSL uses NAT architecture"
  - https://docs.docker.com/engine/storage/bind-mounts/ — Quote: "Containers with bind mounts strongly tied to host"
- Table:
  | Host | Pitfall | Example |
  |---|---|---|
  | cmd.exe (`shell=True`) | `& \| < > ^` metachars; `%VAR%` expansion; 8191-char cap | `docker run -e PASS=a&b` → splits at `&` |
  | PowerShell | `;` + backtick + `$()`; `Start-Process -ArgumentList` quoting | `'install','--user'` must be separate args |
  | WSL interop | `C:\proj` vs `/mnt/c/proj` vs `\\wsl$`; `wslpath` needed | bind `C:\proj:/app` → "invalid mount config" |
  | NAT vs Mirrored | localhost ≠ LAN in NAT; `.wslconfig networkingMode` drift | health probe passes locally, fails remotely |
- Fix: detect platform (`os.name`, `wslpath`), normalize via `realpath`/`wslpath -a`, prefer `--mount type=bind`, never `shell=True` (patch P5). StackOverflow/Reddit threads on these exact errors were unreachable (HTTP 403 bot-wall / login wall — see harvest/crawl_skip.log); primary docs above are authoritative substitutes.

## R6. docker-py (SDK) vs CLI tradeoffs
- Sources:
  - https://docker-py.readthedocs.io/en/stable/ — Quote: "lets you do anything the docker command does, but from within Python"
  - https://docs.docker.com/engine/api/ — Quote: "Docker Engine API is RESTful ... version negotiation"
- CLI (`subprocess ["docker",...]`): zero dep, matches user terminal, trivial `--wait`/`--mount` passthrough; CON: brittle parsing (must parse `docker ps/inspect` text), shell/PATH/escaping burden, version skew, 32k cmdline cap.
- SDK (`docker.from_env()`): typed `containers.run/list`, no shell, structured `attrs/logs`, TLS/`DOCKER_HOST` handling; CON: extra dep, API-version pinning (`DOCKER_API_VERSION` disables negotiation), lags CLI features, still socket-privileged (same R4 socket risk).
- Recommendation: keep CLI + hardened list-form for EnvMan parity with user shell; isolate ALL docker calls behind one `DockerRunner` interface so SDK swap is one-file change; add `docker version` + API-negotiation preflight.

## Exploit matrix (reproduce safely in VM only)
| # | Payload | Effect | Blocked by |
|---|---|---|---|
| E1 | container=`"x; calc.exe #"` via shell=True | host RCE | P1 argv list |
| E2 | image=`"alpine; docker run -v /:/h ..."` | host takeover | P1 + name regex |
| E3 | env `POSTGRES_PASSWORD='a\"; evil'` | arg breakout | P2 no shell |
| E4 | socket exposed `-H tcp://0.0.0.0:2375` no TLS | remote root | P4 TLS/SSH only |
| E5 | bind `~/.ssh:/root/.ssh:ro` malicious compose | key theft | P5 readonly audit + prompt |
