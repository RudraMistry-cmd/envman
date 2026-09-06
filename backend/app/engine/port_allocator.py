"""
Smart Port Allocator
====================

WHY: Hard-coded default ports (5432 for Postgres, 6379 for Redis) collide when
     multiple environments run simultaneously or local host daemons occupy ports.
     Instead of failing, we detect occupied ports and automatically allocate the
     next available free port.

WHAT: Automatically assign ports to avoid conflicts (TECHNICAL_SPEC.md Part 7 §3).
      - Checks system port availability via socket bind.
      - Tracks allocated ports within EnvMan.
      - Tries preferred port, candidate sequential offsets, service common ports,
        and finally ephemeral range.
"""

import socket
from typing import Dict, List, Optional
from app.utils.logger import get_logger

logger = get_logger("port_allocator")


class NoPortAvailableError(Exception):
    """Raised when no free host port can be found."""
    pass


class PortAllocator:
    """Automatically assign ports to avoid conflicts (TECHNICAL_SPEC.md Part 7 §3)."""

    COMMON_PORTS = {
        "node": [3000, 3001, 8080],
        "python": [8000, 8080, 5000],
        "postgres": [5432],
        "mysql": [3306],
        "mongodb": [27017],
        "redis": [6379],
        "elasticsearch": [9200],
        "rabbitmq": [5672, 15672],
        "kafka": [9092],
        "nginx": [80, 443],
        "grafana": [3000],
        "prometheus": [9090],
    }

    def __init__(self):
        self.allocated: Dict[int, str] = {}

    def is_available(self, port: int) -> bool:
        """Check if port is available on the system and not already allocated."""
        if port is None or port <= 0 or port > 65535:
            return False
        if port in self.allocated:
            return False
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("0.0.0.0", port))
            return True
        except OSError:
            return False

    def allocate(self, service_name: str, preferred_port: Optional[int] = None) -> int:
        """Find an available port for a service.

        1. If preferred_port is specified and available, use it.
        2. If preferred_port is specified but occupied, try sequential offsets (1..100).
        3. If no preferred_port, try common ports for this service type.
        4. Fallback to ephemeral range (49152..65535).
        """
        # Clean service name for COMMON_PORTS lookup
        lookup_name = service_name.replace("envman_", "") if service_name.startswith("envman_") else service_name

        if preferred_port is not None and preferred_port > 0:
            if self.is_available(preferred_port):
                self.allocated[preferred_port] = service_name
                logger.info("allocated preferred port %d for '%s'", preferred_port, service_name)
                return preferred_port

            logger.info("preferred port %d for '%s' is in use, searching next available", preferred_port, service_name)
            # Find next available in range
            for offset in range(1, 100):
                candidate = preferred_port + offset
                if candidate <= 65535 and self.is_available(candidate):
                    self.allocated[candidate] = service_name
                    logger.info("reassigned '%s' from port %d to port %d", service_name, preferred_port, candidate)
                    return candidate

        # Use common ports for service type
        common = self.COMMON_PORTS.get(lookup_name, [8000])
        for port in common:
            if self.is_available(port):
                self.allocated[port] = service_name
                logger.info("allocated common port %d for '%s'", port, service_name)
                return port

        # Fallback to ephemeral range
        for port in range(49152, 65535):
            if self.is_available(port):
                self.allocated[port] = service_name
                logger.info("allocated ephemeral port %d for '%s'", port, service_name)
                return port

        raise NoPortAvailableError(f"No available port found for service '{service_name}'")

    def release(self, port: int):
        """Release an allocated port."""
        removed = self.allocated.pop(port, None)
        if removed:
            logger.info("released port %d (was allocated to '%s')", port, removed)

    def get_allocation_map(self) -> Dict[str, int]:
        """Get service -> port mapping."""
        return {service: port for port, service in self.allocated.items()}


# Global singleton instance for runtime port allocation
port_allocator = PortAllocator()
