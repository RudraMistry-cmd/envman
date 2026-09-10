"""Reconciler prototype: compare DB desired state vs `docker ps` observed state.
Pattern: K8s level-triggered control loop (https://kubernetes.io/docs/concepts/architecture/controller/).
Usage: python reconciler_example.py --dry-run  |  python reconciler_example.py --apply
"""
from __future__ import annotations
import json, subprocess, sys

LABELS = {"env": "envman.env", "svc": "envman.service"}

def sh(argv: list[str], timeout=15):
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout, shell=False)

def desired_from_db() -> dict:
    # STUB: replace with sqlite query; shape mirrors EnvMan storage/db.py
    return {"env1": {"redis": {"image": "redis:7", "want": "running"},
                     "db": {"image": "postgres:16", "want": "running"}}}

def observed() -> dict:
    cp = sh(["docker", "ps", "-a", "--format", "{{json .}}"])
    out: dict = {}
    for line in cp.stdout.splitlines():
        try: o = json.loads(line)
        except Exception: continue
        out[o.get("Names", "")] = {"state": o.get("State", ""), "image": o.get("Image", ""),
                                    "labels": o.get("Labels", "")}
    return out

def plan(desired, seen) -> list[tuple[str, str, str]]:
    actions = []
    for env, svcs in desired.items():
        for svc, d in svcs.items():
            name = f"{env}_{svc}"
            s = seen.get(name)
            if not s:
                actions.append(("create", env, svc))
            elif d["want"] == "running" and s["state"] != "running":
                actions.append(("start", env, svc))
            elif d["image"] not in s["image"]:
                actions.append(("recreate", env, svc))  # like --force-recreate
    for name in seen:
        if name.startswith("env1_") and name.split("_", 1)[1] not in desired["env1"]:
            actions.append(("remove-orphan", "env1", name))  # like --remove-orphans
    return actions

if __name__ == "__main__":
    dry = "--apply" not in sys.argv
    acts = plan(desired_from_db(), observed())
    if not acts:
        print("IN SYNC: no actions")
    for a in acts:
        print(("PLAN " if dry else "APPLY ") + f"{a[0]} {a[1]}/{a[2]}")
