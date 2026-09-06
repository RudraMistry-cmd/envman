"""Tier 1: template definitions only reference registered services.

Guards the phase invariant: no template may need a runtime/service that
does not exist in the 14-service registry (e.g. no java/go/rust).
"""

import pytest

from app.registry.services import SERVICES
from app.registry.templates import (
    get_all_templates,
    get_template_by_id,
    template_to_config,
)


REGISTERED_IDS = {svc.id for svc in SERVICES}


class TestOnlyMernAndPythonWeb:
    def test_exactly_two_templates(self):
        assert {t.id for t in get_all_templates()} == {"mern", "python-web"}


class TestAllTemplateServicesRegistered:
    @pytest.mark.parametrize("template", get_all_templates(), ids=lambda t: t.id)
    def test_every_service_id_registered(self, template):
        for service in template.services:
            assert service.id in REGISTERED_IDS, (
                f"template '{template.id}' needs unregistered service '{service.id}'"
            )

    @pytest.mark.parametrize("template", get_all_templates(), ids=lambda t: t.id)
    def test_every_service_has_version(self, template):
        assert len(template.services) >= 2
        for service in template.services:
            assert service.version and isinstance(service.version, str)


class TestTemplateContents:
    def test_mern_pins(self):
        config = template_to_config(get_template_by_id("mern"))
        assert config == {"node": "20", "mongo": "7", "redis": "7"}

    def test_python_web_pins(self):
        config = template_to_config(get_template_by_id("python-web"))
        assert config == {"python": "3.12", "postgres": "16", "redis": "7"}

    def test_unknown_id_returns_none(self):
        assert get_template_by_id("java-spring") is None

    def test_config_matches_manual_picker_shape(self):
        # The picker state is {serviceId: version}; the template prefill must
        # be exactly that shape so handleStart builds identical payloads.
        config = template_to_config(get_template_by_id("mern"))
        assert set(config.keys()) == {"node", "mongo", "redis"}
        assert all(isinstance(v, str) for v in config.values())
