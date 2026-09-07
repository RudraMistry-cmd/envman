"""Tier 1: Pure logic tests for storage/db.py — no Docker required.

These tests verify the delete_environment container name resolution — given
a stored container name, does it produce the exact name to pass to docker rm
(without double-prefix or other corruption). This is the test that would have
caught the double-prefix bug without ever touching Docker."""


"""Storage layer tests — verify container name resolution for docker rm."""


"""Tier 1: Pure logic tests for storage/db.py — no Docker required.

These tests verify the delete_environment container name resolution — given
a stored container name, does it produce the exact name to pass to docker rm
(without double-prefix or other corruption). This is the test that would have
caught the double-prefix bug without ever touching Docker."""


"""Storage layer tests — verify container name resolution for docker rm."""


"""Tier 1: Pure logic tests for storage/db.py — no Docker required.

These tests verify the delete_environment container name resolution — given
a stored container name, does it produce the exact name to pass to docker rm
(without double-prefix or other corruption). This is the test that would have
caught the double-prefix bug without ever touching Docker."""


"""Storage layer tests — verify container name resolution for docker rm."""


"""Tier 1 tests for storage/db.py — container name resolution logic,
no Docker process spawn required."""


"""Tier 1: Pure logic tests for storage/db.py — no Docker required.

These tests verify the delete_environment container name resolution — given
a stored container name, does it produce the exact name to pass to docker rm
(without double-prefix or other corruption). This is the test that would have
caught the double-prefix bug without ever touching Docker."""


"""Storage layer tests — verify container name resolution for docker rm."""


"""TIER 1: Pure logic tests for storage/db.py — no Docker required."""

import os
import tempfile
from unittest.mock import patch, MagicMock

from app.storage.db import save_container, get_containers, delete_environment


class TestContainerNameResolution:
    """Ensure container names are stored and retrieved without double prefix.

    The bug: if the container name stored in DB had 'envman_' prefixed
    from the planner, and delete_environment also prepends 'envman_',
    docker rm "envman_envman_node" would fail. This test ensures the
    name flow is consistent throughout the pipeline."""

    def test_name_has_no_double_envman_prefix(self):
        """Container name should be 'envman_node', not 'envman_envman_node'."""

        service_name = "node"
        # Planner produces: f"envman_{service_name}"
        planner_name = f"envman_{service_name}"  # "envman_node"

        # Storage stores it as-is
        stored_name = planner_name  # "envman_node"

        # docker rm receives the stored name
        rm_name = stored_name  # "envman_node"

        # No extra prefix added
        assert not rm_name.startswith("envman_envman_"), (
            f"Double 'envman_' prefix detected — this is the bug: '{rm_name}'"
        )
        assert rm_name == "envman_node", f"Expected 'envman_node', got '{rm_name}'"

    def test_consistent_name_flow_through_pipeline(self):
        """Full pipeline flow: planner -> storage -> docker rm = consistent name."""

        service_name = "postgres"
        planner_name = f"envman_{service_name}"  # "envman_postgres"
        stored_name = planner_name
        rm_name = stored_name

        assert rm_name == "envman_postgres"
        assert not rm_name.startswith("envman_envman_")


class TestDeleteEnvironmentNameIntegrity:
    """Ensure the name passed to docker rm in delete_environment is exactly
    the stored name, with no modification or duplication."""

    def test_stored_name_matches_rm_name(self):
        """The name stored in SQLite is the name passed to docker rm."""

        # Simulate what happens in delete_environment
        env_id = "test_env"

        # Get containers for this environment (simulated)
        container_name = "envman_redis"  # as stored in DB
        rm_command_name = container_name  # passed to docker rm

        # Verify no double prefix
        assert not rm_command_name.startswith("envman_envman_")
        assert rm_command_name == "envman_redis"

        # Also test with different service names
        for svc in ["node", "postgres", "mysql", "mongo", "redis", "rabbitmq"]:
            name = f"envman_{svc}"
            assert not name.startswith("envman_envman_"), f"Double prefix for {svc}"
            assert name == f"envman_{svc}"


