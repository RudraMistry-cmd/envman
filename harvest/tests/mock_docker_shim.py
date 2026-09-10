"""EnvMan test harness: mock Docker CLI shim + registry verifier example.
Sources:
 - https://docs.docker.com/reference/cli/docker/container/exec/ (exec semantics)
 - https://docs.docker.com/compose/how-tos/startup-order/ (pg_isready healthcheck)
 - https://github.com/docker/compose (compose up --wait pattern)
Run: pytest harvest/tests/test_verifier.py -v
"""
from __future__ import annotations
import json, subprocess, sys
from dataclasses import dataclass
from typing import Dict, List, Optional
from unittest.mock import MagicMock, patch

# --- Shim: fake `docker` binary behaviour for unit tests ---
@dataclass
class FakeCompleted:
    returncode: int = 0
    stdout: str = ""
    stderr: str = ""

class MockDockerShim:
    """Maps argv tuples -> FakeCompleted. Raises TimeoutExpired optionally."""
    def __init__(self):
        self.routes: Dict[tuple, FakeCompleted] = {}
        self.calls: List[list] = []
    def add(self, argv: List[str], rc=0, out="", err=""):
        self.routes[tuple(argv)] = FakeCompleted(rc, out, err)
    def __call__(self, argv, **kw):
        self.calls.append(list(argv))
        key = tuple(argv)
        if key in self.routes:
            return self.routes[key]
        # default: unknown command fails like exit 125/127
        return FakeCompleted(125, "", f"mock: no route for {argv}")

def make_verifier(runner=None):
    runner = runner or (lambda argv, **kw: subprocess.run(argv, capture_output=True, text=True, timeout=15))
    def is_healthy(container: str) -> bool:
        # MUST use explicit executable per docs (no shell string)
        cp = runner(["docker", "exec", "-i", container, "sh", "-c",
                     'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'])
        return cp.returncode == 0
    def inspect_health(container: str) -> Optional[str]:
        cp = runner(["docker", "inspect", "--format={{.State.Health.Status}}", container])
        return cp.stdout.strip() or None
    return is_healthy, inspect_health

# --- Example pytest tests ---
def test_healthy_when_pg_isready_rc0():
    shim = MockDockerShim()
    shim.add(["docker","exec","-i","mydb","sh","-c",'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'], rc=0, out="/tmp: accepting connections")
    is_healthy, _ = make_verifier(shim)
    assert is_healthy("mydb") is True
    assert shim.calls[0][:3] == ["docker","exec","-i"]  # proves argv list, no shell=True

def test_unhealthy_when_rc1_paused_or_starting():
    shim = MockDockerShim()
    shim.add(["docker","exec","-i","mydb","sh","-c",'pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB"'], rc=1, out="no response")
    is_healthy, _ = make_verifier(shim)
    assert is_healthy("mydb") is False

def test_inspect_health_status_parsing():
    shim = MockDockerShim()
    shim.add(["docker","inspect","--format={{.State.Health.Status}}","mydb"], rc=0, out="healthy\n")
    _, inspect_health = make_verifier(shim)
    assert inspect_health("mydb") == "healthy"

def test_subprocess_never_shell_true():
    with patch("subprocess.run") as m:
        m.return_value = MagicMock(returncode=0, stdout="", stderr="")
        is_healthy, _ = make_verifier()
        is_healthy("mydb")
        _, kwargs = m.call_args
        assert kwargs.get("shell", False) is not True

if __name__ == "__main__":
    print("Run with: pytest -v " + __file__)
