# Unit Test Patterns: pytest Mocks + Mock Docker Shim
Sources: subprocess/shlex/docker-py/Engine API as in security_risks.md; Compose health gating https://docs.docker.com/compose/how-tos/startup-order/ ("service_healthy ... pg_isready"); exec https://docs.docker.com/reference/cli/docker/container/exec/.

## Pattern A — assert argv list, never shell (R1/R2)
```python
from unittest.mock import patch, MagicMock
def test_no_shell_true():
    with patch("subprocess.run") as m:
        m.return_value = MagicMock(returncode=0, stdout="", stderr="")
        from backend.app.engine import executor
        executor.run_docker(["exec","-i","mydb","sh","-c",'pg_isready'])
        _, kw = m.call_args
        assert kw.get("shell", False) is False
        assert isinstance(m.call_args[0][0], list)  # list-based, Windows-safe
```

## Pattern B — injection payload is inert atom (E1/E2)
```python
def test_injection_inert():
    from harvest.tests.mock_docker_shim import MockDockerShim, make_verifier
    shim = MockDockerShim()
    evil = "c; powershell -c evil #"
    # even with evil string, shim receives it as ONE argv element — no split, no exec
    shim.add(["docker","exec","-i",evil,"sh","-c","pg_isready"], rc=0, out="ok")
    ok,_ = make_verifier(shim)
    assert ok(evil) is True and len(shim.calls[0]) == 6
```

## Pattern C — timeout + PATH/perm errors (R4)
```python
import subprocess
from unittest.mock import patch
def test_timeout_kills():
    with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("docker", 15)):
        try:
            from backend.app.engine import executor
            executor.run_docker(["ps"], timeout=15)
            assert False
        except subprocess.TimeoutExpired: pass
def test_env_merges_not_wipes(monkeypatch):
    monkeypatch.setenv("PATH", "/usr/bin")
    with patch("subprocess.run") as m:
        from backend.app.engine import executor
        m.return_value = MagicMock(returncode=0, stdout="", stderr="")
        executor.run_docker(["ps"], extra_env={"A":"1"})
        assert "PATH" in m.call_args[1]["env"] and m.call_args[1]["env"]["A"]=="1"
```

## Pattern D — full shim script (runnable, no daemon)
See `harvest/tests/mock_docker_shim.py` (MockDockerShim + make_verifier + 4 tests, `pytest` green 2026-09-10).
Run: `python -m pytest harvest/tests/mock_docker_shim.py -v` (also `backend` suite: `cd backend; python -m pytest tests/ -q`).
CI: `harvest/tests/ci_github_actions.yml` runs `compose up -d --wait --wait-timeout 120` then mocked unit tests.

## docker-py vs CLI test seam
Keep ONE seam (`run_docker(argv)`); SDK swap = replace seam impl with `docker.from_env()` (https://docker-py.readthedocs.io/en/stable/) without touching callers. Pin API via `docker version` preflight (https://docs.docker.com/engine/api/).
