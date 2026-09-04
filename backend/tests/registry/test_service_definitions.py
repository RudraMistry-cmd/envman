"""Tier 1: Pure logic tests for registry/services.py — no Docker required."""

import pytest
import re
from app.registry.services import SERVICES, get_all_services, get_service_by_image


class TestServiceDefinitionHasRequiredFields:
    """Ensure every ServiceDefinition entry has all required fields."""

    @pytest.mark.parametrize("svc", SERVICES)
    def test_has_id(self, svc):
        assert svc.id is not None and isinstance(svc.id, str)

    @pytest.mark.parametrize("svc", SERVICES)
    def test_has_name(self, svc):
        assert svc.name is not None and isinstance(svc.name, str)

    @pytest.mark.parametrize("svc", SERVICES)
    def test_has_category(self, svc):
        assert svc.category is not None and isinstance(svc.category, str)

    @pytest.mark.parametrize("svc", SERVICES)
    def test_has_image(self, svc):
        assert svc.image is not None and isinstance(svc.image, str)

    @pytest.mark.parametrize("svc", SERVICES)
    def test_default_port_is_int_or_none(self, svc):
        """default_port should be an int or None — valid for all services."""
        assert svc.default_port is None or isinstance(svc.default_port, int)

    @pytest.mark.parametrize("svc", SERVICES)
    def test_has_default_env(self, svc):
        assert svc.default_env is not None

    @pytest.mark.parametrize("svc", SERVICES)
    def test_has_health_check_type(self, svc):
        assert svc.health_check_type is not None and isinstance(svc.health_check_type, str)


class TestNoDuplicateIds:
    """Ensure no two ServiceDefinition entries share the same id."""

    def test_no_duplicate_ids(self):
        ids = [svc.id for svc in SERVICES]
        assert len(ids) == len(set(ids)), f"Duplicate ids found: {[x for x in ids if ids.count(x) > 1]}"


class TestCategoryValues:
    """Ensure category values match what ConfigureScreen.jsx's CATEGORY_META expects."""

    VALID_CATEGORIES = {"runtime", "database", "cache", "queue", "search", "storage", "other"}

    @pytest.mark.parametrize("svc", SERVICES)
    def test_category_is_valid(self, svc):
        assert svc.category in self.VALID_CATEGORIES, (
            f"Invalid category '{svc.category}' for service '{svc.id}'. "
            f"Must be one of {self.VALID_CATEGORIES}"
        )


class TestServiceImagePrefixLookup:
    """Ensure get_service_by_image works correctly with the prefix-matching logic."""

    def test_get_service_by_image_for_node(self):
        svc = get_service_by_image("node:20")
        assert svc is not None
        assert svc.id == "node"

    def test_get_service_by_image_for_postgres(self):
        svc = get_service_by_image("postgres:16")
        assert svc is not None
        assert svc.id == "postgres"

    def test_get_service_by_image_for_confluent_kafka(self):
        svc = get_service_by_image("confluentinc/cp-kafka:7.5.16")
        assert svc is not None
        assert svc.id == "kafka"

    def test_get_service_by_image_returns_none_for_unknown(self):
        svc = get_service_by_image("notarealimage:xyz")
        assert svc is None


class TestAllServicesReturned:
    """Ensure get_all_services returns exactly the SERVICES list."""

    def test_get_all_services(self):
        all_svcs = get_all_services()
        assert len(all_svcs) == len(SERVICES)
        assert set(s.id for s in all_svcs) == set(s.id for s in SERVICES)


class TestServiceIdsMatchDockerNamingConventions:
    """Ensure all service IDs in the registry match Docker container naming patterns.

    Docker container names must match ^[a-z0-9][a-z0-9-]*$ — the service
    `id` field is used as the container name prefix (e.g. "envman_node").
    The `name` field can display friendly names with spaces, dots, etc."""

    @pytest.mark.parametrize("svc_entry", [
        {"id": "node", "name": "Node.js"},
        {"id": "python", "name": "Python"},
        {"id": "postgres", "name": "PostgreSQL"},
        {"id": "mysql", "name": "MySQL"},
        {"id": "mongo", "name": "MongoDB"},
        {"id": "redis", "name": "Redis"},
        {"id": "couchdb", "name": "CouchDB"},
        {"id": "rabbitmq", "name": "RabbitMQ"},
        {"id": "kafka", "name": "Kafka"},
        {"id": "nats", "name": "NATS"},
        {"id": "elasticsearch", "name": "Elasticsearch"},
        {"id": "meilisearch", "name": "MeiliSearch"},
        {"id": "typesense", "name": "Typesense"},
        {"id": "minio", "name": "MinIO"},
    ])
    def test_id_matches_docker_pattern(self, svc_entry):
        """Service IDs should match ^[a-z0-9][a-z0-9-]*$ pattern (Docker naming)."""
        name = svc_entry["id"]
        assert re.match(r'^[a-z0-9][a-z0-9-]*$', name), (
            f"Service ID '{name}' doesn't match Docker naming pattern ^[a-z0-9][a-z0-9-]*$"
        )


class TestServiceImagePrefixLookup:
    """Ensure get_service_by_image works correctly with the prefix-matching logic."""

    def test_get_service_by_image_for_node(self):
        svc = get_service_by_image("node:20")
        assert svc is not None
        assert svc.id == "node"

    def test_get_service_by_image_for_postgres(self):
        svc = get_service_by_image("postgres:16")
        assert svc is not None
        assert svc.id == "postgres"

    def test_get_service_by_image_for_confluent_kafka(self):
        svc = get_service_by_image("confluentinc/cp-kafka:7.5.16")
        assert svc is not None
        assert svc.id == "kafka"

    def test_get_service_by_image_returns_none_for_unknown(self):
        svc = get_service_by_image("notarealimage:xyz")
        assert svc is None


class TestAllServicesReturned:
    """Ensure get_all_services returns exactly the SERVICES list."""

    def test_get_all_services(self):
        all_svcs = get_all_services()
        assert len(all_svcs) == len(SERVICES)
        assert set(s.id for s in all_svcs) == set(s.id for s in SERVICES)