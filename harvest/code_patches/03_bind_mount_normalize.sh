#!/usr/bin/env bash
# Source: https://docs.docker.com/engine/storage/bind-mounts/
# Quote: "Containers with bind mounts strongly tied to host"
# Purpose: cross-platform bind-mount normalization for EnvMan executor (Win native + WSL2).
set -euo pipefail
HOST_PATH="$1"   # e.g. C:\proj or /home/u/proj or ./rel
CONT_PATH="${2:-/app}"
# 1) Windows Git-Bash / PowerShell -> POSIX for --mount
# Use wslpath when inside WSL interop; else convert drive letter.
normalize() {
  p="$1"
  if command -v wslpath >/dev/null 2>&1 && [[ "$p" =~ ^[A-Za-z]: ]]; then wslpath -a "$p";
  elif [[ "$p" =~ ^[A-Za-z]: ]]; then echo "$p" | sed -E 's|^([A-Za-z]):|/\L\1|; s|\\|/|g';
  else realpath -m "$p"; fi
}
SRC="$(normalize "$HOST_PATH")"
# 2) Prefer --mount (explicit, fails if missing) over -v (auto-creates as dir)
docker run --rm --mount "type=bind,src=${SRC},dst=${CONT_PATH},readonly" busybox ls "$CONT_PATH"
# Writable variant with create-src guard:
# docker run --rm --mount type=bind,src="$SRC",dst=/data,bind-create-src busybox touch /data/ok
