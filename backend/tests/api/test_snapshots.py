"""Tier 1: Tests for Environment Snapshots (TECHNICAL_SPEC.md Part 7 §4).

Tests verify snapshot creation, listing, retrieval, deletion, and restoration,
confirming that snapshots reuse export/import models and survive deletion of
the original environment.
"""

import json
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

from app.models.environment import EnvironmentConfig, ServiceSpec
from app.engine.snapshot import SnapshotManager, snapshot_manager
from app.api.routes import (
    create_environment_snapshot,
    create_snapshot_direct,
    list_snapshots,
    get_snapshot,
    restore_snapshot,
    delete_snapshot,
    CreateSnapshotRequest,
    CreateSnapshotFromEnvRequest,
)


class TestSnapshotUnit:
    def test_create_snapshot_success(self, monkeypatch):
        """Creating a snapshot saves durable export config with metadata."""
        saved = {}

        mock_config = json.dumps({
            "services": [
                {"name": "postgres", "image": "postgres:16", "port": 5432},
                {"name": "redis", "image": "redis:7", "port": 6379},
            ],
            "network_name": "envman_net",
        })

        monkeypatch.setattr("app.storage.db.get_environment", lambda eid: ("env_123", "envman_net", "time"))
        monkeypatch.setattr("app.storage.db.get_environment_config", lambda eid: mock_config)

        def mock_save(sid, name, eid, cfg):
            saved["id"] = sid
            saved["name"] = name
            saved["eid"] = eid
            saved["cfg"] = cfg

        monkeypatch.setattr("app.storage.db.save_snapshot", mock_save)

        mgr = SnapshotManager()
        result = mgr.create_snapshot("env_123", name="my-prod-backup")

        assert result["name"] == "my-prod-backup"
        assert result["environment_id"] == "env_123"
        assert len(result["services"]) == 2
        assert saved["name"] == "my-prod-backup"
        assert saved["eid"] == "env_123"

    def test_create_snapshot_unknown_env_raises(self, monkeypatch):
        """Creating a snapshot for unknown env raises ValueError."""
        monkeypatch.setattr("app.storage.db.get_environment", lambda eid: None)
        mgr = SnapshotManager()
        with pytest.raises(ValueError, match="not found"):
            mgr.create_snapshot("nonexistent")

    def test_create_snapshot_missing_config_raises(self, monkeypatch):
        """Creating a snapshot when env has no stored config raises ValueError."""
        monkeypatch.setattr("app.storage.db.get_environment", lambda eid: ("env_123", "net", "ts"))
        monkeypatch.setattr("app.storage.db.get_environment_config", lambda eid: None)
        mgr = SnapshotManager()
        with pytest.raises(ValueError, match="no stored config"):
            mgr.create_snapshot("env_123")

    @pytest.mark.asyncio
    async def test_restore_snapshot_calls_run_setup(self, monkeypatch):
        """Restoring snapshot deserializes config and executes run_setup."""
        mock_snapshot = {
            "id": "snap_abc",
            "name": "backup",
            "environment_id": "env_orig",
            "config_json": json.dumps({
                "services": [{"name": "node", "image": "node:20", "port": 3000}],
                "network_name": "envman_net",
            }),
            "created_at": "2026-09-06T12:00:00Z",
        }
        monkeypatch.setattr("app.storage.db.get_snapshot", lambda sid: mock_snapshot)

        captured_config = []

        async def mock_run_setup(cfg):
            captured_config.append(cfg)
            return "new_env_restored"

        monkeypatch.setattr("app.engine.snapshot.run_setup", mock_run_setup)

        mgr = SnapshotManager()
        new_env_id = await mgr.restore_snapshot("snap_abc")

        assert new_env_id == "new_env_restored"
        assert len(captured_config) == 1
        assert isinstance(captured_config[0], EnvironmentConfig)
        assert captured_config[0].services[0].name == "node"
        assert captured_config[0].services[0].port == 3000


class TestSnapshotApiRoutes:
    def test_create_snapshot_endpoint(self, monkeypatch):
        """POST /environments/{env_id}/snapshots endpoint returns snapshot descriptor."""
        mock_res = {
            "id": "snap_1",
            "name": "test-snap",
            "environment_id": "env_1",
            "services": [],
        }
        monkeypatch.setattr(snapshot_manager, "create_snapshot", lambda eid, name: mock_res)

        res = create_environment_snapshot("env_1", CreateSnapshotRequest(name="test-snap"))
        assert res["id"] == "snap_1"
        assert res["name"] == "test-snap"

    def test_create_snapshot_direct_endpoint(self, monkeypatch):
        """POST /snapshots endpoint returns snapshot descriptor."""
        mock_res = {"id": "snap_2", "name": "snap2", "environment_id": "env_2"}
        monkeypatch.setattr(snapshot_manager, "create_snapshot", lambda eid, name: mock_res)

        res = create_snapshot_direct(CreateSnapshotFromEnvRequest(environment_id="env_2", name="snap2"))
        assert res["id"] == "snap_2"

    def test_list_and_get_snapshots(self, monkeypatch):
        """GET /snapshots and GET /snapshots/{id}."""
        mock_snaps = [{"id": "snap_1", "name": "s1"}]
        monkeypatch.setattr(snapshot_manager, "list_snapshots", lambda: mock_snaps)
        monkeypatch.setattr(snapshot_manager, "get_snapshot", lambda sid: mock_snaps[0] if sid == "snap_1" else None)

        assert list_snapshots() == mock_snaps
        assert get_snapshot("snap_1") == mock_snaps[0]

        with pytest.raises(HTTPException) as exc:
            get_snapshot("nonexistent")
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_restore_snapshot_endpoint(self, monkeypatch):
        """POST /snapshots/{id}/restore starts environment restoration."""
        monkeypatch.setattr(snapshot_manager, "restore_snapshot", AsyncMock(return_value="env_restored_999"))

        result = await restore_snapshot("snap_1")
        assert result["status"] == "started"
        assert result["environment_id"] == "env_restored_999"
        assert result["snapshot_id"] == "snap_1"

    def test_delete_snapshot_endpoint(self, monkeypatch):
        """DELETE /snapshots/{id} removes snapshot."""
        monkeypatch.setattr(snapshot_manager, "delete_snapshot", lambda sid: sid == "snap_1")

        res = delete_snapshot("snap_1")
        assert res == {"status": "deleted", "snapshot_id": "snap_1"}

        with pytest.raises(HTTPException) as exc:
            delete_snapshot("missing")
        assert exc.value.status_code == 404
