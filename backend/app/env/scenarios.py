"""
Scenario engine: India Localized (INR, ₹).
Diverse Insurance Domains (Health, Property, Vehicle).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from app.models import (
    ClaimMetadata,
    ClaimSummary,
    CoverageStatus,
    EvidenceBundle,
    IncidentType,
    InvestigationState,
    Observation,
    OperationalSignals,
    PolicyType,
    ClaimantRelationship,
    EpisodeState,
)

class DamageVeracity(str, Enum):
    ACCURATE = "accurate"
    INFLATED = "inflated"
    FABRICATED = "fabricated"

class HonestyLevel(str, Enum):
    TRUTHFUL = "truthful"
    PARTIAL = "partial"
    DECEPTIVE = "deceptive"

class OptimalResolution(str, Enum):
    APPROVE_FULL = "approve_full"
    APPROVE_PARTIAL = "approve_partial"
    DENY = "deny"
    ESCALATE_FRAUD = "escalate_fraud"
    CLOSE_INSUFFICIENT = "close_insufficient"
    SUPERVISOR = "supervisor"

@dataclass(frozen=True)
class HiddenTruth:
    """Internal only; India Context."""
    incident_occurred: bool
    damage_veracity: DamageVeracity
    coverage_applies: bool
    deductible_inr_applicable: float
    claimant_honesty: HonestyLevel
    urgency_legitimate: bool
    fraud_likelihood: float
    fair_payout_low_inr: float
    fair_payout_high_inr: float
    fair_value_target_inr: float
    optimal_resolution: OptimalResolution
    informative_inspect_keys: frozenset[str]
    high_value_requests: frozenset[str]
    has_real_contradiction: bool

@dataclass
class ClaimScenario:
    """One claim episode definition."""
    scenario_id: str
    task_id: str
    hidden: HiddenTruth
    max_steps: int = 40
    investigation_budget: int = 15
    document_catalog: dict[str, str] = field(default_factory=dict)
    inspect_map: dict[str, dict[str, Any]] = field(default_factory=dict)
    inspect_unlocks_flags: dict[str, list[str]] = field(default_factory=dict)
    request_fulfillment: dict[str, dict[str, Any]] = field(default_factory=dict)

    def build_initial_observation(self, task_id: str, step_count: int, max_steps: int, budget: int) -> Observation:
        meta, summary, evidence, ops = self._visible_slices_initial()
        return Observation(
            claim_metadata=meta,
            claim_summary=summary,
            evidence=evidence,
            operational_signals=ops,
            investigation=InvestigationState(),
            episode=EpisodeState(step_count=step_count, max_steps_remaining=max_steps - step_count, investigation_budget_remaining=budget),
            task_id=task_id,
        )

    def _visible_slices_initial(self) -> tuple[ClaimMetadata, ClaimSummary, EvidenceBundle, OperationalSignals]:
        raise NotImplementedError

# --- Scenario 1: StraightThrough (Life/Health) ------------------------------------

def scenario_straight_through() -> ClaimScenario:
    h = HiddenTruth(
        incident_occurred=True,
        damage_veracity=DamageVeracity.ACCURATE,
        coverage_applies=True,
        deductible_inr_applicable=5000.0,
        claimant_honesty=HonestyLevel.TRUTHFUL,
        urgency_legitimate=True,
        fraud_likelihood=0.05,
        fair_payout_low_inr=42000.0,
        fair_payout_high_inr=48000.0,
        fair_value_target_inr=45000.0,
        optimal_resolution=OptimalResolution.APPROVE_FULL,
        informative_inspect_keys=frozenset({"view_policy_details", "view_expert_estimate", "view_claim_summary"}),
        high_value_requests=frozenset(),
        has_real_contradiction=False,
    )
    meta = ClaimMetadata(
        claim_id="CLM-IND-ST",
        policy_id="POL-HEALTH-101",
        policy_type=PolicyType.HEALTH_CONCIERGE,
        policy_age_days=600,
        coverage_status=CoverageStatus.ACTIVE,
        deductible_inr=5000.0,
        incident_date="2026-03-20",
        filing_date="2026-03-21",
        claimant_relationship=ClaimantRelationship.NAMED_INSURED,
        requested_payout_inr=45000.0,
        asset_descriptor="Arjun Mehta (Insured Person)",
    )
    summary = ClaimSummary(
        incident_type=IncidentType.HEALTH_SURGERY,
        claimant_narrative="Emergency appendectomy performed at Nanavati Hospital, Mumbai. Surgery was successful.",
        reported_loss_summary="Hospitalization, surgical fees, and post-op medication.",
        reported_location="Nanavati Super Speciality Hospital, Vile Parle, Mumbai",
        reported_involved_parties="Self",
    )
    evidence = EvidenceBundle(
        available_documents=["discharge_summary", "final_bill"],
        document_summaries={
            "discharge_summary": "Discharge Summary: Acute appendicitis confirmed. Surgery performed 2026-03-20.",
            "final_bill": "Final Bill: Total ₹45,000. Includes room rent, OT charges, and medicines."
        },
        expert_estimate_summary="Hospital bill matches standard TP rates for this geography.",
    )
    ops = OperationalSignals(urgency_score=0.2, estimated_severity=0.1, contradiction_flags=[], prior_claim_count=0, sla_pressure=0.2, current_confidence=0.9, fraud_triage_score=0.05)
    
    class _ST(ClaimScenario):
        def _visible_slices_initial(self) -> tuple[ClaimMetadata, ClaimSummary, EvidenceBundle, OperationalSignals]:
            return meta, summary, evidence.model_copy(), ops.model_copy()

    return _ST(
        scenario_id="sc_straight_through",
        task_id="StraightThrough",
        hidden=h,
        document_catalog={
            "discharge_summary": evidence.document_summaries["discharge_summary"],
            "final_bill": evidence.document_summaries["final_bill"],
        },
        inspect_map={
            "view_expert_estimate": {"update_field": "expert_estimate_summary", "value": "Hospital bill ₹45,000 verified against insurance tariff."},
        }
    )

# --- Scenario 2: MissingButLegit (Property Fire) ----------------------------------

def scenario_missing_but_legit() -> ClaimScenario:
    h = HiddenTruth(
        incident_occurred=True,
        damage_veracity=DamageVeracity.ACCURATE,
        coverage_applies=True,
        deductible_inr_applicable=25000.0,
        claimant_honesty=HonestyLevel.PARTIAL,
        urgency_legitimate=True,
        fraud_likelihood=0.15,
        fair_payout_low_inr=750000.0,
        fair_payout_high_inr=900000.0,
        fair_value_target_inr=850000.0,
        optimal_resolution=OptimalResolution.APPROVE_FULL,
        informative_inspect_keys=frozenset({"view_expert_estimate", "view_official_report"}),
        high_value_requests=frozenset({"request_fire_dept_report"}),
        has_real_contradiction=True,
    )
    meta = ClaimMetadata(
        claim_id="CLM-IND-MBL",
        policy_id="POL-FIRE-202",
        policy_type=PolicyType.PROPERTY_ALL_RISK,
        policy_age_days=1200,
        coverage_status=CoverageStatus.ACTIVE,
        deductible_inr=25000.0,
        incident_date="2026-02-15",
        filing_date="2026-02-16",
        claimant_relationship=ClaimantRelationship.NAMED_INSURED,
        requested_payout_inr=850000.0,
        asset_descriptor="Residential Villa, Delhi (GK-II)",
    )
    summary = ClaimSummary(
        incident_type=IncidentType.PROPERTY_FIRE,
        claimant_narrative="Fire broke out in the kitchen due to an electrical short circuit. Significant damage to the first floor.",
        reported_loss_summary="Kitchen cabinets, electrical wiring, and living room furniture destroyed.",
        reported_location="Greater Kailash Part II, New Delhi",
        reported_involved_parties="Self, Local Fire Brigade",
    )
    evidence = EvidenceBundle(
        available_documents=["damage_photos", "survey_report_prelim"],
        missing_documents=["fire_dept_report"],
        document_summaries={
            "damage_photos": "Photos: Extensive charring in kitchen; smoke damage in living room.",
            "survey_report_prelim": "Surveyor Note: Preliminary loss assessed at ₹8.5 Lakh. Fire cause appears accidental."
        }
    )
    ops = OperationalSignals(urgency_score=0.8, estimated_severity=0.7, contradiction_flags=["fire_cause_unverified"], prior_claim_count=0, sla_pressure=0.6, current_confidence=0.5, fraud_triage_score=0.18)

    class _MBL(ClaimScenario):
        def _visible_slices_initial(self) -> tuple[ClaimMetadata, ClaimSummary, EvidenceBundle, OperationalSignals]:
            return meta, summary, evidence.model_copy(), ops.model_copy()

    return _MBL(
        scenario_id="sc_missing_but_legit",
        task_id="MissingButLegit",
        hidden=h,
        document_catalog={
            "fire_report_official": "Delhi Fire Service: Short circuit confirmed in kitchen. Accidental fire."
        },
        request_fulfillment={
            "request_fire_dept_report": {
                "add_docs": ["fire_report_official"],
                "clear_flags": ["fire_cause_unverified"],
                "notes": "Fire department report received; cause matches claimant's statement."
            }
        }
    )

# --- Scenario 3: InflatedCollision (Vehicle) --------------------------------------

def scenario_inflated_collision() -> ClaimScenario:
    h = HiddenTruth(
        incident_occurred=True,
        damage_veracity=DamageVeracity.INFLATED,
        coverage_applies=True,
        deductible_inr_applicable=10000.0,
        claimant_honesty=HonestyLevel.DECEPTIVE,
        urgency_legitimate=False,
        fraud_likelihood=0.65,
        fair_payout_low_inr=120000.0,
        fair_payout_high_inr=150000.0,
        fair_value_target_inr=135000.0,
        optimal_resolution=OptimalResolution.APPROVE_PARTIAL,
        informative_inspect_keys=frozenset({"view_expert_estimate", "view_witness_statement"}),
        high_value_requests=frozenset({"request_official_report"}),
        has_real_contradiction=True,
    )
    meta = ClaimMetadata(
        claim_id="CLM-IND-INF",
        policy_id="POL-MOTOR-303",
        policy_type=PolicyType.MOTOR_PACKAGE,
        policy_age_days=150,
        coverage_status=CoverageStatus.ACTIVE,
        deductible_inr=10000.0,
        incident_date="2026-03-05",
        filing_date="2026-03-06",
        claimant_relationship=ClaimantRelationship.NAMED_INSURED,
        requested_payout_inr=210000.0,
        asset_descriptor="2022 Maruti Suzuki Grand Vitara (Blue)",
    )
    summary = ClaimSummary(
        incident_type=IncidentType.VEHICLE_COLLISION,
        claimant_narrative="Sideswiped by a truck on Bangalore Electronic City Flyover. Impact damaged the entire driver side and structural pillars.",
        reported_loss_summary="Both doors, fender, and B-pillar damage.",
        reported_location="Electronic City Flyover, Bangalore",
        reported_involved_parties="Self, Unnamed Truck Driver",
    )
    evidence = EvidenceBundle(
        available_documents=["exterior_photos", "estimate_workshop"],
        document_summaries={
            "exterior_photos": "Photos: Scrapes on driver-side doors; fender dented. Pillars appear intact.",
            "estimate_workshop": "Workshop Estimate: ₹2,10,000 (includes structural replacement)."
        }
    )
    ops = OperationalSignals(urgency_score=0.9, estimated_severity=0.8, contradiction_flags=["damage_inflation_suspected"], prior_claim_count=1, sla_pressure=0.8, current_confidence=0.4, fraud_triage_score=0.55)

    class _INF(ClaimScenario):
        def _visible_slices_initial(self) -> tuple[ClaimMetadata, ClaimSummary, EvidenceBundle, OperationalSignals]:
            return meta, summary, evidence.model_copy(), ops.model_copy()

    return _INF(
        scenario_id="sc_inflated_collision",
        task_id="InflatedCollision",
        hidden=h,
        document_catalog={
            "independent_surveyor": "Independent Surveyor Note: Structural damage is non-existent. Fair repair cost is ₹1.35 Lakh."
        },
        inspect_map={
            "view_expert_estimate": {"update_field": "expert_estimate_summary", "value": "Survey confirms inflation; workshop estimate is 50% above fair market value."}
        }
    )

# --- Registry --------------------------------------------------------------------

def _scenario_factories() -> dict[str, Any]:
    return {
        "sc_straight_through": scenario_straight_through,
        "sc_missing_but_legit": scenario_missing_but_legit,
        "sc_inflated_collision": scenario_inflated_collision,
    }

TASK_TO_SCENARIO_ID: dict[str, str] = {
    "StraightThrough": "sc_straight_through",
    "MissingButLegit": "sc_missing_but_legit",
    "InflatedCollision": "sc_inflated_collision",
}

class ScenarioRegistry:
    def __init__(self) -> None:
        self._factories = _scenario_factories()

    def get_scenario(self, task_id: str, seed: int) -> ClaimScenario:
        sid = TASK_TO_SCENARIO_ID.get(task_id)
        if sid is None: raise KeyError(f"Unknown task: {task_id}")
        return self._factories[sid]()
