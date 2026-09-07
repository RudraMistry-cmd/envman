"""Tier 1: Port conflict auto-reassignment tests for executor & coordinator.

Tests prove that an occupied host port triggers automatic reassignment to the next
free port, updates step.params, records reassignment metadata in the step result,
and formats the coordinator event message accurately.
"""

import pytest
from unittest.mock import AsyncMock, patch

from app.models.step import Step
from app.models.environment import EnvironmentConfig, ServiceSpec
import app.engine.executor as executor
import app.engine.coordinator as coordinator


class TestExecutorPortReassignment:
    @pytest.mark.asyncio
    async def test_proactive_reassignment_when_host_port_in_use(self, monkeypatch):
        """When host port is occupied, executor reassigns to next free port."""
        commands_run = []

        async def mock_run_command(cmd, timeout=300):
            commands_run.append(list(cmd))
            return {"stdout": "mock_cid_123456", "stderr": "", "code": 0}

        monkeypatch.setattr(executor, "run_command", mock_run_command)

        # Mock port availability: 5432 is in use, 5433 is free
        def mock_is_available(port):
            return port != 5432

        monkeypatch.setattr(executor.port_allocator, "is_available", mock_is_available)
        executor.port_allocator.allocated.clear()

        step = Step(
            id="start_postgres",
            type="start_container",
            params={
                "name": "envman_postgres",
                "image": "postgres:16",
                "port": "5432:5432",
            },
        )

        result = await executor._start_container(step, network_name="envman_net", env_id="env1")

        assert result["code"] == 0
        assert result.get("reassigned_port") == 5433
        assert result.get("original_port") == 5432
        assert "Port 5432 was in use" in result.get("reassignment_message", "")

        # Verify step params were updated
        assert step.params["port"] == "5433:5432"
        assert step.params["reassigned_port"] == 5433

        # Verify docker command used -p 5433:5432
        run_cmds = [c for c in commands_run if "run" in c]
        assert len(run_cmds) == 1
        assert "-p" in run_cmds[0]
        port_idx = run_cmds[0].index("-p")
        assert run_cmds[0][port_idx + 1] == "5433:5432"

    @pytest.mark.asyncio
    async def test_docker_runtime_port_conflict_triggers_retry(self, monkeypatch):
        """When docker run returns a port allocation error, executor retries with next port."""
        commands_run = []
        call_count = 0

        async def mock_run_command(cmd, timeout=300):
            nonlocal call_count
            commands_run.append(list(cmd))
            if "run" in cmd:
                call_count += 1
                if call_count == 1:
                    # First attempt fails with Docker bind error
                    return {
                        "stdout": "",
                        "stderr": "driver failed programming external connectivity on endpoint: Bind for 0.0.0.0:6379 failed: port is already allocated",
                        "code": 1,
                    }
                # Second attempt succeeds on reassigned port
                return {"stdout": "mock_cid_redis", "stderr": "", "code": 0}
            return {"stdout": "", "stderr": "", "code": 0}

        monkeypatch.setattr(executor, "run_command", mock_run_command)
        executor.port_allocator.allocated.clear()

        step = Step(
            id="start_redis",
            type="start_container",
            params={
                "name": "envman_redis",
                "image": "redis:7",
                "port": "6379:6379",
            },
        )

        result = await executor._start_container(step, network_name="envman_net", env_id="env1")

        assert result["code"] == 0
        assert result.get("reassigned_port") == 6380
        assert result.get("original_port") == 6379
        assert step.params["port"] == "6380:6379"

    @pytest.mark.asyncio
    async def test_coordinator_event_includes_reassigned_port(self, monkeypatch):
        """Coordinator step_done event includes reassignment message."""
        events = []

        async def mock_emit(event_name, data):
            events.append((event_name, data))

        monkeypatch.setattr(coordinator, "emit", mock_emit)
        monkeypatch.setattr(coordinator, "verify_environment", AsyncMock(return_value=[{"service": "postgres", "status": "ready"}]))

        # Plan with single service
        config = EnvironmentConfig(
            services=[ServiceSpec(name="postgres", image="postgres:16", port=5432)],
            network_name="envman_net",
        )

        # Mock execute_step returning reassignment
        async def mock_execute_step(step, network_name, env_id):
            if step.type == "start_container":
                return {
                    "stdout": "cid_pg",
                    "stderr": "",
                    "code": 0,
                    "reassigned_port": 5433,
                    "original_port": 5432,
                }
            return {"stdout": "", "stderr": "", "code": 0}

        monkeypatch.setattr(coordinator, "execute_step", mock_execute_step)
        monkeypatch.setattr(coordinator, "plan_environment", AsyncMock(return_value=type("MockPlan", (), {
            "steps": [Step(id="start_postgres", type="start_container", params={"name": "envman_postgres", "image": "postgres:16"})],
            "network_name": "envman_net",
        })()))

        await coordinator.run_setup(config)

        step_done_events = [data for name, data in events if name == "step_done"]
        assert len(step_done_events) == 1
        done = step_done_events[0]
        assert done["reassigned_port"] == 5433
        assert done["original_port"] == 5432
        assert "port reassigned from 5432 to 5433" in done["message"]

    def test_executor_type_annotations_resolve(self):
        """Ensure all type annotations in executor module resolve without NameError.

        This test directly catches missing typing imports (such as Optional)
        even in Python versions where deferred annotation evaluation is enabled.
        """
        import typing
        hints = typing.get_type_hints(executor.build_docker_run_cmd)
        assert "host_port" in hints
        assert "container_port" in hints
        assert "return" in hints

    @pytest.mark.asyncio
    async def test_start_container_with_real_port_allocator_integration(self, monkeypatch):
        """Test _start_container calling real port_allocator and build_docker_run_cmd without mocking them."""
        commands_run = []

        async def mock_run_command(cmd, timeout=300):
            commands_run.append(list(cmd))
            return {"stdout": "mock_real_cid_123", "stderr": "", "code": 0}

        monkeypatch.setattr(executor, "run_command", mock_run_command)

        # Clear allocator state, do NOT mock port_allocator methods
        executor.port_allocator.allocated.clear()

        step = Step(
            id="start_node",
            type="start_container",
            params={
                "name": "envman_node",
                "image": "node:20",
                "port": "3000:3000",
            },
        )

        result = await executor._start_container(step, network_name="envman_net_test", env_id="env_test")
        assert result["code"] == 0
        assert result["stdout"] == "mock_real_cid_123"
        # Verify docker run command was constructed properly
        run_cmd = [c for c in commands_run if "run" in c][0]
        assert "envman_node" in run_cmd
        assert "envman_net_test" in run_cmd
        assert "node:20" in run_cmd

