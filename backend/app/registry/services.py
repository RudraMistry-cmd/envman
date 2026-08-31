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
    # ===== RUNTIMES =====
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

    # ===== DATABASES =====
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
        id="mongo",
        name="MongoDB",
        category="database",
        image="mongo",
        default_port=27017,
        default_env={},
        health_check_type="mongo_ping"
    ),
    ServiceDefinition(
        id="sqlite",
        name="SQLite",
        category="database",
        image="sqlite",
        default_port=None,
        default_env={},
        health_check_type="sqlite_version"
    ),
    ServiceDefinition(
        id="couchdb",
        name="CouchDB",
        category="database",
        image="couchdb",
        default_port=5984,
        default_env={},
        health_check_type="http_get"
    ),

    # ===== CACHES =====
    ServiceDefinition(
        id="redis",
        name="Redis",
        category="cache",
        image="redis",
        default_port=6379,
        default_env={},
        health_check_type="redis_ping"
    ),

    # ===== MESSAGE QUEUES =====
    ServiceDefinition(
        id="rabbitmq",
        name="RabbitMQ",
        category="queue",
        image="rabbitmq",
        default_port=5672,
        default_env={},
        health_check_type="tcp_port"
    ),
    ServiceDefinition(
        id="kafka",
        name="Kafka",
        category="message_broker",
        image="confluentinc/cp-kafka",
        default_port=9092,
        default_env={},
        health_check_type="kafka_api_version"
    ),
    ServiceDefinition(
        id="nats",
        name="NATS",
        category="message_broker",
        image="nats",
        default_port=4222,
        default_env={},
        health_check_type="http_get"
    ),

    # ===== SEARCH =====
    ServiceDefinition(
        id="elasticsearch",
        name="Elasticsearch",
        category="search",
        image="elasticsearch",
        default_port=9200,
        default_env={},
        health_check_type="http_get"
    ),
    ServiceDefinition(
        id="meilisearch",
        name="MeiliSearch",
        category="search",
        image="getmeili/meilisearch",
        default_port=7700,
        default_env={},
        health_check_type="http_get"
    ),
    ServiceDefinition(
        id="typesense",
        name="Typesense",
        category="search",
        image="typesense/typesense",
        default_port=8108,
        default_env={},
        health_check_type="http_get_with_api_key"
    ),

    # ===== STORAGE =====
    ServiceDefinition(
        id="minio",
        name="MinIO",
        category="storage",
        image="minio/minio",
        default_port=9000,
        default_env={},
        health_check_type="http_get"
    ),
]


def get_service_by_image(image: str):
    for svc in SERVICES:
        if svc.image in image:
            return svc
    return None


def get_all_services():
    return SERVICES
