"""
WHY:
We need a single source of truth for known services and how they behave.

WHAT:
Defines a static registry of ServiceDefinition entries.

HOW:
Verifier will use this registry to determine which health check to run.

THINK OF IT LIKE:
A lookup table mapping service identity → verification behavior.
"""

from .schema import ServiceDefinition


SERVICES = [
    ServiceDefinition(
        id="node",
        name="Node.js",
        category="runtime",
        image="node",
        default_port=None,
        default_env={},
        health_check_type="node_version"
    ),
    ServiceDefinition(
        id="python",
        name="Python",
        category="runtime",
        image="python",
        default_port=None,
        default_env={},
        health_check_type="node_version"
    ),
    ServiceDefinition(
        id="postgres",
        name="PostgreSQL",
        category="database",
        image="postgres",
        default_port=5432,
        default_env={},
        health_check_type="pg_isready"
    ),
    ServiceDefinition(
        id="mysql",
        name="MySQL",
        category="database",
        image="mysql",
        default_port=3306,
        default_env={},
        health_check_type="tcp_port"
    ),
    ServiceDefinition(
        id="redis",
        name="Redis",
        category="cache",
        image="redis",
        default_port=6379,
        default_env={},
        health_check_type="redis_ping"
    ),
    ServiceDefinition(
        id="mongo",
        name="MongoDB",
        category="database",
        image="mongo",
        default_port=27017,
        default_env={},
        health_check_type="tcp_port"
    ),
    ServiceDefinition(
        id="rabbitmq",
        name="RabbitMQ",
        category="queue",
        image="rabbitmq",
        default_port=5672,
        default_env={},
        health_check_type="tcp_port"
    ),
]


def get_service_by_image(image: str):
    for svc in SERVICES:
        if svc.image in image:
            return svc
    return None


def get_all_services():
    return SERVICES