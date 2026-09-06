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
        # Bare `node` launches an interactive REPL that hits EOF and exits
        # under `docker run -d` (no TTY). tail keeps the runtime alive as an
        # exec-able dev environment (portable: works on slim/busybox too,
        # unlike `sleep infinity`).
        default_command=["tail", "-f", "/dev/null"],
        health_check_type="node_version"
    ),
    ServiceDefinition(
        id="python",
        name="Python",
        category="runtime",
        image="python",
        default_port=None,
        default_env={},
        # Same REPL-EOF exit as node; same keep-alive treatment.
        default_command=["tail", "-f", "/dev/null"],
        health_check_type="python_version"
    ),

    # ===== DATABASES =====
    ServiceDefinition(
        id="postgres",
        name="PostgreSQL",
        category="database",
        image="postgres",
        default_port=5432,
        # Official image REFUSES fresh init without a superuser password
        # (proven 2026-09-06: "must specify POSTGRES_PASSWORD"). Matches the
        # postgres://postgres:postgres@... string the app already shows.
        default_env={"POSTGRES_PASSWORD": "postgres"},
        health_check_type="pg_isready"
    ),
    ServiceDefinition(
        id="mysql",
        name="MySQL",
        category="database",
        image="mysql",
        default_port=3306,
        # Official image REFUSES to boot without one of these; empty root
        # password matches the app's mysql://root@localhost:PORT/ string.
        default_env={"MYSQL_ALLOW_EMPTY_PASSWORD": "yes"},
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
        id="couchdb",
        name="CouchDB",
        category="database",
        image="couchdb",
        default_port=5984,
        # CouchDB 3.x REFUSES admin-party boot (proven live: must specify
        # admin user+password). Dev defaults; /_up stays publicly readable.
        default_env={
            "COUCHDB_USER": "admin",
            "COUCHDB_PASSWORD": "admin",
        },
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
        category="queue",
        # apache/kafka boots standalone KRaft combined-mode with zero env
        # (official quickstart: `docker run -d --name broker apache/kafka`).
        # cp-kafka was dropped: it needs CLUSTER_ID + full KRaft env or ZK.
        image="apache/kafka",
        default_port=9092,
        default_env={},
        health_check_type="kafka_api_version"
    ),
    ServiceDefinition(
        id="nats",
        name="NATS",
        category="queue",
        image="nats",
        default_port=4222,
        default_env={},
        # nats image has no curl (code 127) so the in-container http check
        # cannot run; TCP-open on the client port is the honest check.
        health_check_type="tcp_port"
    ),

    # ===== SEARCH =====
    ServiceDefinition(
        id="elasticsearch",
        name="Elasticsearch",
        category="search",
        image="elasticsearch",
        default_port=9200,
        # Single-node dev boot without certs; keeps plain-http 9200 so the
        # http_get health check works.
        default_env={
            "discovery.type": "single-node",
            "xpack.security.enabled": "false",
        },
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
        # Exits without --data-dir (proven live; /data doesn't exist in the
        # image, /tmp does). Key stays env. No curl in image either, so the
        # keyed http check can't run in-container: tcp_port on 8108 instead.
        default_env={"TYPESENSE_API_KEY": "xyz"},
        default_command=["--data-dir", "/tmp"],
        health_check_type="tcp_port"
    ),

    # ===== STORAGE =====
    ServiceDefinition(
        id="minio",
        name="MinIO",
        category="storage",
        image="minio/minio",
        default_port=9000,
        # Explicit == image defaults; documents the console/API creds.
        default_env={
            "MINIO_ROOT_USER": "minioadmin",
            "MINIO_ROOT_PASSWORD": "minioadmin",
        },
        # REQUIRED: image prints help and exits without a server command.
        default_command=["server", "/data", "--console-address", ":9001"],
        health_check_type="http_get"
    ),
]


def get_service_by_image(image: str):
    for svc in SERVICES:
        if image.startswith(svc.image):
            return svc
    return None


def get_all_services():
    return SERVICES
