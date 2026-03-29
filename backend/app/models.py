"""
Typed Pydantic models for observations, actions, rewards, and environment I/O.
Localized for India (INR, ₹).
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ActionCategory(str, Enum):
    INSPECT = "inspect"
    REQUEST = "request"
    ASSESSMENT = "assessment"
    ROUTING = "routing"
    DECISION = "decision"


class IncidentType(str, Enum):
    # Vehicle
    VEHICLE_COLLISION = "vehicle_collision"
    VEHICLE_THEFT = "vehicle_theft"
    # Health
    HEALTH_SURGERY = "health_surgery"
    HEALTH_CRITICAL_ILLNESS = "health_critical_illness"
    # Property
    PROPERTY_FIRE = "property_fire"
    PROPERTY_FLOOD = "property_flood"
    # Life/Travel
    LIFE_BENEFIT = "life_benefit"
    TRAVEL_CANCELLATION = "travel_cancellation"


class PolicyType(str, Enum):
    MOTOR_PACKAGE = "motor_package"
    HEALTH_CONCIERGE = "health_concierge"
    PROPERTY_ALL_RISK = "property_all_risk"
    LIFE_TERM = "life_term"
    TRAVEL_WORLD = "travel_world"


class CoverageStatus(str, Enum):
    ACTIVE = "active"
    LAPSED = "lapsed"
    PENDING_RENEWAL = "pending_renewal"


class ClaimantRelationship(str, Enum):
    NAMED_INSURED = "named_insured"
    SPOUSE = "spouse"
    DEPENDENT = "dependent"
    THIRD_PARTY = "third_party"


class TerminationReason(str, Enum):
    DECISION = "decision"
    MAX_STEPS = "max_steps"
    BUDGET_EXHAUSTED = "budget_exhausted"
    ALREADY_DONE = "already_done"
    NONE = "none"


# ---------------------------------------------------------------------------
# Observation sub-models (claims operations dashboard)
# ---------------------------------------------------------------------------


class ClaimMetadata(BaseModel):
    claim_id: str
    policy_id: str
    policy_type: PolicyType
    policy_age_days: int = Field(ge=0)
    coverage_status: CoverageStatus
    deductible_inr: float = Field(ge=0)
    incident_date: str
    filing_date: str
    claimant_relationship: ClaimantRelationship
    requested_payout_inr: float = Field(ge=0)
    # Operational realism (visible; not ground truth)
    external_reference_id: str = ""
    asset_descriptor: str = ""  # General name for car, house, person


class ClaimSummary(BaseModel):
    incident_type: IncidentType
    claimant_narrative: str
    reported_loss_summary: str
    reported_location: str
    reported_involved_parties: str


class EvidenceBundle(BaseModel):
    available_documents: list[str] = Field(default_factory=list)
    missing_documents: list[str] = Field(default_factory=list)
    document_summaries: dict[str, str] = Field(default_factory=dict)
    expert_estimate_summary: str = ""
    witness_statement_summary: str = ""
    official_report_summary: str = ""  # Police or IRDAI/Surveyor
    prior_claims_summary: str = ""


class OperationalSignals(BaseModel):
    urgency_score: float = Field(ge=0, le=1)
    estimated_severity: float = Field(ge=0, le=1)
    contradiction_flags: list[str] = Field(default_factory=list)
    anomaly_flags: list[str] = Field(default_factory=list)
    prior_claim_count: int = Field(ge=0)
    sla_pressure: float = Field(ge=0, le=1)
    current_confidence: float = Field(ge=0, le=1)
    fraud_triage_score: float = Field(ge=0, le=1, default=0.35)


class InvestigationState(BaseModel):
    reviewed_items: list[str] = Field(default_factory=list)
    requested_items: list[str] = Field(default_factory=list)
    pending_requests: list[str] = Field(default_factory=list)
    notes_or_findings: list[str] = Field(default_factory=list)


class EpisodeState(BaseModel):
    step_count: int = Field(ge=0)
    max_steps_remaining: int = Field(ge=0)
    investigation_budget_remaining: int = Field(ge=0)


class Observation(BaseModel):
    """Structured claims desk dashboard visible to the agent."""

    claim_metadata: ClaimMetadata
    claim_summary: ClaimSummary
    evidence: EvidenceBundle
    operational_signals: OperationalSignals
    investigation: InvestigationState
    episode: EpisodeState
    task_id: str = ""
    routing_queue: str = "standard_intake"


class RewardComponents(BaseModel):
    """Optional breakdown for debugging, tests, and analysis."""

    total: float = 0.0
    inspect_value: float = 0.0
    request_value: float = 0.0
    assessment_value: float = 0.0
    routing_value: float = 0.0
    decision_value: float = 0.0
    efficiency_penalty: float = 0.0
    redundancy_penalty: float = 0.0
    invalid_penalty: float = 0.0


class EnvInfo(BaseModel):
    """Step metadata; never contains hidden truth."""

    termination_reason: TerminationReason = TerminationReason.NONE
    truncated: bool = False
    invalid_action: bool = False
    invalid_reason: str | None = None
    reward_breakdown: RewardComponents | None = None
    extra: dict[str, Any] = Field(default_factory=dict)


class StepResult(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: EnvInfo = Field(default_factory=EnvInfo)


# ---------------------------------------------------------------------------
# Action space
# ---------------------------------------------------------------------------

INSPECT_ACTIONS = frozenset(
    {
        "view_claim_summary",
        "view_policy_details",
        "view_expert_estimate",
        "view_claim_history",
        "view_witness_statement",
        "view_official_report",
        "view_document",
    }
)
REQUEST_ACTIONS = frozenset(
    {
        "request_official_report",
        "request_repair_invoice",
        "request_medical_bills",
        "request_fire_dept_report",
        "request_witness_confirmation",
        "request_timeline_clarification",
    }
)
ASSESSMENT_ACTIONS = frozenset(
    {
        "mark_claim_low_risk",
        "mark_claim_high_risk",
        "flag_inconsistency",
        "mark_coverage_uncertain",
        "mark_fraud_suspected",
        "set_priority_urgent",
        "set_priority_standard",
    }
)
ROUTING_ACTIONS = frozenset(
    {
        "route_to_fast_track",
        "route_to_manual_review",
        "escalate_to_fraud_investigation",
        "escalate_to_supervisor",
        "route_to_settlement_queue",
    }
)
DECISION_ACTIONS = frozenset(
    {
        "approve_claim",
        "deny_claim",
        "offer_partial_settlement",
        "close_for_insufficient_evidence",
    }
)

ALL_ACTION_TYPES = (
    INSPECT_ACTIONS
    | REQUEST_ACTIONS
    | ASSESSMENT_ACTIONS
    | ROUTING_ACTIONS
    | DECISION_ACTIONS
)


def action_category(action_type: str) -> ActionCategory | None:
    if action_type in INSPECT_ACTIONS:
        return ActionCategory.INSPECT
    if action_type in REQUEST_ACTIONS:
        return ActionCategory.REQUEST
    if action_type in ASSESSMENT_ACTIONS:
        return ActionCategory.ASSESSMENT
    if action_type in ROUTING_ACTIONS:
        return ActionCategory.ROUTING
    if action_type in DECISION_ACTIONS:
        return ActionCategory.DECISION
    return None


def is_terminal_action(action_type: str) -> bool:
    return action_type in DECISION_ACTIONS


class Action(BaseModel):
    """Single claims-desk operation."""

    action_type: str
    target: str | None = None
    rationale: str | None = None
    amount_inr: float | None = Field(default=None, ge=0)
    reason_code: str | None = None


class VisibleEnvState(BaseModel):
    """Serializable visible state for state(); no hidden fields."""

    observation: Observation
    last_action_valid: bool = True
    trajectory_length: int = 0
