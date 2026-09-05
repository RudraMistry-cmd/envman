"""Tier 1: connection info must never fabricate reachability.

A registry default_port is not proof of a live `-p` binding. When docker
inspect finds no real binding, host_port/connection_string must be None -
the same "no host port" state shown for node/python - never a fabricated
string.
"""

import pytest
from unittest.mock import AsyncMock

import app.engine.verifier as verifier
from app.engine.verifier import build_connection_info


class TestBuildConnectionInfoNoSilentFallback:
    """build_connection_info(None host_port) must stay None without opt-in."""

    def test_none_stays_none_postgres(self):
        assert build_connection_info("postgres", "postgres:16", None) == {
            "host_port": None, "connection_string": None, "connection_type": None,
        }

    def test_none_stays_none_redis(self):
        info = build_connection_info("redis", "redis:7", None)
        assert info["host_port"] is None
        assert info["connection_string"] is None

    def test_none_stays_none_node(self):
        assert build_connection_info("node", "node:20", None)["connection_string"] is None

    def test_real_port_builds_string(self):
        assert build_connection_info("postgres", "postgres:16", 5432) == {
            "host_port": 5432,
            "connection_string": "postgres://postgres:postgres@localhost:5432/postgres",
            "connection_type": "postgres",
        }

    def test_explicit_cosmetic_opt_in_still_works(self):
        info = build_connection_info("redis", "redis:7", None, allow_registry_default=True)
        assert info["host_port"] == 6379
        assert info["connection_string"] == "redis://localhost:6379"


class TestGetActualHostPortNoSilentFallback:
    """get_actual_host_port must return None - never a default - without a binding."""

    @pytest.mark.asyncio
    async def test_empty_ports_returns_none_not_default(self, monkeypatch):
        monkeypatch.setattr(
            verifier, "run_command",
            AsyncMock(return_value={"code": 0, "stdout": "{}", "stderr": ""}),
        )
        assert await verifier.get_actual_host_port("envman_postgres") is None

    @pytest.mark.asyncio
    async def test_inspect_failure_returns_none(self, monkeypatch):
        monkeypatch.setattr(
            verifier, "run_command",
            AsyncMock(return_value={"code": 1, "stdout": "", "stderr": "No such object"}),
        )
        assert await verifier.get_actual_host_port("envman_postgres") is None

    @pytest.mark.asyncio
    async def test_real_binding_returned(self, monkeypatch):
        stdout = '{"5432/tcp": [{"HostIp": "0.0.0.0", "HostPort": "5432"}]}'
        monkeypatch.setattr(
            verifier, "run_command",
            AsyncMock(return_value={"code": 0, "stdout": stdout, "stderr": ""}),
        )
        assert await verifier.get_actual_host_port("envman_postgres") == 5432
