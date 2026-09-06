"""Tier 1: Pure logic tests for API /stop and /start endpoints — no Docker required.

These tests verify the POST /environments/{env_id}/stop and
POST /environments/{env_id}/start endpoint logic with mocked subprocess and db.
"""

import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from app.api.routes import stop_environment, start_environment


def _cmds(mock_run):
    """Positional argv of every subprocess.run call."""
    return [c.args[0] for c in mock_run.call_args_list]


class TestStopEnvironment:
    """Test the stop environment endpoint with mocked subprocess."""

    @patch("app.api.routes.subprocess.run")
    @patch("app.api.routes.update_container_status")
    @patch("app.api.routes.get_containers")
    @patch("app.api.routes.get_environment")
    def test_stop_returns_stopped_docker_stop_called_not_rm(
        self, mock_get_env, mock_get_containers, mock_update, mock_run
    ):
        """Stop all containers → returns stopped + docker stop called (not rm)."""
        mock_get_env.return_value = ("env1", "envman_net", "ts")
        mock_get_containers.return_value = [
            ("c1", "env1", "envman_node", "node:20", "running", 3000, "some_conn"),
            ("c2", "env1", "envman_postgres", "postgres:16", "running", None, None),
        ]
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        result = stop_environment(env_id="env1")

        assert result["status"] == "stopped"
        assert result["environment_id"] == "env1"
        assert len(result["results"]) == 2
        cmds = _cmds(mock_run)
        assert ["docker", "stop", "envman_node"] in cmds
        assert ["docker", "stop", "envman_postgres"] in cmds
        assert all("rm" not in c for c in cmds)
        assert mock_update.call_count == 2


class TestStopEnvironmentUnknownEnv:
    """Test the stop environment endpoint with unknown environment."""

    @patch("app.api.routes.subprocess.run")
    @patch("app.api.routes.get_containers")
    @patch("app.api.routes.get_environment")
    def test_stop_unknown_env_404(self, mock_get_env, mock_get_containers, mock_run):
        """Unknown environment → 404, docker never invoked."""
        from fastapi import HTTPException

        mock_get_env.return_value = None
        mock_get_containers.return_value = []
        try:
            stop_environment(env_id="nonexistent")
            assert False, "Expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 404
            assert "environment not found" in e.detail
        mock_run.assert_not_called()


class TestStartEnvironment:
    """Test the start environment endpoint with mocked subprocess."""

    @patch("app.api.routes.subprocess.run")
    @patch("app.api.routes.update_container_status")
    @patch("app.api.routes.get_containers")
    @patch("app.api.routes.get_environment")
    def test_start_calls_docker_start_plus_verifier(
        self, mock_get_env, mock_get_containers, mock_update, mock_run
    ):
        """Start all containers → calls docker start + verifier."""
        mock_get_env.return_value = ("env1", "envman_net", "ts")
        mock_get_containers.return_value = [
            ("c1", "env1", "envman_node", "node:20", "stopped", 3000, "some_conn"),
        ]
        mock_run.return_value = MagicMock(returncode=0, stdout="c1", stderr="")
        mock_verify = AsyncMock(return_value=[{"service": "node", "status": "ready"}])

        with patch("app.api.routes.verify_environment", mock_verify):
            result = asyncio.run(start_environment(env_id="env1"))

        assert result["status"] == "starting"
        assert result["environment_id"] == "env1"
        assert len(result["docker_results"]) == 1
        cmds = _cmds(mock_run)
        assert ["docker", "start", "envman_node"] in cmds
        assert all("stop" not in c for c in cmds)
        mock_verify.assert_awaited_once()
        assert result["verification"] == [{"service": "node", "status": "ready"}]

    @patch("app.api.routes.subprocess.run")
    @patch("app.api.routes.get_containers")
    @patch("app.api.routes.get_environment")
    def test_start_unknown_env_404(self, mock_get_env, mock_get_containers, mock_run):
        """Unknown environment → 404, docker never invoked."""
        from fastapi import HTTPException

        mock_get_env.return_value = None
        mock_get_containers.return_value = []
        try:
            asyncio.run(start_environment(env_id="nonexistent"))
            assert False, "Expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 404
            assert "environment not found" in e.detail
        mock_run.assert_not_called()
