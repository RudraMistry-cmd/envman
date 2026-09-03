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
            status TEXT
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


def save_container(container_id: str, env_id: str, name: str, image: str, status: str):
    """Persist a container record.

    WHY: We need to track which containers belong to which environment
         for cleanup and verification.
    """
    logger.info("saving container %s (env: %s, name: %s)", container_id[:12], env_id, name)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO containers (id, environment_id, name, image, status) VALUES (?, ?, ?, ?, ?)",
        (container_id, env_id, name, image, status)
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

    Returns: list of (id, environment_id, name, image, status) tuples
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM containers WHERE environment_id = ?", (env_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_environments():
    """Retrieve all environments with their container lists.

    Returns: list of dicts with keys:
        id, network_name, created_at, containers (list of dicts)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all environments
    cursor.execute("SELECT id, network_name, created_at FROM environments")
    env_rows = cursor.fetchall()

    environments = []
    for env_row in env_rows:
        env_id, network_name, created_at = env_row
        containers = get_containers(env_id)
        container_list = [
            {"id": c[0], "name": c[2], "image": c[3], "status": c[4]}
            for c in containers
        ]
        environments.append({
            "id": env_id,
            "network_name": network_name,
            "created_at": created_at,
            "containers": container_list,
        })

    conn.close()
    return environments


def delete_environment(env_id: str):
    """Delete an environment: stop/remove containers, remove network, delete DB rows.

    WHY: Clean up all resources when user clicks Delete on the dashboard.

    HOW:
        1. Get all containers for this environment
        2. Stop and remove each container via Docker CLI
        3. Remove the Docker network
        4. Delete all container records from DB
        5. Delete the environment record from DB
    """
    import subprocess

    containers = get_containers(env_id)
    env_row = get_environment(env_id)

    if not env_row:
        logger.warning("environment %s not found for deletion", env_id)
        return

    network_name = env_row[1]

    for c in containers:
        container_name = f"envman_{c[2]}"
        subprocess.run(
            ["docker", "rm", "-f", container_name],
            capture_output=True, text=True, timeout=30,
        )

    subprocess.run(
        ["docker", "network", "remove", network_name],
        capture_output=True, text=True, timeout=30,
    )

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM containers WHERE environment_id = ?", (env_id,))
    cursor.execute("DELETE FROM environments WHERE id = ?", (env_id,))
    conn.commit()
    conn.close()

    logger.info("environment %s fully deleted", env_id)


# Initialize database on module import
init_db()
