"""
Planner
=======

WHY: Before building anything, you need a plan.
     "First create the network, THEN pull images, THEN start containers."
     You can't start a container before its image is downloaded.

WHAT: Takes the user's config (services list)
     and creates a list of steps to execute.

HOW:
     1. Create network step (first)
     2. For each service:
        a. Check if image exists locally
        b. If not, create pull step
        c. Create start step with networking, volumes, env vars
     3. Return ordered plan

THINK OF IT LIKE:
     Building with LEGO.
     Step 1: Lay the foundation (create network)
     Step 2: Open the box (pull image)
     Step 3: Build the house (start container)
     You MUST lay the foundation before building.
"""

from typing import List, Optional, Dict
from app.models.plan import Plan
from app.models.step import Step
from app.models.environment import EnvironmentConfig, ServiceSpec
from app.engine.executor import image_exists
from app.registry.services import get_service_by_image, get_all_services
from app.utils.logger import get_logger

logger = get_logger("planner")


def _lookup_registry_service(service: ServiceSpec) -> Optional[Dict]:
    """Look up a service in the registry by image prefix.

    WHY: Registry defines default_env (API keys, root passwords, etc.)
         that must be merged into the container's environment.

    Returns: ServiceDefinition dict or None if not found.
    """
    return get_service_by_image(service.image)


def _merge_env(registry_env: Dict[str, str], user_env: Optional[Dict[str, str]]) -> Dict[str, str]:
    """Merge registry defaults with user-supplied env vars.

    WHY: Registry provides required defaults (e.g. TYPESENSE_API_KEY).
         User values override on conflict.

    Priority: user_env > registry_env
    """
    merged = {}
    if registry_env:
        merged.update(registry_env)
    if user_env:
        merged.update(user_env)
    return merged


async def plan_environment(config: EnvironmentConfig) -> Plan:
    """Create a step-by-step plan from the user's config.

    This is the BLUEPRINT. Nothing runs yet.
    We just figure out WHAT needs to happen and in WHAT ORDER.

    Plan structure:
    - Step: create_network(network_name)
    - For each service:
      - Step: pull_image(image)  [only if image not cached]
      - Step: run_container(name, image, port, volume, env, network)
    """
    steps: List[Step] = []
    network_name = config.network_name

    # Network creation step (always first)
    steps.append(Step(
        id="create_network",
        type="create_network",
        params={"network_name": network_name},
    ))

    # Service steps
    for service in config.services:
        # Check if image exists locally
        needs_pull = not await image_exists(service.image)

        # Image pull step (only if image not cached)
        if needs_pull:
            steps.append(Step(
                id=f"pull_{service.name}",
                type="pull_image",
                params={"image": service.image},
            ))

        # Container run step
        container_name = f"envman_{service.name}"
        params = {
            "image": service.image,
            "name": container_name,
        }

        # Add optional params
        if service.port:
            params["port"] = f"{service.port}:{service.port}"
        if service.volume:
            params["volume"] = service.volume

        # Merge registry default_env with user-supplied env
        # WHY: Registry provides required defaults (API keys, root passwords).
        #      User values override on conflict.
        registry_svc = _lookup_registry_service(service)
        registry_env = registry_svc.default_env if registry_svc else {}
        merged_env = _merge_env(registry_env, service.env)
        if merged_env:
            params["env"] = merged_env

        steps.append(Step(
            id=f"start_{service.name}",
            type="start_container",
            params=params,
            depends_on=f"pull_{service.name}" if needs_pull else None,
        ))

    total_services = len(config.services)
    pulled_count = sum(1 for s in steps if s.type == "pull_image")
    logger.info("plan created with %d steps (%d pulls needed)", len(steps), pulled_count)
    for step in steps:
        dep = f" (after {step.depends_on})" if step.depends_on else ""
        logger.info("  -> %s [%s]%s", step.id, step.type, dep)

    return Plan(steps=steps, network_name=network_name)
