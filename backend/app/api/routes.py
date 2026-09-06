"""
API Routes
==========

WHY: The frontend needs a way to TALK to the backend.
     Two ways:
       1. POST /setup   → "Please start building my environment"
       2. WS   /ws      → "Tell me what's happening in real time"

WHAT:
     POST /setup:
       - Receives: { "node": "20", "postgres": "16" }
       - Starts the setup in the background
       - Returns: { "status": "started" }

     GET /health:
       - Returns { "status": "ok" } if the server is alive

     WS /ws:
       - WebSocket connection for live events
       - Server sends: step_started, step_done, step_failed, done
"""

from fastapi import APIRouter, HTTPException
from app.engine.coordinator import run_setup
from app.models.environment import EnvironmentConfig
from app.registry.services import get_all_services
from app.registry.templates import get_all_templates
from app.storage.db import (
    get_all_environments,
    get_containers,
    save_environment,
    delete_environment,
)
from app.utils.logger import get_logger
import subprocess

logger = get_logger("routes")

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint. Load balancers use this."""
    return {"status": "ok"}


@router.get("/registry/services")
def list_services():
    """
    WHY:
    Frontend needs to know which services are available.

    WHAT:
    Returns the full service registry.

    HOW:
    Directly serializes ServiceDefinition objects.

    THINK OF IT LIKE:
    An API endpoint exposing EnvMan's supported ecosystem.
    """
    return get_all_services()


@router.get("/templates")
def list_templates():
    """
    WHY:
    The frontend template picker needs the pinned {id, version} sets.

    WHAT:
    Returns the mern + python-web definitions. Every service id here
    exists in the service registry; versions match the picker options.
    """
    return get_all_templates()


@router.get("/environments")
def list_environments():
    """Return all environments with their service lists and status."""
    environments = get_all_environments()
    return environments


@router.delete("/environments/{env_id}")
def delete_env(env_id: str):
    """Stop and remove all containers, the network, and DB records for an environment."""
    delete_environment(env_id)
    return {"status": "deleted", "environment_id": env_id}


@router.get("/environments/{env_id}/containers/{container_name}/logs")
def container_logs(env_id: str, container_name: str, tail: int = 200):
    """Fetch recent logs for one container, fetch-on-demand (no streaming).

    SECURITY: container_name must belong to env_id per the stored records -
    anything else is rejected with 404 and never reaches the docker CLI.
    Missing/stopped containers yield available=false, not a raw error.
    """

    tail = max(1, min(int(tail), 1000))
    try:
        allowed = {row[2] for row in get_containers(env_id)}
    except Exception as e:  # noqa: BLE001 - unknown env degrades gracefully
        logger.warning("log fetch for unknown env %s: %s", env_id, e)
        raise HTTPException(status_code=404, detail="environment not found")
    if container_name not in allowed:
        raise HTTPException(
            status_code=404,
            detail=f"container '{container_name}' not part of environment",
        )
    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", str(tail), container_name],
            capture_output=True, text=True, timeout=15,
        )
    except Exception as e:  # noqa: BLE001 - docker down/timeout
        logger.warning("log fetch failed for '%s': %s", container_name, e)
        return {"container": container_name, "logs": "",
                "available": False, "detail": "log fetch failed"}
    output = (result.stdout or "") + (result.stderr or "")
    if result.returncode != 0:
        return {"container": container_name, "logs": "",
                "available": False, "detail": "no logs available"}
    return {"container": container_name, "logs": output.strip(),
            "available": True}


@router.post("/setup")
async def setup_env(config: EnvironmentConfig):
    """Start building the environment.

    This returns IMMEDIATELY. The actual work happens in the background.
     The frontend listens to WebSocket events for progress updates.

    WHY not wait? Because setup takes 30-60 seconds.
     We don't want the HTTP request to hang that long.
     Instead, we start the work and tell the frontend to watch WebSocket.
    """
    service_names = [s.name for s in config.services]
    logger.info("setup requested: services=%s", service_names)

    # Run setup in the background (doesn't block the response)
    env_id = await run_setup(config)

    return {"status": "started", "environment_id": env_id}
