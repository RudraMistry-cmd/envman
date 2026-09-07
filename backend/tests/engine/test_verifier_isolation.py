"""Tier 1: Tests verifying verification isolation per environment.

Tests prove that:
1. verify_environment(env_id=...) queries ONLY containers belonging to that env_id via db.get_containers.
2. Even if state.container_registry has accumulated containers from other environments
   (e.g. node, mongo, postgres, python), verify_environment for redis ONLY checks redis.
3. State registry functions (store_container, get_container, dump_registry, clear_registry)
   properly support env_id scoping.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import app.engine.verifier as verifier
import app.engine.state as state


class TestVerifierEnvironmentIsolation:
    """Verify that verify_environment never inspects containers from other environments."""

    @pytest.mark.asyncio
    @patch("app.engine.verifier._verify_service")
    async def test_verify_environment_only_inspects_current_env_containers(self, mock_verify_service, monkeypatch, tmp_path):
        """When env_id is passed, verifier queries db.get_containers(env_id) and ignores all others."""
        import app.storage.db as db_mod

        # Use an isolated temporary sqlite DB
        test_db = str(tmp_path / "test_envman.db")
        monkeypatch.setattr(db_mod, "DB_PATH", test_db)
        db_mod.init_db()

        # Populate DB with containers from TWO environments
        # Environment A: only redis
        env_a = "env_a_redis_only"
        db_mod.save_environment(env_a, "envman_net_a")
        db_mod.save_container("cid_redis", env_a, "envman_redis", "redis:7", "running", host_port=6379)

        # Environment B: python, postgres, node, mongo
        env_b = "env_b_multi"
        db_mod.save_environment(env_b, "envman_net_b")
        db_mod.save_container("cid_python", env_b, "envman_python", "python:3.12", "running")
        db_mod.save_container("cid_postgres", env_b, "envman_postgres", "postgres:16", "running", host_port=5432)
        db_mod.save_container("cid_node", env_b, "envman_node", "node:20", "running")
        db_mod.save_container("cid_mongo", env_b, "envman_mongo", "mongo:7", "running", host_port=27017)

        # Contaminate the global in-memory registry with all 5 containers
        state.container_registry["start_python"] = "cid_python"
        state.container_registry["start_postgres"] = "cid_postgres"
        state.container_registry["start_node"] = "cid_node"
        state.container_registry["start_mongo"] = "cid_mongo"
        state.container_registry["start_redis"] = "cid_redis"

        # Mock _verify_service to return ready for any service
        mock_verify_service.side_effect = lambda name, image, port, container_name=None: {
            "service": name,
            "status": "ready",
            "checks": [],
            "host_port": port,
            "connection_string": None,
            "connection_type": None,
        }

        # Run verification for Environment A (Redis only)
        results = await verifier.verify_environment(env_id=env_a)

        # Assert: ONLY redis was inspected! None of python, postgres, node, mongo were touched.
        assert len(results) == 1
        assert results[0]["service"] == "redis"
        assert mock_verify_service.call_count == 1

        called_services = [call.args[0] for call in mock_verify_service.call_args_list]
        assert called_services == ["redis"]
        assert "python" not in called_services
        assert "postgres" not in called_services
        assert "node" not in called_services
        assert "mongo" not in called_services


class TestStateRegistryScoping:
    """Ensure state.py supports per-environment scoping."""

    def test_store_and_dump_scoped_by_env(self):
        state.clear_registry()

        state.store_container("start_redis", "cid_r1", env_id="env1", name="envman_redis", image="redis:7")
        state.store_container("start_postgres", "cid_p1", env_id="env2", name="envman_postgres", image="postgres:16")

        # dump_registry for env1 only returns redis
        env1_dump = state.dump_registry(env_id="env1")
        assert env1_dump == {"start_redis": "cid_r1"}

        # dump_registry for env2 only returns postgres
        env2_dump = state.dump_registry(env_id="env2")
        assert env2_dump == {"start_postgres": "cid_p1"}

        # get_container with env_id
        assert state.get_container("start_redis", env_id="env1") == "cid_r1"
        assert state.get_container("start_postgres", env_id="env1") is None
        assert state.get_container("start_postgres", env_id="env2") == "cid_p1"

        # clear_registry for env1 only removes env1
        state.clear_registry(env_id="env1")
        assert state.dump_registry(env_id="env1") == {}
        assert state.dump_registry(env_id="env2") == {"start_postgres": "cid_p1"}
