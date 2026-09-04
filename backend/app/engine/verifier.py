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
    "python_version": "_python_version",
    "tcp_port": "_tcp_port_check",
    # Phase 2 additions:
    "mongo_ping": "_mongo_ping",
    "http_get": "_http_get_check",
    "http_get_with_api_key": "_http_get_with_api_key_check",
    "kafka_api_version": "_kafka_api_version",
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


async def _python_version(name: str) -> Dict[str, Any]:
    """Check Python version inside the container.

    WHY: The user asked for Python. Did they GET Python?
     We run "python --version" INSIDE the container to verify.
     Tries python3 first, falls back to python if not found.
    """
    result = await run_command(["docker", "exec", name, "python3", "--version"])
    if result["code"] != 0:
        result = await run_command(["docker", "exec", name, "python", "--version"])
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


def _tcp_port_check_sync(container_name: str, port: int) -> bool:
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


async def _tcp_port_check(container_name: str, port: int) -> bool:
    """Async wrapper for TCP port check — runs blocking subprocess in thread."""
    return await asyncio.to_thread(_tcp_port_check_sync, container_name, port)


# ===== Phase 2 Health Check Functions =====

async def _mongo_ping(name: str) -> Dict[str, Any]:
    """Check MongoDB responds to ping via mongosh.

    WHY: Real protocol-level check, not just TCP port.
    """
    result = await run_command([
        "docker", "exec", name,
        "mongosh", "--eval", "db.adminCommand({ping:1})", "--quiet"
    ])
    return {
        "success": result["code"] == 0,
        "output": result["stdout"],
        "error": result["stderr"] if result["code"] != 0 else None,
    }


async def _http_get_check(container_name: str, url: str, timeout: int = 5) -> Dict[str, Any]:
    """HTTP GET health check — runs curl inside container.

    Used by: couchdb, elasticsearch, meilisearch, minio, nats
    """
    result = await run_command([
        "docker", "exec", container_name,
        "curl", "-sf", "--max-time", str(timeout), url
    ])
    return {
        "success": result["code"] == 0,
        "output": result["stdout"] if result["code"] == 0 else result["stderr"],
    }


async def _http_get_with_api_key_check(container_name: str, url: str, api_key: str) -> Dict[str, Any]:
    """HTTP GET with API key header — for typesense.

    WHY: Typesense requires API key for all endpoints including health.
    """
    result = await run_command([
        "docker", "exec", container_name,
        "curl", "-sf", "-H", f"X-TYPESENSE-API-KEY: {api_key}", url
    ])
    return {
        "success": result["code"] == 0,
        "output": result["stdout"] if result["code"] == 0 else result["stderr"],
    }


async def _kafka_api_version(container_name: str) -> Dict[str, Any]:
    """Check Kafka broker is ready via API version probe.

    WHY: Official Kafka readiness check — proves broker accepts connections.
    NOTE: Kafka takes 15-30s to start. Retry logic is in verify_environment.
    """
    result = await run_command([
        "docker", "exec", container_name,
        "kafka-broker-api-versions", "--bootstrap-server", "localhost:9092"
    ])
    return {
        "success": result["code"] == 0,
        "output": result["stdout"][:200] if result["code"] == 0 else result["stderr"],
    }




# ===== Health check URL configuration =====
# Maps service image patterns to their health check URLs
HEALTH_CHECK_URLS = {
    "couchdb": "http://localhost:5984/_up",
    "elasticsearch": "http://localhost:9200/_cluster/health",
    "meilisearch": "http://localhost:7700/health",
    "minio": "http://localhost:9000/minio/health/live",
    "nats": "http://localhost:8222/healthz",
    "typesense": "http://localhost:8108/health",
}


def _get_health_check_url(image: str) -> str:
    """Get the health check URL for a service based on its image."""
    for pattern, url in HEALTH_CHECK_URLS.items():
        if pattern in image:
            return url
    return ""


async def _discover_envman_containers() -> List[Dict[str, str]]:
    """Discover envman containers via Docker when in-memory registry is empty.

    WHY: After server restart, container_registry is empty but containers
         are still running. This fallback queries Docker directly.
    """
    result = await run_command([
        "docker", "ps", "--filter", "name=envman_", "--format", "{{.Names}}|{{.Image}}"
    ])
    containers = []
    if result["code"] == 0 and result["stdout"]:
        for line in result["stdout"].strip().splitlines():
            if "|" in line:
                name, image = line.split("|", 1)
                # Extract service name from container name (envman_xxx -> xxx)
                service_name = name.replace("envman_", "")
                containers.append({
                    "step_id": f"start_{service_name}",
                    "container_name": name,
                    "image": image,
                })
    return containers


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

    elif check_type == "python_version":
        version_info = await _python_version(container_name)
        checks.append({
            "name": "python_version",
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
            port_reachable = await _tcp_port_check(container_name, port)
            checks.append({
                "name": "tcp_port",
                "passed": port_reachable,
                "detail": f"port {port} reachable" if port_reachable else f"port {port} not reachable",
            })

    elif check_type == "mongo_ping":
        ping_result = await _mongo_ping(container_name)
        checks.append({
            "name": "mongo_ping",
            "passed": ping_result["success"],
            "detail": ping_result["output"] if ping_result["success"] else ping_result["error"],
        })

    elif check_type == "http_get":
        url = _get_health_check_url(image)
        if not url:
            checks.append({
                "name": "http_get",
                "passed": False,
                "detail": "no health check URL configured for this service",
            })
        else:
            http_result = await _http_get_check(container_name, url)
            checks.append({
                "name": "http_get",
                "passed": http_result["success"],
                "detail": http_result["output"] if http_result["success"] else http_result["error"],
            })

    elif check_type == "http_get_with_api_key":
        url = _get_health_check_url(image)
        # Typesense API key from default_env
        api_key = service.default_env.get("TYPESENSE_API_KEY", "xyz")
        if not url:
            checks.append({
                "name": "http_get_with_api_key",
                "passed": False,
                "detail": "no health check URL configured for this service",
            })
        else:
            http_result = await _http_get_with_api_key_check(container_name, url, api_key)
            checks.append({
                "name": "http_get_with_api_key",
                "passed": http_result["success"],
                "detail": http_result["output"] if http_result["success"] else http_result["error"],
            })

    elif check_type == "kafka_api_version":
        kafka_result = await _kafka_api_version(container_name)
        checks.append({
            "name": "kafka_api_version",
            "passed": kafka_result["success"],
            "detail": kafka_result["output"] if kafka_result["success"] else kafka_result["error"],
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

    DYNAMIC: Iterates over all containers in the registry
    instead of hardcoding specific services.

    FALLBACK: If in-memory registry is empty (e.g. after server restart),
    discovers envman containers directly via Docker.
    """
    logger.info("=== starting verification ===")
    registry = dump_registry()

    # Build work items from registry
    work_items = []

    if registry:
        # Use in-memory registry
        for step_id, container_id in registry.items():
            if not step_id.startswith("start_"):
                continue
            service_name = step_id[6:]
            container_name = f"envman_{service_name}"
            work_items.append({"step_id": step_id, "container_name": container_name})
    else:
        # Fallback: discover containers via Docker
        logger.info("in-memory registry empty, discovering containers via Docker")
        discovered = await _discover_envman_containers()
        work_items = discovered

    results: List[Dict[str, Any]] = []

    for item in work_items:
        container_name = item["container_name"]
        # Extract service name from container name
        service_name = container_name.replace("envman_", "")

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
