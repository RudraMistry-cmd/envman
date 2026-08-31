"""
Verifier
========

WHY: This is the MOST IMPORTANT part of EnvMan.
     The whole promise is: "If EnvMan says it works, IT WORKS."

     Starting a container is NOT the same as it working.
     A container can be "running" but Postgres hasn't finished starting yet.
     A container can be "running" but Node can't connect to Postgres.

WHAT: Checks that each service is ACTUALLY ready to use.
     - Postgres: can we connect and run a query?
     - Node:     is the right version installed?
     - Redis:    can we ping it?

HOW:
     1. Check if container exists
     2. Check if container is running
     3. Run commands INSIDE the container (docker exec)
     4. Retry if needed (Postgres takes time to start)
     5. Return a clear report

CRITICAL DETAIL:
     We use "docker exec" to run commands INSIDE the container.
     NOT "docker inspect" on the host.
     WHY? Because we need to know if the SERVICE works,
     not just if the container process is alive.

THINK OF IT LIKE:
     A car inspection.
     "The engine is running" ≠ "The car drives."
     You need to: start engine, check oil, test brakes, try the radio.
     THEN you can say "this car works."
"""

import asyncio
import subprocess
from typing import Dict, Any, List
from app.engine.executor import run_command
from app.engine.state import get_container, dump_registry
from app.registry.services import get_service_by_image
from app.utils.logger import get_logger

logger = get_logger("verifier")

# Dispatch map for health check methods
HEALTH_CHECK_DISPATCH = {
    "pg_isready": "_pg_is_ready",
    "redis_ping": "_redis_ping",
    "node_version": "_node_version",
    "tcp_port": "_tcp_port_check",
}

# How many times to retry checking Postgres
PG_RETRY_COUNT = 5
# How long to wait between retries (seconds)
PG_RETRY_DELAY = 2


async def _container_exists(name: str) -> bool:
    """Check if a container exists (running or stopped)."""
    result = await run_command(["docker", "inspect", name])
    return result["code"] == 0


async def _container_running(name: str) -> bool:
    """Check if a container is currently running."""
    result = await run_command([
        "docker", "inspect", "-f", "{{.State.Running}}", name
    ])
    return result["code"] == 0 and result["stdout"].strip() == "true"


async def _pg_is_ready(name: str) -> bool:
    """Check if Postgres is ready to accept connections.

    WHY retry? Because Postgres takes a few seconds to start
     after the container is created. The first check might fail
     even though everything is fine. We wait and try again.
    """
    for attempt in range(1, PG_RETRY_COUNT + 1):
        result = await run_command(
            ["docker", "exec", name, "pg_isready", "-U", "postgres"]
        )
        if result["code"] == 0:
            logger.info("postgres ready (attempt %d/%d)", attempt, PG_RETRY_COUNT)
            return True

        if attempt < PG_RETRY_COUNT:
            logger.info(
                "postgres not ready yet (attempt %d/%d), waiting %ds...",
                attempt, PG_RETRY_COUNT, PG_RETRY_DELAY,
            )
            await asyncio.sleep(PG_RETRY_DELAY)

    logger.error("postgres not ready after %d attempts", PG_RETRY_COUNT)
    return False


async def _pg_run_query(name: str) -> Dict[str, Any]:
    """Run a real SQL query inside Postgres.

    WHY: pg_isready says "I'm listening."
     But can we actually RUN a query?
     This is the REAL test of whether Postgres works.
    """
    result = await run_command([
        "docker", "exec", name,
        "psql", "-U", "postgres", "-c", "SELECT 1 AS connected;"
    ])
    return {
        "success": result["code"] == 0,
        "output": result["stdout"],
        "error": result["stderr"] if result["code"] != 0 else None,
    }


async def _node_version(name: str) -> Dict[str, Any]:
    """Check Node.js version inside the container.

    WHY: The user asked for Node 20. Did they GET Node 20?
     We run "node -v" INSIDE the container to verify.
    """
    result = await run_command(["docker", "exec", name, "node", "-v"])
    return {
        "version": result["stdout"].strip() if result["code"] == 0 else None,
        "success": result["code"] == 0,
    }


async def _redis_ping(name: str) -> Dict[str, Any]:
    """Check if Redis responds to PING.

    WHY: Redis might be running but not accepting connections.
     PING → PONG confirms the service is alive.
    """
    result = await run_command([
        "docker", "exec", name, "redis-cli", "ping"
    ])
    return {
        "success": result["code"] == 0 and "PONG" in result["stdout"],
        "output": result["stdout"],
        "error": result["stderr"] if result["code"] != 0 else None,
    }


def _tcp_port_check(container_name: str, port: int) -> bool:
    """
    WHY:
    Some services only need a basic port-level readiness check.

    WHAT:
    Verifies that a TCP port is open inside the container.

    HOW:
    Uses bash + /dev/tcp to probe port from within container.

    THINK OF IT LIKE:
    A minimal liveness probe — not full correctness, but connectivity.
    """
    cmd = [
        "docker", "exec", container_name,
        "bash", "-c", f"</dev/tcp/localhost/{port}"
    ]
    result = subprocess.run(cmd, capture_output=True)
    return result.returncode == 0


