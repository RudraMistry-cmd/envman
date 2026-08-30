"""
Planner
=======

WHY: Before building anything, you need a plan.
     "First pull the images, THEN start the containers."
     You can't start a container before its image is downloaded.

WHAT: Takes the user's config (node:20, postgres:16)
     and creates a list of steps to execute.

HOW:
     1. Resolve version aliases ("20" → "20.18.0")
     2. Create pull steps (download images)
     3. Create start steps (launch containers)
     4. Set dependencies (start depends on pull)

THINK OF IT LIKE:
     Building with LEGO.
     Step 1: Open the box (pull image)
     Step 2: Build the house (start container)
     You MUST open the box before building.
"""

from typing import List
from app.models.plan import Plan
from app.models.step import Step
from app.models.environment import EnvironmentConfig
from app.utils.logger import get_logger

logger = get_logger("planner")


def resolve_version(service: str, version: str) -> str:
    """Resolve a short version to a full version.

    WHY: "node:20" is ambiguous. "node:20.18.0" is exact.
     Docker needs exact image tags to be reliable.

    HOW: We maintain a small map of known-good versions.
     In the future, this could query Docker Hub.

    EXAMPLES:
         resolve_version("node", "20")     → "20.18.0"
         resolve_version("postgres", "16")  → "16.4"
         resolve_version("node", "20.18.0") → "20.18.0" (already exact)
    """
    VERSION_MAP = {
        "node": {
            "18": "18.20.4",
            "20": "20.18.0",
            "22": "22.9.0",
        },
        "postgres": {
            "14": "14.13",
            "15": "15.8",
            "16": "16.4",
            "17": "17.0",
        },
    }

    service_versions = VERSION_MAP.get(service, {})
    resolved = service_versions.get(version, version)

    if resolved != version:
        logger.info("resolved %s:%s → %s:%s", service, version, service, resolved)
    else:
        logger.info("using exact version %s:%s", service, resolved)

    return resolved


def plan_environment(config: EnvironmentConfig) -> Plan:
    """Create a step-by-step plan from the user's config.

    This is the BLUEPRINT. Nothing runs yet.
    We just figure out WHAT needs to happen and in WHAT ORDER.
    """

    node_version = resolve_version("node", config.node)
    pg_version = resolve_version("postgres", config.postgres)

    steps: List[Step] = [
        Step(
            id="pull_node",
            type="pull_image",
            params={"image": f"node:{node_version}"},
        ),
        Step(
            id="pull_pg",
            type="pull_image",
            params={"image": f"postgres:{pg_version}"},
        ),
        Step(
            id="start_pg",
            type="start_container",
            params={
                "image": f"postgres:{pg_version}",
                "name": "envman_pg",
                "env": "POSTGRES_PASSWORD=postgres",
                "port": "5432:5432",
            },
            depends_on="pull_pg",
        ),
        Step(
            id="start_node",
            type="start_container",
            params={
                "image": f"node:{node_version}",
                "name": "envman_node",
            },
            depends_on="pull_node",
        ),
    ]

    logger.info("plan created with %d steps:", len(steps))
    for step in steps:
        dep = f" (after {step.depends_on})" if step.depends_on else ""
        logger.info("  → %s [%s]%s", step.id, step.type, dep)

    return Plan(steps=steps)
