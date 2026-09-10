# What Can Kill EnvMan — Top 10 (each linked to evidence)

1. **DB-ready race ships as green** — Compose only waits until running, not ready. Fix with service_healthy + pg_isready. Sources: https://docs.docker.com/compose/how-tos/startup-order/ ("Compose does not wait until container is ready only until running").
2. **Windows/WSL2 bind-mount path hell** — C:\ vs /mnt/c vs daemon-VM paths break first run. Sources: https://docs.docker.com/engine/storage/bind-mounts/ ("strongly tied to host"); https://docs.docker.com/desktop/features/wsl/.
3. **Docker Desktop license audit** — enterprise >250 emp / >$10M must pay; EnvMan defaulting to Desktop = blocked deal. Sources: https://www.docker.com/pricing/faq/; https://docs.docker.com/desktop/setup/install/windows-install/.
4. **Daemon socket = root** — one malicious compose/env = host takeover; single CVE ends trust. Source: https://docs.docker.com/engine/security/ ("only trusted users should control daemon").
5. **macOS ARM emulation cliff** — amd64-only images crawl/fail on M1-M3; users blame EnvMan. Sources: https://orbstack.dev/; https://github.com/abiosoft/colima ("Rosetta 2 emulation").
6. **Subprocess fragility (shell/quote/paused)** — chained exec without sh -c fails; paused container errors. Source: https://docs.docker.com/reference/cli/docker/container/exec/ ("command must be executable").
7. **Hub rate-limit outage on demo day** — unauth 10/hr/IP kills onboarding. Source: https://www.docker.com/pricing/faq/ ("100 pull/hour ... 10 pull/hour").
8. **OrbStack/DevPod/Codespaces out-UX us** — 2s start + prebuilds reset expectations. Sources: https://docs.orbstack.dev/ ("Starts in 2 seconds"); https://docs.github.com/en/codespaces; https://devpod.sh/docs/what-is-devpod ("5-10 times cheaper").
9. **Network-mode drift (NAT→Mirrored)** — localhost works on dev, fails on LAN/VPN. Source: https://learn.microsoft.com/en-us/windows/wsl/networking ("By default WSL uses NAT").
10. **Silent hook/volume staleness** — pre_start failure retained but UI green; anon volumes hide schema drift. Source: https://docs.docker.com/reference/cli/docker/compose/up/ (hook + --renew-anon-volumes).
