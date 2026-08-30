"""
Logger Setup
============

WHY: Every part of EnvMan needs to talk to you.
     When something goes wrong, you need to see WHAT happened and WHERE.

WHAT: Configures Python's logging system so every module
     writes consistent, readable messages.

HOW: We set up one central logging configuration.
     Every module imports `get_logger("name")` and uses it.

EXAMPLE OUTPUT:
     [14:30:01] [executor] pulling image node:20
     [14:30:05] [executor] image pulled successfully
     [14:30:06] [verifier] checking postgres... ready
"""

import logging
import sys
from datetime import datetime, timezone


class EnvManFormatter(logging.Formatter):
    """Custom formatter that makes logs easy to read."""

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        level = record.levelname.lower()
        module = record.name.replace("envman.", "")
        message = record.getMessage()
        return f"[{timestamp}] [{module}] [{level}] {message}"


def setup_logging(level: str = "INFO") -> None:
    """Call this once when the app starts."""

    root = logging.getLogger("envman")
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(EnvManFormatter())
    root.addHandler(handler)

    root.info("logging initialized (level=%s)", level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Usage:
        logger = get_logger("executor")
        logger.info("pulling image node:20")
    """
    return logging.getLogger(f"envman.{name}")