async def _verify_service(name: str, image: str, port: int = None) -> Dict[str, Any]:
    """Verify a single service based on registry dispatch.

    WHY:
    We want verification logic driven by the service registry,
    not fragile substring matching on image strings.

    WHAT:
    Looks up service definition from registry and dispatches
    to the appropriate health check method.

    HOW:
    Uses get_service_by_image to find the service definition,
    then dispatches based on health_check_type.

    THINK OF IT LIKE:
    A router that maps service type → verification behavior.
    """
    container_name = f"envman_{name}"

    # Check if container exists
    if not await _container_exists(container_name):
        logger.error("container '%s' does not exist", container_name)
        return {
            "service": name,
            "status": "not_found",
            "checks": [],
        }

    # Check if container is running
    if not await _container_running(container_name):
        logger.error("container '%s' is not running", container_name)
        return {
            "service": name,
            "status": "not_running",
            "checks": [],
        }

    # Look up service in registry
    service = get_service_by_image(image)

    if not service:
        logger.warning("no registry match for image '%s'", image)
        return {
            "service": name,
            "status": "unknown",
            "checks": [{
                "name": "registry_lookup",
                "passed": False,
                "detail": "no registry match for image",
            }],
        }

    checks = []
    check_type = service.health_check_type

    # Dispatch to appropriate health check
    if check_type == "pg_isready":
        ready = await _pg_is_ready(container_name)
        checks.append({
            "name": "pg_isready",
            "passed": ready,
            "detail": "accepting connections" if ready else "not accepting connections",
        })

        if ready:
            query_result = await _pg_run_query(container_name)
            checks.append({
                "name": "query_execution",
                "passed": query_result["success"],
                "detail": query_result["output"] if query_result["success"] else query_result["error"],
            })

    elif check_type == "redis_ping":
        ping_result = await _redis_ping(container_name)
        checks.append({
            "name": "redis_ping",
            "passed": ping_result["success"],
            "detail": ping_result["output"] if ping_result["success"] else ping_result["error"],
        })

    elif check_type == "node_version":
        version_info = await _node_version(container_name)
        checks.append({
            "name": "node_version",
            "passed": version_info["success"],
            "detail": version_info["version"] or "could not get version",
        })

    elif check_type == "tcp_port":
        if not port:
            checks.append({
                "name": "tcp_port",
                "passed": False,
                "detail": "no port defined for service",
            })
        else:
            port_reachable = _tcp_port_check(container_name, port)
            checks.append({
                "name": "tcp_port",
                "passed": port_reachable,
                "detail": f"port {port} reachable" if port_reachable else f"port {port} not reachable",
            })

    else:
        # Unsupported check type
        checks.append({
            "name": "unsupported_check",
            "passed": False,
            "detail": f"unsupported health check type: {check_type}",
        })

    status = "ready" if all(c["passed"] for c in checks) else "failed"
    logger.info("verification for '%s': %s (type=%s)", name, status, check_type)

    return {
        "service": name,
        "status": status,
        "checks": checks,
    }


async def verify_environment() -> List[Dict[str, Any]]:
    """Run ALL verification checks and return a complete report.

    This is what we send to the frontend.
    Every service gets a clear status: ready, failed, not_found, etc.

    NOW DYNAMIC: Iterates over all containers in the registry
    instead of hardcoding specific services.
    """
    logger.info("=== starting verification ===")
    registry = dump_registry()

    results: List[Dict[str, Any]] = []

    # Map step IDs to service info
    # Step IDs are like "start_node", "start_postgres", etc.
    for step_id, container_id in registry.items():
        # Extract service name from step ID (remove "start_" prefix)
        if not step_id.startswith("start_"):
            continue

        service_name = step_id[6:]  # Remove "start_" prefix
        container_name = f"envman_{service_name}"

        # Get image from container inspect
        result = await run_command([
            "docker", "inspect", "--format", "{{.Config.Image}}", container_name
        ])
        image = result["stdout"].strip() if result["code"] == 0 else "unknown"

        # Get port from container inspect (first exposed port)
        port = None
        port_result = await run_command([
            "docker", "inspect", "--format", "{{range $p, $conf := .NetworkSettings.Ports}}{{$p}} {{end}}", container_name
        ])
        if port_result["code"] == 0:
            ports = port_result["stdout"].strip().split()
            if ports:
                # Extract port number from "80/tcp" format
                port_str = ports[0].split("/")[0]
                try:
                    port = int(port_str)
                except ValueError:
                    pass

        # Verify this service
        verification = await _verify_service(service_name, image, port)
        results.append(verification)

    logger.info("=== verification complete ===")
    return results
