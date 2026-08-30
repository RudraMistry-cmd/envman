"""
State Manager
=============

WHEN Docker starts a container, it gives back a long ID like:
     a1b2c3d4e5f6...

We need to REMEMBER which container belongs to which step.
Otherwise, how do we know if "envman_pg" is the postgres container?

WHAT: A simple dictionary (like a phone book).
     Step ID → Container ID

HOW:
     When executor starts "envman_pg", it saves:
       store_container("start_pg", "a1b2c3d4...")

     When verifier needs to check postgres, it looks up:
       get_container("start_pg") → "a1b2c3d4..."

WHY THIS MATTERS:
     If we don't track containers, we can't verify them.
     If we can't verify them, we can't promise "it works."
"""

from typing import Dict, Optional
from app.storage import db
from app.utils.logger import get_logger

logger = get_logger("state")

container_registry: Dict[str, str] = {}


def store_container(step_id: str, container_id: str, env_id: str = None, name: str = None, image: str = None) -> None:
    """Save a container ID for a step.

    FIX #6: Includes persistence hook with error handling.
    """
    container_registry[step_id] = container_id
    logger.info("stored: step '%s' -> container '%s'", step_id, container_id[:12])

    # Persistence hook (FIX #6: with error handling)
    if env_id and name and image:
        try:
            db.save_container(container_id, env_id, name, image, "running")
        except Exception as e:
            logger.warning("Failed to persist container: %s", e)


def store_environment(env_id: str, network_name: str) -> None:
    """Persist environment record to SQLite.

    FIX #6: Includes error handling.
    """
    try:
        db.save_environment(env_id, network_name)
    except Exception as e:
        logger.warning("Failed to persist environment: %s", e)


def get_container(step_id: str) -> Optional[str]:
    """Look up which container a step created."""
    cid = container_registry.get(step_id)
    if cid:
        logger.debug("lookup: step '%s' -> container '%s'", step_id, cid[:12])
    else:
        logger.warning("lookup: step '%s' -> NOT FOUND", step_id)
    return cid


def dump_registry() -> Dict[str, str]:
    """Return a copy of all tracked containers (for debugging)."""
    logger.info("registry: %s", container_registry)
    return dict(container_registry)