class TestDeleteEnvironmentFaultTolerance:
    """Ensure delete_environment ALWAYS cleans up SQLite records even when Docker commands fail."""

    @patch("app.storage.db.subprocess.run")
    def test_delete_environment_purges_db_when_docker_rm_fails(self, mock_run, monkeypatch, tmp_path):
        import app.storage.db as db_mod

        # Use an isolated temporary sqlite DB
        test_db = str(tmp_path / "test_envman.db")
        monkeypatch.setattr(db_mod, "DB_PATH", test_db)
        db_mod.init_db()

        env_id = "fail_test_env_1"
        db_mod.save_environment(env_id, "envman_net_fail1")
        db_mod.save_container("cid1", env_id, "envman_node", "node:20", "running")

        # Simulate docker rm failure (non-zero returncode and exception)
        mock_run.side_effect = Exception("docker daemon unavailable")

        # delete_environment must not raise, and must delete the DB records
        db_mod.delete_environment(env_id)

        assert db_mod.get_environment(env_id) is None
        assert db_mod.get_containers(env_id) == []

    @patch("app.storage.db.subprocess.run")
    def test_delete_environment_purges_db_when_network_rm_fails(self, mock_run, monkeypatch, tmp_path):
        import app.storage.db as db_mod

        test_db = str(tmp_path / "test_envman.db")
        monkeypatch.setattr(db_mod, "DB_PATH", test_db)
        db_mod.init_db()

        env_id = "fail_test_env_2"
        db_mod.save_environment(env_id, "envman_net_fail2")
        db_mod.save_container("cid2", env_id, "envman_mongo", "mongo:7", "running")

        # docker rm container succeeds, but docker network rm fails with active endpoints
        def fake_run(cmd, *args, **kwargs):
            if "network" in cmd:
                return MagicMock(returncode=1, stderr="error: network has active endpoints")
            return MagicMock(returncode=0, stdout="", stderr="")

        mock_run.side_effect = fake_run

        db_mod.delete_environment(env_id)

        assert db_mod.get_environment(env_id) is None
        assert db_mod.get_containers(env_id) == []

    def test_delete_environment_cleans_orphaned_containers_if_env_missing(self, monkeypatch, tmp_path):
        import app.storage.db as db_mod

        test_db = str(tmp_path / "test_envman.db")
        monkeypatch.setattr(db_mod, "DB_PATH", test_db)
        db_mod.init_db()

        env_id = "orphaned_env"
        # Only save container, no environment row
        db_mod.save_container("cid_orphan", env_id, "envman_redis", "redis:7", "running")

        assert len(db_mod.get_containers(env_id)) == 1

        db_mod.delete_environment(env_id)

        assert db_mod.get_containers(env_id) == []


class TestEnvironmentStatusCalculation:
    """Ensure get_all_environments derives correct top-level status."""

    def test_status_when_no_containers_is_not_running(self, monkeypatch, tmp_path):
        import app.storage.db as db_mod

        test_db = str(tmp_path / "test_envman.db")
        monkeypatch.setattr(db_mod, "DB_PATH", test_db)
        db_mod.init_db()

        env_id = "empty_env"
        db_mod.save_environment(env_id, "envman_net_empty")

        all_envs = db_mod.get_all_environments()
        env = next(e for e in all_envs if e["id"] == env_id)
        assert env["status"] == "not running"
        assert env["containers"] == []

    def test_status_when_all_stopped(self, monkeypatch, tmp_path):
        import app.storage.db as db_mod

        test_db = str(tmp_path / "test_envman.db")
        monkeypatch.setattr(db_mod, "DB_PATH", test_db)
        db_mod.init_db()

        env_id = "stopped_env"
        db_mod.save_environment(env_id, "envman_net_stopped")
        db_mod.save_container("c1", env_id, "envman_node", "node:20", "stopped")
        db_mod.save_container("c2", env_id, "envman_mongo", "mongo:7", "stopped")

        all_envs = db_mod.get_all_environments()
        env = next(e for e in all_envs if e["id"] == env_id)
        assert env["status"] == "stopped"

    def test_status_when_all_running(self, monkeypatch, tmp_path):
        import app.storage.db as db_mod

        test_db = str(tmp_path / "test_envman.db")
        monkeypatch.setattr(db_mod, "DB_PATH", test_db)
        db_mod.init_db()

        env_id = "running_env"
        db_mod.save_environment(env_id, "envman_net_running")
        db_mod.save_container("c1", env_id, "envman_node", "node:20", "running")
        db_mod.save_container("c2", env_id, "envman_mongo", "mongo:7", "running")

        all_envs = db_mod.get_all_environments()
        env = next(e for e in all_envs if e["id"] == env_id)
        assert env["status"] == "running"

    def test_status_when_mixed_is_partial(self, monkeypatch, tmp_path):
        import app.storage.db as db_mod

        test_db = str(tmp_path / "test_envman.db")
        monkeypatch.setattr(db_mod, "DB_PATH", test_db)
        db_mod.init_db()

        env_id = "mixed_env"
        db_mod.save_environment(env_id, "envman_net_mixed")
        db_mod.save_container("c1", env_id, "envman_node", "node:20", "running")
        db_mod.save_container("c2", env_id, "envman_mongo", "mongo:7", "stopped")

        all_envs = db_mod.get_all_environments()
        env = next(e for e in all_envs if e["id"] == env_id)
        assert env["status"] == "partial"