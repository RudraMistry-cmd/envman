"""Tier 1: Tests verifying coordinator tears down environments on all failure modes.

Tests prove that if any step raises an exception (e.g. NameError, Docker crash),
fails with non-zero exit code, or if an unexpected exception occurs,
coordinator ALWAYS executes delete_environment(env_id), preventing ghost environments.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.engine.coordinator import run_setup
from app.models.environment import EnvironmentConfig, ServiceSpec


@pytest.fixture
def sample_config():
    return EnvironmentConfig(
        services=[
            ServiceSpec(name="node", image="node:20", port=3000),
        ],
        network_name="envman_net",
    )


class TestCoordinatorFailureCleanup:
    """Test coordinator cleanup guarantees on failure."""

    @pytest.mark.asyncio
    @patch("app.engine.coordinator.delete_environment")
    @patch("app.engine.coordinator.execute_step")
    @patch("app.engine.coordinator.plan_environment")
    @patch("app.engine.coordinator.store_environment")
    @patch("app.engine.coordinator.save_environment_config")
    @patch("app.engine.coordinator.emit")
    async def test_step_exception_triggers_delete_environment(
        self, mock_emit, mock_save_cfg, mock_store_env, mock_plan, mock_exec, mock_delete, sample_config
    ):
        """When execute_step raises an unhandled exception, delete_environment is called."""
        plan_mock = MagicMock()
        step1 = MagicMock(id="start_node", type="start_container", params={"name": "envman_node"})
        plan_mock.steps = [step1]
        plan_mock.network_name = "envman_net_test"
        mock_plan.return_value = plan_mock

        # Step raises unexpected exception mid-execution (like NameError)
        mock_exec.side_effect = NameError("name 'Optional' is not defined")

        env_id = await run_setup(sample_config)

        assert mock_delete.call_count == 1
        assert mock_delete.call_args[0][0] == env_id

    @pytest.mark.asyncio
    @patch("app.engine.coordinator.delete_environment")
    @patch("app.engine.coordinator.execute_step")
    @patch("app.engine.coordinator.plan_environment")
    @patch("app.engine.coordinator.store_environment")
    @patch("app.engine.coordinator.save_environment_config")
    @patch("app.engine.coordinator.emit")
    async def test_step_nonzero_exit_triggers_delete_environment(
        self, mock_emit, mock_save_cfg, mock_store_env, mock_plan, mock_exec, mock_delete, sample_config
    ):
        """When execute_step returns a non-zero code, delete_environment is called."""
        plan_mock = MagicMock()
        step1 = MagicMock(id="pull_node", type="pull_image", params={"image": "invalid:image"})
        plan_mock.steps = [step1]
        plan_mock.network_name = "envman_net_test"
        mock_plan.return_value = plan_mock

        mock_exec.return_value = {"code": 1, "stdout": "", "stderr": "image not found"}

        env_id = await run_setup(sample_config)

        assert mock_delete.call_count == 1
        assert mock_delete.call_args[0][0] == env_id

    @pytest.mark.asyncio
    @patch("app.engine.coordinator.delete_environment")
    @patch("app.engine.coordinator.execute_step")
    @patch("app.engine.coordinator.plan_environment")
    @patch("app.engine.coordinator.store_environment")
    @patch("app.engine.coordinator.save_environment_config")
    @patch("app.engine.coordinator.emit")
    async def test_emit_failure_does_not_prevent_delete_environment(
        self, mock_emit, mock_save_cfg, mock_store_env, mock_plan, mock_exec, mock_delete, sample_config
    ):
        """If emit fails (e.g. WebSocket disconnected), delete_environment is still executed."""
        plan_mock = MagicMock()
        step1 = MagicMock(id="start_node", type="start_container", params={"name": "envman_node"})
        plan_mock.steps = [step1]
        plan_mock.network_name = "envman_net_test"
        mock_plan.return_value = plan_mock

        mock_exec.side_effect = RuntimeError("step crash")
        # emit raises WebSocket exception on step_failed
        async def fake_emit(event, data):
            if event == "step_failed":
                raise ConnectionResetError("client disconnected")
        mock_emit.side_effect = fake_emit

        env_id = await run_setup(sample_config)

        # delete_environment must still be called in finally
        assert mock_delete.call_count >= 1
        assert mock_delete.call_args[0][0] == env_id

    @pytest.mark.asyncio
    @patch("app.engine.coordinator.delete_environment")
    @patch("app.engine.coordinator.plan_environment")
    async def test_unexpected_exception_triggers_delete_environment(
        self, mock_plan, mock_delete, sample_config
    ):
        """If an unexpected exception is raised in coordinator outer flow, delete_environment is called."""
        mock_plan.side_effect = Exception("database disk full")

        env_id = await run_setup(sample_config)

        assert mock_delete.call_count == 1
        assert mock_delete.call_args[0][0] == env_id
