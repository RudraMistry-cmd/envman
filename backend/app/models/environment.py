"""
Environment Config Model
========================

WHY: We need to know WHAT the user wants to build.
     "I want Node 20 and Postgres 16."

WHAT: A Pydantic model that defines the user's input.
     Pydantic automatically VALIDATES the input.
     If the user sends bad data, we catch it HERE, not in Docker.

HOW:
     User sends:  { "node": "20", "postgres": "16" }
     Pydantic checks: Are these strings? Are they present?
     If valid → we proceed
     If invalid → we return a clear error message

THINK OF IT LIKE:
     A order form at a restaurant.
     You must fill in: dish name, quantity.
     If you leave them blank, the waiter asks you to fill them in.
"""

from pydantic import BaseModel, field_validator


class EnvironmentConfig(BaseModel):
    """What services and versions the user wants."""

    node: str
    postgres: str

    @field_validator("node")
    @classmethod
    def validate_node(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("node version cannot be empty")
        return v

    @field_validator("postgres")
    @classmethod
    def validate_postgres(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("postgres version cannot be empty")
        return v
