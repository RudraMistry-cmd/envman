"""
Storage Layer
=============

WHY: We need to PERSIST environment and container state.
     In-memory dicts are lost when the server restarts.
     SQLite gives us durable storage without external dependencies.

WHAT: Simple SQLite operations for environments and containers.
      Open → execute → close pattern. No ORM. No connection pooling.

HOW:
     1. init_db() creates tables if they don't exist
     2. save_environment() persists environment records
     3. save_container() persists container records
     4. get_environment() / get_containers() retrieve data

THINK OF IT LIKE:
     A filing cabinet.
     Each environment gets a folder (environments table).
     Each container gets a card in that folder (containers table).
"""

import sqlite3
import os
import subprocess
from datetime import datetime, timezone
from app.utils.logger import get_logger

logger = get_logger("storage")

# FIX #3: Explicit DB path relative to this file's directory
DB_PATH = os.path.join(os.path.dirname(__file__), "envman.db")


def init_db():
    """Create tables if they don't exist.

    WHY: First time running, there's no database.
         This ensures the schema exists before we try to use it.
    """
    logger.info("initializing database at %s", DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS environments (
            id TEXT PRIMARY KEY,
            network_name TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS containers (
            id TEXT PRIMARY KEY,
            environment_id TEXT,
            name TEXT,
            image TEXT,
            status TEXT,
            host_port INTEGER,
            connection_string TEXT
        )
    """)

    # Migrate pre-existing DBs: CREATE TABLE IF NOT EXISTS does NOT add
    # columns to an old 5-column table, which made every save_container fail
    # with "no column named host_port" (and silently orphaned containers on
    # delete). Idempotent: only adds what's missing.
    existing = {row[1] for row in cursor.execute("PRAGMA table_info(containers)").fetchall()}
    if "host_port" not in existing:
        cursor.execute("ALTER TABLE containers ADD COLUMN host_port INTEGER")
    if "connection_string" not in existing:
        cursor.execute("ALTER TABLE containers ADD COLUMN connection_string TEXT")

    # Migrate pre-existing DBs: add config_json column to environments table
    # if it doesn't already exist (idempotent, same pattern as containers).
    existing = {row[1] for row in cursor.execute("PRAGMA table_info(environments)").fetchall()}
    if "config_json" not in existing:
        cursor.execute("ALTER TABLE environments ADD COLUMN config_json TEXT")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            id TEXT PRIMARY KEY,
            name TEXT,
            environment_id TEXT,
            config_json TEXT,
            created_at TEXT
        )
    """)

    conn.commit()
    conn.close()
    logger.info("database initialized successfully")


def save_environment(env_id: str, network_name: str):
    """Persist an environment record.

    WHY: We need to remember which environments exist
         and which network they use.
    """
    logger.info("saving environment %s (network: %s)", env_id, network_name)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO environments (id, network_name, created_at) VALUES (?, ?, ?)",
        (env_id, network_name, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()


def save_environment_config(env_id: str, config_json: str):
    """Persist environment config as JSON.

    WHY: We need to persist the setup config so it can be exported/imported
         without requiring the user to re-specify services/versions.
    """
    logger.info("saving environment config for %s", env_id)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE environments SET config_json = ? WHERE id = ?",
        (config_json, env_id),
    )
    conn.commit()
    conn.close()


def get_environment_config(env_id: str):
    """Retrieve environment config JSON.

    Returns: config_json string or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT config_json FROM environments WHERE id = ?", (env_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def save_container(container_id: str, env_id: str, name: str, image: str, status: str,
                   host_port: int = None, connection_string: str = None):
    """Persist a container record.

    WHY: We need to track which containers belong to which environment
         for cleanup and verification.
    """
    logger.info("saving container %s (env: %s, name: %s)", container_id[:12], env_id, name)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO containers (id, environment_id, name, image, status, host_port, connection_string) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (container_id, env_id, name, image, status, host_port, connection_string)
    )
    conn.commit()
    conn.close()


def get_environment(env_id: str):
    """Retrieve an environment by ID.

    Returns: (id, network_name, created_at) or None
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM environments WHERE id = ?", (env_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def get_containers(env_id: str):
    """Retrieve all containers for an environment.

    Returns: list of (id, environment_id, name, image, status, host_port, connection_string) tuples
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM containers WHERE environment_id = ?", (env_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def _inspect_host_port(container_name: str):
    """Return the live HostPort int for a container, or None.

    WHY: The dashboard must show only real bindings. The db layer is sync,
    so this uses a short-timeout subprocess directly. ANY failure (docker
    down, no such container, no binding, unparsable output) returns None
    and never raises - a broken lookup must degrade to "unknown", not 500.
    """
    import json
    import subprocess

    try:
        result = subprocess.run(
            ["docker", "inspect", "--format", "{{json .NetworkSettings.Ports}}", container_name],
            capture_output=True, text=True, timeout=10,
        )
    except Exception:
        return None
    if result.returncode != 0 or not (result.stdout or "").strip():
        return None
    try:
        ports_json = json.loads(result.stdout.strip())
    except (ValueError, TypeError):
        return None
    try:
        for binding in ports_json.values():
            if isinstance(binding, list) and binding and "HostPort" in binding[0]:
                return int(binding[0]["HostPort"])
    except (ValueError, TypeError, AttributeError):
        return None
    return None


def get_all_environments():
    """Retrieve all environments with their container lists.

    Returns: list of dicts with keys:
        id, network_name, created_at, containers (list of dicts)
    """
    from app.engine.verifier import build_connection_info

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all environments
    cursor.execute("SELECT id, network_name, created_at FROM environments")
    env_rows = cursor.fetchall()

    environments = []
    for env_row in env_rows:
        env_id, network_name, created_at = env_row
        containers = get_containers(env_id)
        container_list = []
        for c in containers:
            # c = (id, environment_id, name, image, status) - older DBs have
            # exactly 5 columns; tolerate a 7-col shape if a migration added
            # stored host_port/connection_string columns.
            if len(c) >= 7:
                container_id, env_id_, name, image, status, stored_host_port, stored_connection_string = c[:7]
            else:
                container_id, env_id_, name, image, status = c[:5]
                stored_host_port, stored_connection_string = None, None

            # Derive service_id from container name (strip envman_ prefix)
            service_id = name.replace("envman_", "", 1) if name.startswith("envman_") else name

            # Resolve host_port: stored value first, else LIVE docker inspect.
            # Never substitute a registry default: no verified binding means
            # host_port None, and build_connection_info reports it honestly.
            host_port = stored_host_port
            if host_port is None:
                host_port = _inspect_host_port(name)

            # Build connection_info using host_port
            connection_info = build_connection_info(service_id, image, host_port)

            container_list.append({
                "id": container_id,
                "name": name,
                "image": image,
                "status": status,
                "host_port": connection_info["host_port"],
                "connection_string": connection_info["connection_string"],
                "connection_type": connection_info["connection_type"],
                # Preserve stored values for backward compatibility
                "_stored_host_port": stored_host_port,
                "_stored_connection_string": stored_connection_string,
            })

        # Derive overall environment status
        if not container_list:
            env_status = "not running"
        elif all(c["status"] == "stopped" for c in container_list):
            env_status = "stopped"
        elif all(c["status"] == "running" for c in container_list):
            env_status = "running"
        else:
            env_status = "partial"

        environments.append({
            "id": env_id,
            "network_name": network_name,
            "created_at": created_at,
            "containers": container_list,
            "status": env_status,
        })

    conn.close()
    return environments


def update_container_status(env_id: str, name: str, status: str):
    """Update a container's status in storage.

    WHY: We need to track container lifecycle state changes (e.g., stopped/started)
          so the dashboard reflects real state without re-querying Docker on every render.

    HOW: UPDATE containers SET status = ? WHERE environment_id = ? AND name = ?.
         Idempotent: safe to call even if status hasn't changed.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE containers SET status = ? WHERE environment_id = ? AND name = ?",
        (status, env_id, name),
    )
    conn.commit()
    conn.close()


