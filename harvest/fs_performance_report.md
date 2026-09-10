# Bind-Mount Filesystem Performance Report (numbers + citations)
Date: 2026-09-10

## Cited numbers
1. OrbStack provision benchmark: **OrbStack 17 min vs Docker Desktop 45 min** (Supabase dev-env provision, Aug 2023) — https://orbstack.dev/ — Quote: "Time to provision development environment (lower is better) OrbStack 17 min Docker Desktop 45 min"
2. OrbStack start: **2 seconds**; background CPU **<0.1%** on Apple Silicon; disk **<10 MB** out of box — https://docs.orbstack.dev/ ("Starts in 2 seconds") + https://orbstack.dev/ (lightning fast / light as feather: VirtioFS, Rosetta x86, "Bind mounts and port forwards just work")
3. WSL2 backend: "improvements to file system sharing, faster cold-start times, dynamic resource allocation" + `autoMemoryReclaim` — https://docs.docker.com/desktop/features/wsl/
4. Bind-mount coupling: "Containers with bind mounts strongly tied to host" + daemon-host (VM) semantics for Desktop — https://docs.docker.com/engine/storage/bind-mounts/
5. WSL networking modes (NAT default; Mirrored adds localhost/VPN/multicast) affect where files+ports live — https://learn.microsoft.com/en-us/windows/wsl/networking ("By default WSL uses NAT architecture")
6. DDEV WSL2 field evidence: Mirrored mode needs `hostAddressLoopback=true`; VirtioProxy experimental with "no internet / Xdebug" failures — https://ddev.readthedocs.io/en/stable/
7. Desktop install scale: WSL 2.1.5+, 8GB RAM, SLAT/virtualization; per-user vs all-users backends — https://docs.docker.com/desktop/setup/install/windows-install/

## What the numbers mean for EnvMan
- macOS bind mounts under Docker Desktop (osxfs/gRPC-FUSE legacy) are the classic slow path (node_modules/postgres I/O); OrbStack VirtioFS and files-in-VM/named volumes are the fast paths. The 17-vs-45min gap is provision-level proof users feel.
- Windows: files on `C:\` shared into WSL2-VM daemon = 2-hop (9P/VirtioFS) — slow; files INSIDE WSL distro (`\\wsl$\Ubuntu\home`) = 1-hop — fast. DDEV's mirrored/virtioproxy pain confirms networking+fs interact.
- Linux: native bind mounts fast; only SELinux `:z/:Z` relabel and propagation (`rprivate` default; "Mount propagation doesn't work with Docker Desktop") matter — https://docs.docker.com/engine/storage/bind-mounts/

## Mitigation ladder (cheapest first)
1. Keep hot I/O off bind mounts: `node_modules`, `PGDATA`, build caches → named volumes (see recommended_workarounds.md).
2. macOS: recommend OrbStack/Colima+VirtioFS; file access via native-files; Rosetta for x86 images — https://docs.orbstack.dev/ + https://github.com/abiosoft/colima
3. Windows: keep repo inside WSL fs + WSL integration per-distro; `.wslconfig` reclaim; avoid `/mnt/c` hot loops — https://docs.docker.com/desktop/features/wsl/
4. Measure: time `docker run --rm -v` write/read 1k files; surface in UI (see workarounds).
