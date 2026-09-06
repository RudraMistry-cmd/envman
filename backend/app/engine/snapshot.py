"""
Snapshot Manager
================

WHY: Developers need to checkpoint their working environments, share them, or
     restore them after teardown.
     TECHNICAL_SPEC.md Part 7 §4 specifies environment snapshots.

WHAT: Save and restore entire environment state by reusing the existing export/import
      logic: a snapshot is a named, durably stored export persisted in SQLite.
"""

import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.models.environment import EnvironmentConfig
from app.engine.coordinator import run_setup
from app.storage import db
from app.utils.logger import get_logger

logger = get_logger("snapshot")


class SnapshotManager:
    """Save and restore entire environment state (TECHNICAL_SPEC.md Part 7 §4)."""

    def create_snapshot(self, env_id: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Save current environment state by reusing export configuration.

        A snapshot is a named, durably stored export that survives deletion of the
        original environment.
        """
        env_row = db.get_environment(env_id)
        if not env_row:
            raise ValueError(f"environment '{env_id}' not found")

        config_json = db.get_environment_config(env_id)
        if not config_json:
            raise ValueError(f"no stored config for environment '{env_id}'")

        snapshot_id = f"snapshot_{uuid.uuid4().hex[:8]}"
        snapshot_name = name.strip() if (name and name.strip()) else f"snapshot_{env_id[:8]}"

        db.save_snapshot(snapshot_id, snapshot_name, env_id, config_json)

        parsed_config = json.loads(config_json)
        logger.info("created snapshot %s ('%s') for env %s", snapshot_id, snapshot_name, env_id)

        return {
            "id": snapshot_id,
            "name": snapshot_name,
            "environment_id": env_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "config": parsed_config,
            "services": parsed_config.get("services", []),
        }

    async def restore_snapshot(self, snapshot_id: str) -> str:
        """Restore environment from a saved snapshot by reusing import / run_setup."""
        snap = db.get_snapshot(snapshot_id)
        if not snap:
            raise ValueError(f"snapshot '{snapshot_id}' not found")

        config_dict = json.loads(snap["config_json"])
        config = EnvironmentConfig(**config_dict)

        logger.info("restoring snapshot %s ('%s')", snapshot_id, snap["name"])
        new_env_id = await run_setup(config)
        logger.info("snapshot %s restored into new environment %s", snapshot_id, new_env_id)
        return new_env_id

    def list_snapshots(self) -> List[Dict[str, Any]]:
        """Return all saved snapshots."""
        return db.get_all_snapshots()

    def get_snapshot(self, snapshot_id: str) -> Optional[Dict[str, Any]]:
        """Get details of a single snapshot."""
        snap = db.get_snapshot(snapshot_id)
        if not snap:
            return None
        parsed = json.loads(snap["config_json"])
        return {
            "id": snap["id"],
            "name": snap["name"],
            "environment_id": snap["environment_id"],
            "created_at": snap["created_at"],
            "config": parsed,
            "services": parsed.get("services", []),
        }

    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete a saved snapshot."""
        return db.delete_snapshot(snapshot_id)


# Global singleton instance for snapshot management
snapshot_manager = SnapshotManager()
