"""Tier 1: startup command threading (ServiceSpec -> planner -> executor).

Images like minio/minio REQUIRE a command after the image name; without one
they print help and exit. These tests prove the command flows end-to-end
without needing Docker.
"""

import pytest
from unittest.mock import AsyncMock

from app.models.environment import EnvironmentConfig, ServiceSpec
from app.models.step import Step


class TestServiceSpecCommandField:
    def test_command_defaults_none(self):
        assert ServiceSpec(name="node", image="node:20").command is None

    def test_command_accepts_list(self):
        spec = ServiceSpec(
            name="minio", image="minio/minio:latest",
            command=["server", "/data", "--console-address", ":9001"],
        )
        assert spec.command == ["server", "/data", "--console-address", ":9001"]

    def test_registry_minio_default_command(self):
        from app.registry.services import get_service_by_image
        svc = get_service_by_image("minio/minio:latest")
        assert svc is not None
        assert svc.default_command == ["server", "/data", "--console-address", ":9001"]

    def test_registry_others_have_no_default_command(self):
        from app.registry.services import get_all_services
        for svc in get_all_services():
            if svc.id in ("minio", "typesense"):
                continue
            assert svc.default_command is None, f"{svc.id} unexpectedly has a command"


class TestPlannerThreadsCommand:
    @pytest.mark.asyncio
    async def test_registry_default_command_reaches_step_params(self, monkeypatch):
        import app.engine.planner as planner

        monkeypatch.setattr(
            planner, "image_exists", AsyncMock(return_value=True)
        )
        config = EnvironmentConfig(
            services=[ServiceSpec(name="minio", image="minio/minio:latest")]
        )
        plan = await planner.plan_environment(config)
        start = [s for s in plan.steps if s.type == "start_container"][0]
        assert start.params["command"] == ["server", "/data", "--console-address", ":9001"]

    @pytest.mark.asyncio
    async def test_explicit_service_command_wins(self, monkeypatch):
        import app.engine.planner as planner

        monkeypatch.setattr(
            planner, "image_exists", AsyncMock(return_value=True)
        )
        config = EnvironmentConfig(
            services=[ServiceSpec(
                name="minio", image="minio/minio:latest",
                command=["server", "/custom"],
            )]
        )
        plan = await planner.plan_environment(config)
        start = [s for s in plan.steps if s.type == "start_container"][0]
        assert start.params["command"] == ["server", "/custom"]

    @pytest.mark.asyncio
    async def test_no_command_means_no_param(self, monkeypatch):
        import app.engine.planner as planner

        monkeypatch.setattr(
            planner, "image_exists", AsyncMock(return_value=True)
        )
        config = EnvironmentConfig(
            services=[ServiceSpec(name="node", image="node:20")]
        )
        plan = await planner.plan_environment(config)
        start = [s for s in plan.steps if s.type == "start_container"][0]
        assert "command" not in start.params


class TestExecutorAppendsCommandAfterImage:
    @pytest.mark.asyncio
    async def test_command_appended_after_image(self, monkeypatch):
        import app.engine.executor as executor

        seen = {}

        async def fake_run(cmd, timeout=300):
            seen["cmd"] = cmd
            return {"stdout": "cid123", "stderr": "", "code": 0}

        monkeypatch.setattr(executor, "run_command", fake_run)
        monkeypatch.setattr(executor, "store_container", lambda *a, **k: None)

        step = Step(
            id="start_minio", type="start_container",
            params={
                "image": "minio/minio:latest",
                "name": "envman_minio",
                "command": ["server", "/data", "--console-address", ":9001"],
            },
        )
        result = await executor._start_container(step, "envman_net")
        assert result["code"] == 0
        cmd = seen["cmd"]
        assert cmd[-4:] == ["server", "/data", "--console-address", ":9001"]
        assert cmd.index("minio/minio:latest") < cmd.index("server")

    @pytest.mark.asyncio
    async def test_no_command_leaves_image_last(self, monkeypatch):
        import app.engine.executor as executor

        seen = {}

        async def fake_run(cmd, timeout=300):
            seen["cmd"] = cmd
            return {"stdout": "cid123", "stderr": "", "code": 0}

        monkeypatch.setattr(executor, "run_command", fake_run)
        monkeypatch.setattr(executor, "store_container", lambda *a, **k: None)

        step = Step(
            id="start_node", type="start_container",
            params={"image": "node:20", "name": "envman_node"},
        )
        await executor._start_container(step, "envman_net")
        assert seen["cmd"][-1] == "node:20"
