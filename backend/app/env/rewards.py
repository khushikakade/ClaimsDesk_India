"""
Step reward shaping: India Localized Context.
"""

from __future__ import annotations

from dataclasses import dataclass
from app.models import RewardComponents
from .scenarios import ClaimScenario


@dataclass
class RewardContext:
    """Per-step context for reward computation."""
    action_type: str
    category: str | None
    is_valid: bool
    is_redundant: bool
    revealed_new_info: bool
    cleared_contradiction_flag: bool
    matched_informative_inspect: bool
    matched_high_value_request: bool
    appropriate_inconsistency_flag: bool
    step_index: int
    budget_before: int
    terminal_decision: bool
    fraud_suspect_alignment: float
    low_value_request: bool
    investigation_request_count: int


# Tunable weights
W_INSPECT_INFORMATIVE = 0.12
W_REQUEST_VALUABLE = 0.15
W_REDUNDANT = -0.15
W_INVALID = -0.2
W_GOOD_INCONSISTENCY = 0.12
W_CLEAR_CONTRADICTION = 0.06
W_STEP_COST = -0.015
W_TRUNCATION = -0.35
W_LOW_VALUE_REQUEST = -0.08
W_OVER_INVESTIGATE = -0.06


def compute_step_reward(
    scenario: ClaimScenario,
    ctx: RewardContext,
    *,
    truncated: bool,
) -> RewardComponents:
    rc = RewardComponents()

    if not ctx.is_valid:
        rc.invalid_penalty = W_INVALID
        rc.total = rc.invalid_penalty
        return rc

    if ctx.is_redundant:
        rc.redundancy_penalty = W_REDUNDANT
        rc.total += rc.redundancy_penalty

    if ctx.category == "inspect":
        if ctx.matched_informative_inspect and ctx.revealed_new_info:
            rc.inspect_value = W_INSPECT_INFORMATIVE
        elif not ctx.revealed_new_info and not ctx.is_redundant:
            rc.inspect_value = W_STEP_COST
        rc.total += rc.inspect_value

    if ctx.category == "request":
        if ctx.matched_high_value_request:
            rc.request_value = W_REQUEST_VALUABLE
        elif ctx.low_value_request:
            rc.request_value = W_LOW_VALUE_REQUEST
        else:
            rc.request_value = W_STEP_COST * 1.8
        rc.total += rc.request_value

    if ctx.category == "assessment":
        base = W_STEP_COST + ctx.fraud_suspect_alignment
        if ctx.appropriate_inconsistency_flag:
            base += W_GOOD_INCONSISTENCY
        rc.assessment_value = base
        rc.total += rc.assessment_value

    if ctx.category == "routing":
        rc.routing_value = W_STEP_COST * 0.9
        rc.total += rc.routing_value

    if ctx.cleared_contradiction_flag:
        rc.total += W_CLEAR_CONTRADICTION

    # Efficiency
    if ctx.step_index > 22:
        rc.efficiency_penalty = -0.018
        rc.total += rc.efficiency_penalty
        
    if truncated:
        rc.efficiency_penalty += W_TRUNCATION
        rc.total += W_TRUNCATION

    rc.total += W_STEP_COST
    return rc


def append_decision_reward(
    rc: RewardComponents,
    decision_component: float,
) -> RewardComponents:
    rc.decision_value = decision_component
    rc.total += decision_component
    return rc
