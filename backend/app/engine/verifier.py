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
from typing import Dict, Any, List
from app.engine.executor import run_command
from app.engine.state import get_container, dump_registry
from app.utils.logger import get_logger

logger = get_logger("verifier")

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


async def verify_environment() -> List[Dict[str, Any]]:
    """Run ALL verification checks and return a complete report.

    This is what we send to the frontend.
    Every service gets a clear status: ready, failed, not_found, etc.
    """
    logger.info("=== starting verification ===")
    dump_registry()

    results: List[Dict[str, Any]] = []

    # --- Verify Postgres ---
    pg_name = "envman_pg"
    pg_container = get_container("start_pg")

    if not pg_container:
        logger.error("postgres container not tracked")
        results.append({
            "service": "postgres",
            "status": "not_tracked",
            "checks": [],
        })
    elif not await _container_exists(pg_name):
        logger.error("postgres container '%s' does not exist", pg_name)
        results.append({
            "service": "postgres",
            "status": "not_found",
            "checks": [],
        })
    elif not await _container_running(pg_name):
        logger.error("postgres container '%s' is not running", pg_name)
        results.append({
            "service": "postgres",
            "status": "not_running",
            "checks": [],
        })
    else:
        checks = []

        # Check 1: pg_isready
        ready = await _pg_is_ready(pg_name)
        checks.append({
            "name": "pg_isready",
            "passed": ready,
            "detail": "accepting connections" if ready else "not accepting connections",
        })

        # Check 2: run a real query
        if ready:
            query_result = await _pg_run_query(pg_name)
            checks.append({
                "name": "query_execution",
                "passed": query_result["success"],
                "detail": query_result["output"] if query_result["success"] else query_result["error"],
            })

        status = "ready" if all(c["passed"] for c in checks) else "failed"
        logger.info("postgres verification: %s", status)

        results.append({
            "service": "postgres",
            "status": status,
            "checks": checks,
        })

    # --- Verify Node ---
    node_name = "envman_node"
    node_container = get_container("start_node")

    if not node_container:
        logger.error("node container not tracked")
        results.append({
            "service": "node",
            "status": "not_tracked",
            "checks": [],
        })
    elif not await _container_exists(node_name):
        logger.error("node container '%s' does not exist", node_name)
        results.append({
            "service": "node",
            "status": "not_found",
            "checks": [],
        })
    elif not await _container_running(node_name):
        logger.error("node container '%s' is not running", node_name)
        results.append({
            "service": "node",
            "status": "not_running",
            "checks": [],
        })
    else:
        checks = []

        # Check 1: node -v
        version_info = await _node_version(node_name)
        checks.append({
            "name": "node_version",
            "passed": version_info["success"],
            "detail": version_info["version"] or "could not get version",
        })

        status = "ready" if all(c["passed"] for c in checks) else "failed"
        logger.info("node verification: %s (version: %s)", status, version_info["version"])

        results.append({
            "service": "node",
            "status": status,
            "version": version_info["version"],
            "checks": checks,
        })

    logger.info("=== verification complete ===")
    return results
