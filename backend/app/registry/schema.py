"""
WHY:
We need a canonical definition for known services so that verification
logic is not inferred from image string matching.

WHAT:
Defines ServiceDefinition — a structured contract describing a service,
its defaults, and how it should be verified.

HOW:
Used by verifier to dispatch correct health checks.

THINK OF IT LIKE:
A type system for services — instead of guessing behavior from strings,
we declare it explicitly.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel


class ServiceCategory(str, Enum):
    RUNTIME = "runtime"
    DATABASE = "database"
    CACHE = "cache"
    QUEUE = "queue"
    SEARCH = "search"
    STORAGE = "storage"
    MONITORING = "monitoring"
    PROXY = "proxy"
    MESSAGE_BROKER = "message_broker"
    OTHER = "other"


class ServiceDefinition(BaseModel):
    """Complete definition of a service type."""
    id: str
    name: str
    category: ServiceCategory
    image: str  # Docker image prefix (e.g., "postgres", "redis")
    default_port: Optional[int] = None
    default_env: Dict[str, str] = {}
    health_check_type: str  # "pg_isready", "redis_ping", "node_version", "tcp_port"
