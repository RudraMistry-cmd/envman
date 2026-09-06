"""Tier 1: Pure logic tests for API export/import endpoints — no Docker required."""

import asyncio
import json
from unittest.mock import patch, AsyncMock

from fastapi import HTTPException

from app.models.environment import EnvironmentConfig, ServiceSpec


def test_export_returns_stored_services():
    """Export returns the stored services from config_json."""
    from app.api.routes import export_environment

    stored = json.dumps({
        "services": [
            {"name": "node", "image": "node:20", "port": 3000},
            {"name": "postgres", "image": "postgres:16", "port": 5432},
        ],
        "network_name": "envman_net",
    })
    with patch("app.api.routes.get_environment", return_value=("env1", "envman_net", "ts")), \
         patch("app.api.routes.get_environment_config", return_value=stored):
        result = export_environment(env_id="env1")

    assert result["environment_id"] == "env1"
    assert len(result["services"]) == 2
    assert result["services"][0]["name"] == "node"
    assert result["services"][0]["image"] == "node:20"
    assert result["services"][0]["port"] == 3000
    assert result["services"][1]["name"] == "postgres"
    assert result["services"][1]["image"] == "postgres:16"
    assert result["services"][1]["port"] == 5432


def test_export_unknown_env():
    """Export unknown environment returns 404."""
    from app.api.routes import export_environment

    with patch("app.api.routes.get_environment", return_value=None):
        try:
            export_environment(env_id="nonexistent")
            assert False, "Expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 404
            assert "environment not found" in e.detail


def test_export_no_stored_config():
    """Export environment with no stored config returns 404."""
    from app.api.routes import export_environment

    with patch("app.api.routes.get_environment", return_value=("env1", "envman_net", "ts")), \
         patch("app.api.routes.get_environment_config", return_value=None):
        try:
            export_environment(env_id="env1")
            assert False, "Expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 404
            assert "no stored config" in e.detail.lower()


def test_import_valid_json_calls_run_setup():
    """Import valid JSON calls run_setup and returns started."""
    from app.api.routes import import_environment

    mock_run = AsyncMock(return_value="new_env123")
    with patch("app.api.routes.run_setup", mock_run):
        result = asyncio.run(import_environment(
            EnvironmentConfig(services=[
                ServiceSpec(name="node", image="node:20"),
                ServiceSpec(name="postgres", image="postgres:16"),
            ])
        ))
    assert result == {"status": "started", "environment_id": "new_env123"}
    mock_run.assert_awaited_once()


def test_import_empty_services():
    """Import with empty services list still delegates to run_setup."""
    from app.api.routes import import_environment

    mock_run = AsyncMock(return_value="empty_env")
    with patch("app.api.routes.run_setup", mock_run):
        result = asyncio.run(import_environment(EnvironmentConfig(services=[])))
    assert result == {"status": "started", "environment_id": "empty_env"}
    mock_run.assert_awaited_once()
