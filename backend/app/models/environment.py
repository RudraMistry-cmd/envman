"""
Environment Config Model
========================

WHY: We need to know WHAT the user wants to build.
     "I want Node 20, Postgres 16, and Redis."

WHAT: A Pydantic model that defines the user's input.
      Pydantic automatically VALIDATES the input.
      If the user sends bad data, we catch it HERE, not in Docker.

HOW:
     New format:  { "services": [{ "name": "node", "image": "node:20" }, ...] }
     Legacy format: { "node": "20", "postgres": "16" }  (backward compatible)

THINK OF IT LIKE:
     A order form at a restaurant.
     You must fill in: dish name, quantity.
     If you leave them blank, the waiter asks you to fill them in.
"""

import re
from typing import List, Optional, Dict
from pydantic import BaseModel, model_validator


class ServiceSpec(BaseModel):
    """Specification for a single service."""

    name: str  # Must match ^[a-z0-9][a-z0-9-]*$ pattern
    image: str
    port: Optional[int] = None
    volume: Optional[str] = None  # format: "host_path:container_path"
    env: Optional[Dict[str, str]] = None

    def validate_name(self) -> bool:
        """Validate service name follows Docker naming conventions."""
        return bool(re.match(r'^[a-z0-9][a-z0-9-]*$', self.name))


class EnvironmentConfig(BaseModel):
    """What services and versions the user wants.

    Supports both new format (services list) and legacy format (node/postgres strings).
    """

    services: List[ServiceSpec]
    network_name: str = "envman_net"  # Default network name

    @model_validator(mode='before')
    @classmethod
    def convert_legacy_format(cls, data):
        """Convert legacy {node: str, postgres: str} format to services list.

        WHY: Backward compatibility — existing API calls must continue working.
        """
        if isinstance(data, dict) and 'node' in data and 'services' not in data:
            services = []
            if data.get('node'):
                services.append(ServiceSpec(
                    name="node",
                    image=f"node:{data['node']}"
                ))
            if data.get('postgres'):
                services.append(ServiceSpec(
                    name="postgres",
                    image=f"postgres:{data['postgres']}"
                ))
            return {'services': services}
        return data

    @model_validator(mode='after')
    def validate_service_names(self):
        """Ensure all service names follow Docker naming conventions."""
        for service in self.services:
            if not re.match(r'^[a-z0-9][a-z0-9-]*$', service.name):
                raise ValueError(
                    f"Service name '{service.name}' is invalid. "
                    "Must match pattern: ^[a-z0-9][a-z0-9-]*$"
                )
        return self
