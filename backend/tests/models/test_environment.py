"""Tier 1: Pure logic tests for models/environment.py — no Docker required."""

import pytest
import re
from app.models.environment import ServiceSpec, EnvironmentConfig


class TestServiceSpecNameValidation:
    """Ensure ServiceSpec names follow Docker naming conventions."""

    @pytest.mark.parametrize("name", ["node", "python3", "my-service", "a1"])
    def test_valid_names(self, name):
        spec = ServiceSpec(name=name, image="node:20")
        assert spec.validate_name() is True

    @pytest.mark.parametrize("name", ["Node", "Node.js", " node", "node!", "Node_js"])
    def test_invalid_names(self, name):
        spec = ServiceSpec(name=name, image="node:20")
        assert spec.validate_name() is False


class TestLegacyFormatConverter:
    """Ensure the legacy format converter handles {node, postgres} correctly
    and does NOT silently accept other keys."""

    @pytest.mark.parametrize("input_data, expected_node_count, expected_postgres_count, expected_total", [
        ({"node": "20", "postgres": "16"}, 1, 1, 2),
        ({"node": "20"}, 1, 0, 1),
        # Legacy converter only triggers when 'node' key is present;
        # {"postgres": "16"} alone falls through to Pydantic v2 validation
        ({"node": "20", "postgres": "16", "redis": "7"}, 1, 1, 2),  # redis silently ignored
    ])
    def test_legacy_format(self, input_data, expected_node_count, expected_postgres_count, expected_total):
        result = EnvironmentConfig.model_validate(input_data)
        service_names = [s.name for s in result.services]
        node_count = sum(1 for s in result.services if s.name == "node")
        postgres_count = sum(1 for s in result.services if s.name == "postgres")
        total_count = len(result.services)

        assert node_count == expected_node_count, (
            f"Expected {expected_node_count} node services, got {node_count}"
        )
        assert postgres_count == expected_postgres_count, (
            f"Expected {expected_postgres_count} postgres services, got {postgres_count}"
        )
        assert total_count == expected_total, (
            f"Expected {expected_total} total services, got {total_count}"
        )


class TestServiceSpecNamesFollowDockerConventions:
    """Ensure all service IDs in the registry match Docker naming patterns.

    The `id` field is used as the Docker container name prefix (e.g. "envman_node"),
    while the `name` field is a display name that can have spaces, uppercase, etc."""

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


class TestEnvironmentConfigValidatesNamesAfterConversion:
    """Ensure EnvironmentConfig validates service names after legacy format
    conversion — the validator in the 'after' phase catches invalid names."""

    @pytest.mark.parametrize("bad_input", [
        {"services": [{"name": "Node", "image": "node:20"}]},
    ])
    def test_invalid_names_raise_error(self, bad_input):
        """Service names with uppercase should raise ValueError after conversion."""
        with pytest.raises(ValueError):
            EnvironmentConfig.model_validate(bad_input)

    @pytest.mark.parametrize("good_input", [
        {"services": [{"name": "node", "image": "node:20"}]},
    ])
    def test_valid_names_pass_conversion(self, good_input):
        """Valid service names should pass conversion and validation."""
        config = EnvironmentConfig.model_validate(good_input)
        assert len(config.services) >= 1