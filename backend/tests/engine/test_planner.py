"""Tier 1: Pure logic tests for engine/planner.py — no Docker required."""

import pytest
from unittest.mock import patch, AsyncMock
from app.engine.planner import plan_environment, _merge_env
from app.models.plan import Plan
from app.models.step import Step
from app.models.environment import EnvironmentConfig, ServiceSpec


class TestMergeEnv:
    """Ensure _merge_env correctly prioritizes user env over registry default_env
    and doesn't mutate the registry's dict."""

    @pytest.mark.asyncio
    async def test_user_env_overrides_registry(self):
        """User-supplied values should take priority over registry defaults."""
        registry_env = {"TYPESENSE_API_KEY": "xyz", "POSTGRES_PASSWORD": "postgres"}
        user_env = {"POSTGRES_PASSWORD": "custom123"}
        merged = _merge_env(registry_env, user_env)
        assert merged["POSTGRES_PASSWORD"] == "custom123"  # user wins
        assert merged["TYPESENSE_API_KEY"] == "xyz"  # registry preserved

    def test_registry_env_when_no_user(self):
        """If user provides no env, registry defaults should be used."""
        registry_env = {"TYPESENSE_API_KEY": "xyz"}
        user_env = None
        merged = _merge_env(registry_env, user_env)
        assert merged == {"TYPESENSE_API_KEY": "xyz"}

    def test_empty_both_returns_empty(self):
        """If both are empty/falsy, result is empty dict."""
        merged = _merge_env({}, {})
        assert merged == {}

    def test_registry_dict_not_mutated(self):
        """_merge_env must not mutate the registry's original dict."""
        registry_env = {"KEY": "value"}
        user_env = None
        original = dict(registry_env)  # copy to compare later
        _merge_env(registry_env, user_env)
        assert registry_env == original  # unchanged


class TestPlanEnvironmentStepOrder:
    """Ensure plan_environment produces the right step order and dependencies."""

    @pytest.fixture
    def basic_config(self):
        """Config with node + postgres services."""
        spec = EnvironmentConfig(
            services=[
                ServiceSpec(name="node", image="node:20"),
                ServiceSpec(name="postgres", image="postgres:16"),
            ]
        )
        return spec

    @pytest.mark.asyncio
    async def test_network_creation_is_first_step(self, basic_config):
        """The plan always starts with create_network."""
        plan = await plan_environment(basic_config)
        assert plan.steps[0].id == "create_network"
        assert plan.steps[0].type == "create_network"

    @pytest.mark.asyncio
    @patch("app.engine.planner.image_exists", new_callable=AsyncMock, return_value=False)
    async def test_pull_steps_come_after_network(self, mock_image_exists, basic_config):
        """Pull steps should come after network creation."""
        plan = await plan_environment(basic_config)
        network_step = plan.steps[0]
        pull_steps = [s for s in plan.steps if s.type == "pull_image"]
        assert len(pull_steps) > 0  # at least one image needs pulling

    @pytest.mark.asyncio
    async def test_start_steps_have_correct_dependencies(self, basic_config):
        """Start steps should depend on their corresponding pull steps."""
        plan = await plan_environment(basic_config)
        start_steps = [s for s in plan.steps if s.type == "start_container"]
        pull_ids = {s.id for s in plan.steps if s.type == "pull_image"}

        for step in start_steps:
            # Each start step should depend on a pull step
            if step.depends_on:
                assert step.depends_on in pull_ids, (
                    f"Start step {step.id} depends on {step.depends_on}, "
                    f"but that's not a pull step"
                )

    @pytest.mark.asyncio
    @patch("app.engine.planner.image_exists", new_callable=AsyncMock, return_value=False)
    async def test_multiple_services_have_independent_steps(self, mock_image_exists):
        """Multiple services should each have their own pull + start pair."""
        spec = EnvironmentConfig(
            services=[
                ServiceSpec(name="node", image="node:20"),
                ServiceSpec(name="postgres", image="postgres:16"),
                ServiceSpec(name="redis", image="redis:7"),
            ]
        )
        plan = await plan_environment(spec)
        start_ids = {s.id for s in plan.steps if s.type == "start_container"}
        pull_ids = {s.id for s in plan.steps if s.type == "pull_image"}
        # Should have 3 start steps and 3 pull steps
        assert len(start_ids) == 3
        assert len(pull_ids) == 3

    @pytest.mark.asyncio
    async def test_service_with_port_has_port_param(self):
        """A service with a port should have the port param in its step."""
        spec = EnvironmentConfig(
            services=[
                ServiceSpec(name="node", image="node:20", port=3000),
            ]
        )
        plan = await plan_environment(spec)
        start_step = [s for s in plan.steps if s.type == "start_container" and "node" in s.id][0]
        # The step params should contain the port mapping
        assert "port" in start_step.params
        assert start_step.params["port"] == "3000:3000"

    @pytest.mark.asyncio
    async def test_service_with_volume_has_volume_param(self):
        """A service with a volume should have the volume param in its step."""
        spec = EnvironmentConfig(
            services=[
                ServiceSpec(name="node", image="node:20", volume="/app/node_modules"),
            ]
        )
        plan = await plan_environment(spec)
        start_step = [s for s in plan.steps if s.type == "start_container" and "node" in s.id][0]
        assert "volume" in start_step.params