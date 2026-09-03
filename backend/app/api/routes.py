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

from fastapi import APIRouter
from app.engine.coordinator import run_setup
from app.models.environment import EnvironmentConfig
from app.registry.services import get_all_services
from app.storage.db import get_all_environments, save_environment, delete_environment
from app.utils.logger import get_logger

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
