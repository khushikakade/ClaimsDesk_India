"""Environment configuration."""

from __future__ import annotations
import os
from pydantic import BaseModel, Field

class ClaimsDeskSettings(BaseModel):
    default_max_steps: int = Field(default=45, ge=1)
    default_investigation_budget: int = Field(default=16, ge=0)

    @classmethod
    def from_env(cls) -> ClaimsDeskSettings:
        return cls(
            default_max_steps=int(os.getenv("CLAIMSDESK_DEFAULT_MAX_STEPS", "45")),
            default_investigation_budget=int(os.getenv("CLAIMSDESK_DEFAULT_INVESTIGATION_BUDGET", "16")),
        )
