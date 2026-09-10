# Recommended Workarounds: Detect + Auto-Suggest Fixes in EnvMan UI
Sources: same as fs_performance_report.md (orbstack.dev, docs.orbstack.dev, Desktop WSL/file-sharing, bind-mounts, MS WSL networking, DDEV, colima).

## D1. Detect slow-bind-mount (all OS)
- Probe on env create: `time docker run --rm --mount type=bind,src=<proj>,dst=/t busybox sh -c 'time (i=0; while [ $i -lt 500 ]; do echo x >> /t/.probe; i=$((i+1)); done)'` + read-back. Threshold: >8s warn, >20s blocking suggest.
- Signals: `node_modules` on bind; `PGDATA` on bind; `C:\` or `/Users` prefix on Win/Mac + Desktop backend.

## D2. Auto-suggest copy (UI strings)
- macOS + Desktop + bind hot path: "Bind mounts are ~3-10x slower here. [Move code into VM volume] [Switch to OrbStack] [Keep anyway]" — link https://orbstack.dev/ benchmarks.
- Windows + repo on C:\: "Repo is on Windows fs (2-hop). [Move to \\wsl$\Ubuntu\home] [Use named volume for data]" — link https://docs.docker.com/desktop/features/wsl/
- Generic: "[Convert PGDATA/node_modules to named volume] (keeps code live, data fast)" — link https://docs.docker.com/engine/storage/bind-mounts/
- Mirrored/VirtioProxy weirdness: "Detected networkingMode=Mirrored without hostAddressLoopback — [Show .wslconfig fix]" — https://ddev.readthedocs.io/en/stable/

## D3. One-click actions EnvMan should implement
1. `Convert to named volume` (data dirs only): create volume, `chown`, update compose `volumes:`, keep code bind.
2. `Relocate repo into WSL` (Windows): `wsl --list`, rsync, reopen.
3. `Switch backend` helper: detect `colima status` / OrbStack / Desktop; set DOCKER_HOST; re-verify (see platform handling in issues ENV-014).
4. `Rosetta/arch` toggle on ARM: set `platform: linux/arm64` or enable Rosetta — https://github.com/abiosoft/colima
5. Perf badge per env: "fs: fast/ok/slow (2.1s/500 files)" persisted; re-run on backend change.
