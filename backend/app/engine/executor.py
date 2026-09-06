"""
Executor
========

WHY: The planner made a plan. Now someone has to DO it.
     The executor RUNS Docker commands to pull images and start containers.

WHAT: Executes one step at a time.
      - create_network: creates a Docker network
      - pull_image: downloads a Docker image
      - start_container: creates and starts a container

HOW:
     1. Takes a Step object
     2. Builds a SAFE command (list of strings, NOT a shell string)
     3. Runs it asynchronously (doesn't freeze the server)
     4. Returns success or failure

SECURITY RULES:
     - NEVER use shell=True (prevents command injection)
     - ALWAYS use list-based commands
     - ALWAYS name containers (deterministic)
     - ALWAYS remove old containers before creating new ones

THINK OF IT LIKE:
     A factory worker who follows instructions.
     Instruction: "Pull image node:20"
     Worker: runs "docker pull node:20"
     Reports back: "Done!" or "Failed: image not found"
"""

import asyncio
import socket
import subprocess
from typing import Dict, Any, List
from app.models.step import Step
from app.engine.state import store_container
from app.engine.port_allocator import port_allocator, NoPortAvailableError
from app.utils.logger import get_logger

logger = get_logger("executor")


def _run_sync(cmd: List[str], timeout: int) -> Dict[str, Any]:
    """Synchronous command runner (called in a thread)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "code": result.returncode,
        }
    except subprocess.TimeoutExpired:
        return {"stdout": "", "stderr": f"Timed out after {timeout}s", "code": -1}
    except FileNotFoundError:
        return {
            "stdout": "",
            "stderr": "Docker not found. Is Docker installed and in PATH?",
            "code": -1,
        }
    except Exception as e:
        return {"stdout": "", "stderr": f"{type(e).__name__}: {e}", "code": -1}


def is_host_port_in_use(port: int) -> bool:
    """Check if a host port is already in use via socket bind attempt.

    WHY: Prevent Docker port conflicts before attempting docker run -p.
         If the host port is already occupied, docker will fail with a
         confusing "port is already allocated" error.

    HOW: Try to bind a socket to 0.0.0.0:port. If bind raises OSError
         with errno 98 (EADDRINUSE) or 10048 (same on Windows), the port
         is in use. Otherwise bind succeeds and port is free.
    """
    if port is None or port <= 0:
        return False
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
        return False  # bind succeeded -> port is free
    except OSError as e:
        # errno 98 = EADDRINUSE (Linux), errno 10048 = WSAEADDRINUSE (Windows)
        if e.errno in (98, 10048):
            return True  # port is already in use
        # For other OSErrors, treat as "port free" to avoid false positives
        return False


async def run_command(cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
    """Run a command SAFELY and ASYNCHRONOUSLY.

    WHY list-based? Because:
         subprocess.run("docker pull " + user_input, shell=True)
         If user_input = "node:20; rm -rf /"
         That would DELETE YOUR FILES.

         subprocess.run(["docker", "pull", "node:20"])
         This is SAFE. Each argument is separate. No tricks.

    WHY asyncio.to_thread? Because:
         Docker pull can take 30+ seconds.
         If we block the event loop, the entire server freezes.
         asyncio.to_thread runs subprocess.run in a background thread
         so the event loop stays free for WebSocket messages.
    """
    logger.info("running: %s", " ".join(cmd))

    result = await asyncio.to_thread(_run_sync, cmd, timeout)

    if result["code"] == 0:
        logger.info("success: %s", result["stdout"][:100])
    else:
        logger.error("failed (code %d): %s", result["code"], result["stderr"][:200])

    return result


async def image_exists(image: str) -> bool:
    """Check if a Docker image exists locally.

    WHY: Before pulling, we check if the image is already cached.
     Docker Hub has rate limits and pulls are slow.
     If the image is already local, we skip the pull entirely.

    HOW: Uses `docker images --format` to query the local image store.
     Returns True if the exact image:tag is present.
    """
    result = await run_command(
        ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}", image],
        timeout=10,
    )
    if result["code"] != 0:
        return False
    lines = [line.strip() for line in result["stdout"].splitlines() if line.strip()]
    exists = image in lines
    if exists:
        logger.info("image %s found locally, pull can be skipped", image)
    else:
        logger.info("image %s not found locally, pull required", image)
    return exists


async def _create_network(network_name: str) -> Dict[str, Any]:
    """Create a Docker network.

    WHY: Containers on the same network can communicate via container names.
         This is essential for multi-service environments (e.g., Node connecting to Postgres).

    FIX: Ignore error if network already exists.
    """
    logger.info("creating network: %s", network_name)
    result = await run_command(["docker", "network", "create", network_name])

    # Ignore "already exists" error
    if result["code"] != 0 and "already exists" not in result.get("stderr", ""):
        logger.error("failed to create network: %s", result["stderr"])
        return result

    logger.info("network '%s' ready", network_name)
    return {"stdout": network_name, "stderr": "", "code": 0}


async def _pull_image(image: str) -> Dict[str, Any]:
    """Download a Docker image from Docker Hub.

    WHY: Before we can start a container, we need its image.
     Think of it like downloading an app before you can open it.
    """
    return await run_command(["docker", "pull", image])


async def _start_container(step: Step, network_name: str, env_id: str = None) -> Dict[str, Any]:
    """Start a Docker container.

    STEPS:
     1. Remove any old container with the same name (cleanup)
     2. Build the docker run command (safely, as a list)
     3. Start the container
     4. Save the container ID for later verification
    """
    name: str = step.params.get("name", step.id)
    image: str = step.params["image"]

    # Clean up: remove old container if it exists
    logger.info("cleaning up old container '%s' if exists", name)
    await run_command(["docker", "rm", "-f", name])

    # Extract host port and container port from param
    raw_port = step.params.get("port")
    host_port = None
    container_port = None
    if raw_port is not None:
        if ":" in str(raw_port):
            parts = str(raw_port).split(":")
            try:
                host_port = int(parts[0])
                container_port = int(parts[1]) if len(parts) > 1 else host_port
            except ValueError:
                pass
        else:
            try:
                host_port = int(raw_port)
                container_port = host_port
            except ValueError:
                pass

    original_host_port = host_port
    assigned_host_port = host_port
    reassigned = False

    # Proactive conflict check & allocation (TECHNICAL_SPEC.md Part 7 §3)
    if host_port is not None:
        if not port_allocator.is_available(host_port):
            try:
                assigned_host_port = port_allocator.allocate(name, preferred_port=host_port)
                reassigned = (assigned_host_port != original_host_port)
                if reassigned:
                    logger.info(
                        "Host port %d is in use; reassigning container '%s' to port %d",
                        original_host_port, name, assigned_host_port,
                    )
            except NoPortAvailableError as e:
                logger.error("No free port available for '%s': %s", name, e)
                normalized = f"Host port {host_port} is already in use and no available port was found - cannot start container '{name}'."
                return {"stdout": "", "stderr": normalized, "code": 1}
        else:
            port_allocator.allocated[host_port] = name

    def _build_cmd(curr_host_port: Optional[int]) -> List[str]:
        cmd: List[str] = ["docker", "run", "-d", "--name", name, "--network", network_name]
        if curr_host_port is not None and container_port is not None:
            cmd.extend(["-p", f"{curr_host_port}:{container_port}"])
        elif raw_port:
            cmd.extend(["-p", str(raw_port)])

        volume = step.params.get("volume")
        if volume:
            cmd.extend(["-v", volume])

        env = step.params.get("env")
        if env:
            if isinstance(env, dict):
                for key, value in env.items():
                    cmd.extend(["-e", f"{key}={value}"])
            else:
                cmd.extend(["-e", env])

        cmd.append(image)
        command = step.params.get("command")
        if command:
            if isinstance(command, str):
                command = [command]
            cmd.extend(command)
        return cmd

    max_retries = 5
    attempts = 0
    result: Dict[str, Any] = {"stdout": "", "stderr": "", "code": -1}

    while attempts <= max_retries:
        cmd = _build_cmd(assigned_host_port)
        result = await run_command(cmd)
        if result["code"] == 0:
            break

        stderr_lower = result["stderr"].lower()
        is_port_conflict = (
            "port is already allocated" in stderr_lower
            or "bind for" in stderr_lower
            or "address already in use" in stderr_lower
        )

        if is_port_conflict and assigned_host_port is not None and attempts < max_retries:
            attempts += 1
            port_allocator.release(assigned_host_port)
            try:
                next_port = port_allocator.allocate(name, preferred_port=assigned_host_port + 1)
            except NoPortAvailableError:
                break
            logger.warning(
                "Docker reported port %d in use for '%s'; retrying with next free port %d (attempt %d/%d)",
                assigned_host_port, name, next_port, attempts, max_retries,
            )
            assigned_host_port = next_port
            reassigned = True
            await run_command(["docker", "rm", "-f", name])
            continue

        # If not port conflict or exceeded max retries:
        if is_port_conflict:
            port_to_report = assigned_host_port or host_port
            normalized = f"Host port {port_to_report} is already in use - cannot start container '{name}'. Stop the conflicting service or choose a different port."
            logger.error(normalized)
            return {"stdout": "", "stderr": normalized, "code": 1}
        break

    if result["code"] == 0:
        container_id = result["stdout"]
        store_container(step.id, container_id, env_id=env_id, name=name, image=image)
        if reassigned:
            step.params["port"] = f"{assigned_host_port}:{container_port}"
            step.params["reassigned_port"] = assigned_host_port
            step.params["original_port"] = original_host_port
            result["reassigned_port"] = assigned_host_port
            result["original_port"] = original_host_port
            result["reassignment_message"] = (
                f"Port {original_host_port} was in use; reassigned container '{name}' to port {assigned_host_port}"
            )
            logger.info("container '%s' started successfully on reassigned port %d", name, assigned_host_port)
        else:
            logger.info("container '%s' started successfully", name)
    else:
        logger.error("failed to start container '%s': %s", name, result["stderr"])

    return result


async def execute_step(step: Step, network_name: str = "envman_net", env_id: str = None) -> Dict[str, Any]:
    """Execute a single step.

    This is the main entry point the coordinator calls.
    It figures out what type of step it is and runs it.
    """
    logger.info("=== executing step: %s (%s) ===", step.id, step.type)

    if step.type == "create_network":
        return await _create_network(step.params.get("network_name", network_name))

    if step.type == "pull_image":
        return await _pull_image(step.params["image"])

    if step.type == "start_container":
        return await _start_container(step, network_name, env_id)

    return {"stdout": "", "stderr": f"Unknown step type: {step.type}", "code": 1}
