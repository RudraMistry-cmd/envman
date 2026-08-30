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
import subprocess
from typing import Dict, Any, List
from app.models.step import Step
from app.engine.state import store_container
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

    # Build command as a LIST (never as a string!)
    cmd: List[str] = ["docker", "run", "-d", "--name", name]

    # FIX #5: Network attachment
    cmd.extend(["--network", network_name])

    # Port mapping (if specified)
    port = step.params.get("port")
    if port:
        cmd.extend(["-p", port])

    # Volume mounting (if specified)
    volume = step.params.get("volume")
    if volume:
        cmd.extend(["-v", volume])

    # Environment variables (convert dict to multiple -e flags)
    env = step.params.get("env")
    if env:
        if isinstance(env, dict):
            for key, value in env.items():
                cmd.extend(["-e", f"{key}={value}"])
        else:
            # Legacy string format: "POSTGRES_PASSWORD=postgres"
            cmd.extend(["-e", env])

    # Add the image name last
    cmd.append(image)

    result = await run_command(cmd)

    if result["code"] == 0:
        container_id = result["stdout"]
        store_container(step.id, container_id, env_id=env_id, name=name, image=image)
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
