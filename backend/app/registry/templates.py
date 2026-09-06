"""
WHY:
Clicking through six category pickers for the same standard stack every
time is tedious. A template is just a predefined set of {service id,
version} selections that pre-fills the picker.

WHAT:
Two template definitions whose services ALL already exist in the
14-service registry. No new runtimes, no startup ordering - selecting a
template produces the exact same config state (and /setup payload) as
picking each service manually.

HOW:
Frontend fetches GET /templates, renders a card per entry, and on select
sets config to {serviceId: version} for that template's services.
"""

from typing import Dict, List
from pydantic import BaseModel


class TemplateService(BaseModel):
    """One pinned service inside a template."""

    id: str  # must match a ServiceDefinition id in services.py
    version: str  # must match a version offered by the frontend picker


class Template(BaseModel):
    """A named, pre-filled service selection."""

    id: str
    name: str
    description: str
    services: List[TemplateService]


TEMPLATES = [
    Template(
        id="mern",
        name="MERN Stack",
        description="Node.js API + MongoDB database + Redis cache.",
        services=[
            TemplateService(id="node", version="20"),
            TemplateService(id="mongo", version="7"),
            TemplateService(id="redis", version="7"),
        ],
    ),
    Template(
        id="python-web",
        name="Python Web App",
        description="Python runtime + PostgreSQL database + Redis cache.",
        services=[
            TemplateService(id="python", version="3.12"),
            TemplateService(id="postgres", version="16"),
            TemplateService(id="redis", version="7"),
        ],
    ),
]


def get_all_templates() -> List[Template]:
    return TEMPLATES


def get_template_by_id(template_id: str) -> Template | None:
    for template in TEMPLATES:
        if template.id == template_id:
            return template
    return None


def template_to_config(template: Template) -> Dict[str, str]:
    """Return the {serviceId: version} config state selecting this template
    produces - identical to manual one-by-one picks."""
    return {service.id: service.version for service in template.services}
