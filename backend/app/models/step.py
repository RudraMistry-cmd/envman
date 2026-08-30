"""
Step Model
==========

WHY: The planner breaks the setup into small, clear actions.
     Each action is a "step."

WHAT: One step = one thing to do.
     Examples:
       - Pull the node:20 image from Docker Hub
       - Start the postgres container

HOW:
     Each step has:
       - id:        unique name (like "pull_node")
       - type:      what kind of step (pull_image, start_container)
       - params:    the details (which image, which port, etc.)
       - depends_on: what must finish BEFORE this step runs

THINK OF IT LIKE:
     A recipe.
     Step 1: "Preheat oven" (no dependencies)
     Step 2: "Mix flour" (no dependencies)
     Step 3: "Put cake in oven" (depends on: Step 1 AND Step 2)
"""

from pydantic import BaseModel
from typing import Optional, Dict


class Step(BaseModel):
    """One action in the setup plan."""

    id: str
    type: str
    params: Dict
    depends_on: Optional[str] = None
