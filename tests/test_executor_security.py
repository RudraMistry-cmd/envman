"""Executor security tests — verify CORRECTED behavior (apply recommended_patches.diff first).

Run:  pytest tests/test_executor_security.py -q        (repo root; no Docker daemon needed)
Apply: git checkout -b feature/executor-hardening && git apply recommended_patches.diff && pytest -q

Covers security_risks.md R1-R5/R7: escaping, env leakage, WSL paths, error parsing.
No test uses shell=True. Dangerous inputs travel as single argv atoms (asserted).
"""
from __future__ import annotations
import os
import subprocess
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
pytest.importorskip("pydantic", reason="backend deps required (pip install -r backend/requirements.txt)")

from app.engine import executor as ex  # noqa: E402  (patched module under test)


# --- R3: argument escaping / allowlist -------------------------------------

def test_injection_name_rejected():
    with pytest.raises(ValueError):
        ex.validate_name("x; rm -rf /")
    with pytest.raises(ValueError):
        ex.validate_name("a && calc.exe")
    assert ex.validate_name("env1_redis-7.db") == "env1_redis-7.db"


def test_build_cmd_is_list_and_inert():
    cmd = ex.build_docker_run_cmd(name="mydb", image="postgres:16",
                                  network_name="envman_net",
                                  env={"POSTGRES_PASSWORD": "s3cret; rm -rf /"})
    assert isinstance(cmd, list) and all(isinstance(a, str) for a in cmd)
    # dangerous payload survives as ONE atom (would only split under a shell)
    atom = [a for a in cmd if "rm -rf" in a]
    assert len(atom) == 1 and atom[0].startswith("POSTGRES_PASSWORD=")


# --- R4: env leakage / validation ------------------------------------------

def test_env_key_rejected():
    with pytest.raises(ValueError):
        ex.validate_env({"A=B": "x"})          # smuggled delimiter
    with pytest.raises(ValueError):
        ex.validate_env({"A B": "x"})          # whitespace key
    with pytest.raises(ValueError):
        ex.validate_env({"OK": "line1\nline2"})  # newline smuggle


def test_secret_redaction_in_logs():
    cmd = ["docker", "run", "-e", "POSTGRES_PASSWORD=s3cret", "-e", "PORT=5432", "postgres:16"]
    red = ex.redact_cmd(cmd)
    assert "POSTGRES_PASSWORD=***" in red and "PORT=5432" in red
    assert "s3cret" not in " ".join(red)


# --- R5: WSL path normalization ---------------------------------------------

def test_windows_backslash_normalized_without_wsl(monkeypatch):
    import shutil as _sh
    _real = _sh.which
    monkeypatch.setattr(_sh, "which", lambda c, **k: None if c == "wslpath" else _real(c, **k))
    assert ex.normalize_volume("C:\\proj\\data:/app") == "C:/proj/data:/app"
    assert ex.normalize_volume("/home/u/proj:/app:ro") == "/home/u/proj:/app:ro"


def test_wslpath_used_when_present(monkeypatch):
    # Simulate WSL: stub module-boundary calls (works on any OS, no shell).
    import shutil as _sh
    _real_which = _sh.which
    monkeypatch.setattr(_sh, "which",
                        lambda c, **k: "C:/fake/wslpath" if c == "wslpath" else _real_which(c, **k))

    class _R:
        returncode = 0
        stdout = "/mnt/c/proj\n"
    monkeypatch.setattr(ex.subprocess, "run", lambda *a, **k: _R())
    assert ex.normalize_volume("C:\\proj:/app") == "/mnt/c/proj:/app"


# --- error parsing / timeouts (R1) ------------------------------------------

class _FakeResult:
    def __init__(self, rc=0, out="", err=""):
        self.returncode = rc
        self.stdout = out
        self.stderr = err


def test_run_sync_timeout_mapping(monkeypatch):
    def boom(*_a, **_k):
        raise subprocess.TimeoutExpired(cmd="docker", timeout=15)
    monkeypatch.setattr(ex.subprocess, "run", boom)
    r = ex._run_sync(["docker", "ps"], timeout=15)
    assert r["code"] == -1 and "Timed out after 15s" in r["stderr"]


def test_verifier_pg_probes_are_timebounded():
    src = open(os.path.join(os.path.dirname(__file__), "..", "backend",
                            "app", "engine", "verifier.py"), encoding="utf-8").read()
    assert "pg_isready" in src and "timeout=15" in src      # R1: pg_isready bound
    assert "SELECT 1 AS connected" in src and "timeout=30" in src  # R1: query bound
