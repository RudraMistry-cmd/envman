#!/usr/bin/env bash
# Sources: WSL networking + DDEV WSL2 guidance
#  - https://learn.microsoft.com/en-us/windows/wsl/networking ("By default WSL uses NAT architecture")
#  - https://ddev.readthedocs.io/en/stable/ (hostAddressLoopback=true for Mirrored)
#  - https://docs.docker.com/desktop/features/wsl/ (WSL integration per-distro)
set -euo pipefail
echo "== wsl version =="; wsl.exe -l -v || true
echo "== host IP seen from WSL =="; ip route show | grep -i default | awk '{print $3}' || true
echo "== .wslconfig =="; cat ~/.wslconfig 2>/dev/null || cat /mnt/c/Users/$USER/.wslconfig 2>/dev/null || echo "(no .wslconfig)"
cat <<'CFG'
# Fix for Mirrored-mode loopback (C:\Users\<you>\.wslconfig):
# [wsl2]
# networkingMode=Mirrored
# [experimental]
# hostAddressLoopback=true
CFG
# Port-proxy fallback for NAT LAN access:
# netsh interface portproxy add v4tov4 listenport=4000 listenaddress=0.0.0.0 connectport=4000 connectaddress=$(wsl hostname -I)
