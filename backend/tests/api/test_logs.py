"""Tier 1: Pure logic tests for API /logs endpoint — no Docker required.

These tests verify the GET /environments/{env_id}/containers/{container_name}/logs
endpoint logic with mocked subprocess and get_containers.
"""

import pytest
from fastapi import HTTPException
from unittest.mock import patch, MagicMock

from app.api.routes import container_logs


class TestContainerLogsHappyPath:
    """Test the logs endpoint with valid container in environment."""

    @patch("subprocess.run")
    @patch("app.api.routes.get_containers")
    def test_happy_path_returns_logs_and_available_true(
        self, mock_get_containers, mock_subprocess_run
    ):
        """Valid container → returns logs + available=True."""
        # Arrange: container is in the environment
        mock_get_containers.return_value = [
            ("c1", "env1", "envman_node", "node:20", "running", 3000, "some_conn"),
        ]

        # Mock docker logs output
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "log line 1\nlog line 2\n"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        # Act
        result = container_logs(env_id="env1", container_name="envman_node", tail=200)

        # Assert
        assert result["available"] is True
        assert "log line 1" in result["logs"]
        assert result["container"] == "envman_node"
        mock_subprocess_run.assert_called_once_with(
            ["docker", "logs", "--tail", "200", "envman_node"],
            capture_output=True, text=True, timeout=15,
        )
        mock_get_containers.assert_called_once_with("env1")


class TestContainerLogsMismatchedContainer:
    """Test the logs endpoint with container not belonging to environment."""

    @patch("subprocess.run")
    @patch("app.api.routes.get_containers")
    def test_mismatched_container_returns_404(
        self, mock_get_containers, mock_subprocess_run
    ):
        """Container not in env → 404, docker never invoked."""
        # Arrange: different container not in this env
        mock_get_containers.return_value = [
            ("c1", "env1", "envman_postgres", "postgres:16", "running", None, None),
        ]

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            container_logs(env_id="env1", container_name="envman_unknown")

        assert exc_info.value.status_code == 404
        assert "not part of environment" in exc_info.value.detail

        # Docker should never have been called
        mock_subprocess_run.assert_not_called()
        mock_get_containers.assert_called_once_with("env1")


class TestContainerLogsDockerFailure:
    """Test the logs endpoint when docker subprocess fails."""

    @patch("subprocess.run")
    @patch("app.api.routes.get_containers")
    def test_docker_subprocess_failure_returns_available_false(
        self, mock_get_containers, mock_subprocess_run
    ):
        """subprocess.run exception → available=False, 'log fetch failed'."""
        # Arrange: container is in the environment
        mock_get_containers.return_value = [
            ("c1", "env1", "envman_node", "node:20", "running", 3000, "some_conn"),
        ]

        # Make subprocess.run raise an exception (docker down/timeout)
        mock_subprocess_run.side_effect = Exception("docker not available")

        # Act
        result = container_logs(env_id="env1", container_name="envman_node", tail=200)

        # Assert
        assert result["available"] is False
        assert result["logs"] == ""
        assert result["detail"] == "log fetch failed"
        assert result["container"] == "envman_node"


class TestContainerLogsNoLogsAvailable:
    """Test the logs endpoint when docker returns empty output."""

    @patch("subprocess.run")
    @patch("app.api.routes.get_containers")
    def test_no_logs_available_when_returncode_0_and_empty_output(
        self, mock_get_containers, mock_subprocess_run
    ):
        """Docker returns with returncode 0 but empty output → available=True with empty logs."""
        # Arrange
        mock_get_containers.return_value = [
            ("c1", "env1", "envman_node", "node:20", "running", 3000, "some_conn"),
        ]

        # Mock docker with empty output but returncode 0
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        # Act
        result = container_logs(env_id="env1", container_name="envman_node", tail=200)

        # Assert - code returns available=True with empty logs when
        # docker succeeded but produced no output
        assert result["available"] is True
        assert result["logs"] == ""


class TestContainerLogsTailClamping:
    """Test tail parameter clamping."""

    @patch("subprocess.run")
    @patch("app.api.routes.get_containers")
    def test_tail_clamped_min_1(
        self, mock_get_containers, mock_subprocess_run
    ):
        """tail < 1 → clamped to 1."""
        mock_get_containers.return_value = [
            ("c1", "env1", "envman_node", "node:20", "running", 3000, "some_conn"),
        ]
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "logs"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        result = container_logs(env_id="env1", container_name="envman_node", tail=-5)

        assert result["available"] is True
        # Should have been called with tail=1, not tail=-5
        mock_subprocess_run.assert_called_once()
        args, _ = mock_subprocess_run.call_args
        assert args[0][3] == "1"  # tail parameter in the command

    @patch("subprocess.run")
    @patch("app.api.routes.get_containers")
    def test_tail_clamped_max_1000(
        self, mock_get_containers, mock_subprocess_run
    ):
        """tail > 1000 → clamped to 1000."""
        mock_get_containers.return_value = [
            ("c1", "env1", "envman_node", "node:20", "running", 3000, "some_conn"),
        ]
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "logs"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result

        result = container_logs(env_id="env1", container_name="envman_node", tail=5000)

        assert result["available"] is True
        mock_subprocess_run.assert_called_once()
        args, _ = mock_subprocess_run.call_args
        assert args[0][3] == "1000"  # tail parameter in the command


class TestContainerLogsMissingEnv:
    """Test the logs endpoint when environment doesn't exist."""

    @patch("subprocess.run")
    @patch("app.api.routes.get_containers")
    def test_missing_env_raises_404_environment_not_found(
        self, mock_get_containers, mock_subprocess_run
    ):
        """When env doesn't exist at all → 404 'environment not found'."""
        # Arrange: make get_containers raise for missing env
        mock_get_containers.side_effect = Exception("unknown environment")

        # Act & Assert
        from fastapi import HTTPException
        try:
            container_logs(env_id="nonexistent", container_name="envman_node")
            assert False, "Expected HTTPException"
        except HTTPException as e:
            assert e.status_code == 404
            assert "environment not found" in e.detail