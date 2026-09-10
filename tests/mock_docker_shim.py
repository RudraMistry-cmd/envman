#!/usr/bin/env python3
"""Mock `docker` shim for EnvMan executor security tests (no daemon required).

Usage (PATH trick — shadow the real binary for the test process only):
    PATH="<repo>/tests:<original PATH>" pytest tests/test_executor_security.py -q

Behavior: argv[1] dispatches to a canned response. Exit codes mirror the
Docker CLI (0 ok, 1 generic, 125 daemon error, 126 not invocable, 127 not found).
Secrets passed via -e are NEVER echoed (mirrors the redaction requirement).

Routes:
    docker version            -> 0, "Server.APIVersion=1.44"
    docker ps                 -> 0, one fake container line
    docker images ...         -> 0, "" (not cached)
    docker pull <img>         -> 0 if image allowlisted else 1
    docker run ...            -> 0, fake container id (echoes argv count, not values)
    docker exec <c> <exe...>  -> 0 for pg_isready/redis-cli/curl probes; 1 + paused msg if ENV MOCK_PAUSED=1
    docker rm -f <name>       -> 0
    docker network create ... -> 0, or 1 + "already exists" if ENV MOCK_NET_EXISTS=1
Anything else -> 127 + usage error.
"""
from __future__ import annotations
import os
import sys


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print("mock-docker: missing subcommand", file=sys.stderr)
        return 127
    sub = argv[1]
    if sub == "version":
        print("Server.APIVersion=1.44/Client.APIVersion=1.44")
        return 0
    if sub == "ps":
        print("env1_redis Up 5 seconds")
        return 0
    if sub == "images":
        return 0
    if sub == "pull":
        img = argv[2] if len(argv) > 2 else ""
        if img in ("redis:7", "postgres:16", "node:20"):
            print(f"Status: Image is up to date for {img}")
            return 0
        print(f"Error response from daemon: pull access denied for {img}", file=sys.stderr)
        return 1
    if sub == "run":
        # Never echo -e values (secret hygiene); only report arity.
        print(f"mockcontainerid-argv{len(argv)}")
        return 0
    if sub == "exec":
        if os.environ.get("MOCK_PAUSED") == "1":
            print("Error response from daemon: Container is paused, unpause before exec",
                  file=sys.stderr)
            return 1
        rest = argv[3:]
        if rest[:1] == ["sh"] and rest[1:2] == ["-c"]:
            return 0  # container-side shell probe accepted
        if rest[:1] == ["pg_isready"]:
            print("/tmp: accepting connections")
            return 0
        if rest[:2] == ["redis-cli", "ping"]:
            print("PONG")
            return 0
        print(f"mock-docker: exec {rest[0] if rest else ''}: not found", file=sys.stderr)
        return 127
    if sub == "rm":
        return 0
    if sub == "network" and argv[2:3] == ["create"]:
        if os.environ.get("MOCK_NET_EXISTS") == "1":
            print("Error response from daemon: network already exists", file=sys.stderr)
            return 1
        print(argv[3] if len(argv) > 3 else "envman_net")
        return 0
    print(f"mock-docker: unknown subcommand {sub}", file=sys.stderr)
    return 127


if __name__ == "__main__":
    sys.exit(main(sys.argv))