def delete_environment(env_id: str):
    """Delete an environment: stop/remove containers, remove network, delete DB rows.

    WHY: Clean up all resources when user clicks Delete on the dashboard, or when
         setup fails mid-flight.

    HOW:
        1. Get all containers for this environment
        2. Stop and remove each container via Docker CLI (isolated per container)
        3. Remove the Docker network if not shared (isolated)
        4. Unconditionally delete all container and environment DB records in finally block
    """
    import subprocess

    containers = get_containers(env_id)
    env_row = get_environment(env_id)

    if not env_row:
        logger.warning("environment %s not found for deletion; cleaning any orphaned records", env_id)
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM containers WHERE environment_id = ?", (env_id,))
            cursor.execute("DELETE FROM environments WHERE id = ?", (env_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning("failed to purge db records for non-existent env %s: %s", env_id, e)
        return

    network_name = env_row[1]

    # Stop and remove each container individually without letting one failure abort cleanup
    for c in containers:
        container_name = c[2]
        try:
            result = subprocess.run(
                ["docker", "rm", "-f", container_name],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode != 0:
                logger.warning("failed to remove container %s: %s", container_name, result.stderr.strip())
        except Exception as e:
            logger.warning("exception while removing container %s: %s", container_name, e)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Only remove network if no other active environment in DB uses it
        cursor.execute("SELECT COUNT(*) FROM environments WHERE network_name = ? AND id != ?", (network_name, env_id))
        other_users = cursor.fetchone()[0]
        if other_users == 0:
            try:
                result = subprocess.run(
                    ["docker", "network", "rm", network_name],
                    capture_output=True, text=True, timeout=30,
                )
                if result.returncode != 0:
                    logger.warning("failed to remove network %s: %s", network_name, result.stderr.strip())
            except Exception as e:
                logger.warning("exception while removing network %s: %s", network_name, e)
        else:
            logger.info("network %s is still in use by %d other environment(s); skipping network removal", network_name, other_users)
    finally:
        # DB deletion must ALWAYS succeed regardless of Docker CLI outcome
        try:
            cursor.execute("DELETE FROM containers WHERE environment_id = ?", (env_id,))
            cursor.execute("DELETE FROM environments WHERE id = ?", (env_id,))
            conn.commit()
        finally:
            conn.close()

    try:
        from app.engine.state import clear_registry
        clear_registry(env_id)
    except Exception as e:
        logger.warning("failed to clear in-memory state for env %s: %s", env_id, e)

    logger.info("environment %s fully deleted", env_id)


def save_snapshot(snapshot_id: str, name: str, env_id: str, config_json: str):
    """Persist a snapshot record.

    WHY: TECHNICAL_SPEC.md Part 7 §4 requires saving environment snapshots
         so they can be restored later even after the original environment is deleted.
    """
    logger.info("saving snapshot %s ('%s') for env %s", snapshot_id, name, env_id)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO snapshots (id, name, environment_id, config_json, created_at) "
        "VALUES (?, ?, ?, ?, ?)",
        (snapshot_id, name, env_id, config_json, datetime.now(timezone.utc).isoformat())
    )
    conn.commit()
    conn.close()


def get_snapshot(snapshot_id: str):
    """Retrieve a snapshot by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, environment_id, config_json, created_at FROM snapshots WHERE id = ?", (snapshot_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "id": row[0],
        "name": row[1],
        "environment_id": row[2],
        "config_json": row[3],
        "created_at": row[4],
    }


def get_all_snapshots():
    """Retrieve all snapshots ordered by created_at DESC."""
    import json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, environment_id, config_json, created_at FROM snapshots ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    snapshots = []
    for r in rows:
        services = []
        try:
            cfg = json.loads(r[3])
            services = cfg.get("services", [])
        except Exception:
            pass
        snapshots.append({
            "id": r[0],
            "name": r[1],
            "environment_id": r[2],
            "created_at": r[4],
            "services": services,
        })
    return snapshots


def delete_snapshot(snapshot_id: str) -> bool:
    """Delete a snapshot by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM snapshots WHERE id = ?", (snapshot_id,))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


# Initialize database on module import
init_db()
