"""
Plan Model
==========

WHY: The planner produces a list of steps.
     We need a container to hold them.

WHAT: A list of Step objects, in order.

HOW:
     planner creates Plan(steps=[step1, step2, step3])
     coordinator reads plan.steps and runs them one by one
"""

from pydantic import BaseModel
from typing import List
from .step import Step


class Plan(BaseModel):
    """The full list of steps to set up the environment."""

    steps: List[Step]
    network_name: str = "envman_net"  # Network for this environment
