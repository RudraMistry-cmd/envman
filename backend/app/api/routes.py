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

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.engine.coordinator import run_setup
from app.engine.snapshot import snapshot_manager
from app.models.environment import EnvironmentConfig
from app.registry.services import get_all_services
from app.registry.templates import get_all_templates
from app.storage.db import (
    get_all_environments,
    get_containers,
    get_environment,
    get_environment_config,
    save_environment,
    delete_environment,
    update_container_status,
)
from app.engine.verifier import verify_environment
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


@router.post("/environments/{env_id}/stop")
def stop_environment(env_id: str):
    """Stop all containers for an environment.

    WHY: Allow user to stop an entire environment (e.g., save resources)
         without removing containers and their data.

    HOW:
        1. Get all containers for this environment via get_containers()
        2. For each container, run `docker stop <name>` (list-based, never shell=True)
        3. Update stored status to 'stopped' via update_container_status
        4. Return per-container results

    SECURITY: Unknown environments return 404; docker CLI is never invoked
              for envs that don't exist.
    """
    # Verify environment exists by fetching its containers
    # Raises exception for unknown envs (degrades gracefully)
    try:
        containers = get_containers(env_id)
    except Exception as e:  # noqa: BLE001 - unknown env degrades gracefully
        logger.warning("stop failed for unknown env %s: %s", env_id, e)
        raise HTTPException(status_code=404, detail="environment not found")
    if not containers:
        raise HTTPException(status_code=404, detail="environment not found")

    results = []
    for c in containers:
        # c = (id, environment_id, name, image, status, host_port, connection_string)
        container_name = c[2]
        result = subprocess.run(
            ["docker", "stop", container_name],
            capture_output=True, text=True, timeout=30,
        )
        # Update stored status to 'stopped' only if docker stop succeeded
        if result.returncode == 0:
            update_container_status(env_id, container_name, "stopped")
        results.append({
            "container": container_name,
            "docker_result": {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "code": result.returncode,
            }
        })

    return {"environment_id": env_id, "status": "stopped", "results": results}


@router.post("/environments/{env_id}/start")
async def start_environment(env_id: str):
    """Start all stored containers for an environment and re-run verifier.

    WHY: Allow user to restart an environment that was previously stopped,
          restoring services and verifying they're ready.

    HOW:
        1. Get all containers for this environment via get_containers()
        2. For each container, run `docker start <name>` (list-based, never shell=True)
        3. Update stored status
        4. Re-run verifier the same way fresh setup does
        5. Return verification results

    SECURITY: Unknown environments return 404; docker CLI is never invoked
              for envs that don't exist.
    """
    # Verify environment exists by fetching its containers
    # Raises exception for unknown envs (degrades gracefully)
    try:
        containers = get_containers(env_id)
    except Exception as e:  # noqa: BLE001 - unknown env degrades gracefully
        logger.warning("start failed for unknown env %s: %s", env_id, e)
        raise HTTPException(status_code=404, detail="environment not found")
    if not containers:
        raise HTTPException(status_code=404, detail="environment not found")

    results = []
    for c in containers:
        # c = (id, environment_id, name, image, status, host_port, connection_string)
        container_name = c[2]
        result = subprocess.run(
            ["docker", "start", container_name],
            capture_output=True, text=True, timeout=30,
        )
        # Update stored status based on docker start result
        if result.returncode == 0:
            new_status = "running"
        else:
            new_status = "stopped"
        update_container_status(env_id, container_name, new_status)
        results.append({
            "container": container_name,
            "docker_result": {
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "code": result.returncode,
            }
        })

    # Re-run verifier the same way fresh setup does
    verification = await verify_environment(env_id=env_id)

    return {
        "environment_id": env_id,
        "status": "starting",
        "docker_results": results,
        "verification": verification,
    }


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


@router.post("/environments/{env_id}/export")
def export_environment(env_id: str):
    """Export environment config as JSON.

    Returns the stored setup config for an environment.
    Useful for saving and re-using environment configurations.

    SECURITY: Unknown environments return 404; no stored config returns 404.
    """
    # Verify environment exists
    env_row = get_environment(env_id)
    if not env_row:
        raise HTTPException(status_code=404, detail="environment not found")

    # Retrieve stored config
    config_json = get_environment_config(env_id)
    if not config_json:
        raise HTTPException(status_code=404, detail="no stored config for environment")

    import json
    config = json.loads(config_json)

    # Transform to export shape: {environment_id, services:[{name,image,port,volume,env,command}]}
    services = []
    for svc in config.get("services", []):
        service = {
            "name": svc.get("name", ""),
            "image": svc.get("image", ""),
            "port": svc.get("port"),
            "volume": svc.get("volume"),
            "env": svc.get("env"),
            "command": svc.get("command"),
        }
        services.append(service)

    return {"environment_id": env_id, "services": services}


@router.post("/environments/import")
async def import_environment(config: EnvironmentConfig):
    """Import environment config and start setup.

    Parses the body as an EnvironmentConfig (validated by Pydantic)
    and runs the setup pipeline via run_setup.

    Returns the same shape as /setup: {status: "started", environment_id}.
    """
    env_id = await run_setup(config)
    return {"status": "started", "environment_id": env_id}


class CreateSnapshotRequest(BaseModel):
    name: Optional[str] = None


class CreateSnapshotFromEnvRequest(BaseModel):
    environment_id: str
    name: Optional[str] = None


@router.post("/environments/{env_id}/snapshots")
@router.post("/environments/{env_id}/snapshot")
def create_environment_snapshot(env_id: str, body: Optional[CreateSnapshotRequest] = None):
    """Create a durable snapshot from an environment.

    Reuses stored export configuration so the environment can be restored later.
    """
    name = body.name if body else None
    try:
        return snapshot_manager.create_snapshot(env_id, name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/snapshots")
def create_snapshot_direct(body: CreateSnapshotFromEnvRequest):
    """Create a snapshot specifying environment_id in body."""
    try:
        return snapshot_manager.create_snapshot(body.environment_id, body.name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/snapshots")
def list_snapshots():
    """List all saved environment snapshots."""
    return snapshot_manager.list_snapshots()


@router.get("/snapshots/{snapshot_id}")
def get_snapshot(snapshot_id: str):
    """Retrieve details of a specific snapshot."""
    snap = snapshot_manager.get_snapshot(snapshot_id)
    if not snap:
        raise HTTPException(status_code=404, detail="snapshot not found")
    return snap


@router.post("/snapshots/{snapshot_id}/restore")
async def restore_snapshot(snapshot_id: str):
    """Restore an environment from a saved snapshot.

    Reuses the import/run_setup pipeline to launch and verify the environment.
    """
    try:
        new_env_id = await snapshot_manager.restore_snapshot(snapshot_id)
        return {"status": "started", "environment_id": new_env_id, "snapshot_id": snapshot_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/snapshots/{snapshot_id}")
def delete_snapshot(snapshot_id: str):
    """Delete a saved snapshot."""
    deleted = snapshot_manager.delete_snapshot(snapshot_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="snapshot not found")
    return {"status": "deleted", "snapshot_id": snapshot_id}

