"""
ClaimsDesk environment: India Localized (INR, ₹).
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.models import Action, EnvInfo, Observation, StepResult, TerminationReason, VisibleEnvState
from .actions import is_terminal_operation, validate_action
from .config import ClaimsDeskSettings
from .graders import TrajectoryRecord
from .rewards import RewardContext, append_decision_reward, compute_step_reward
from .scenarios import ClaimScenario, OptimalResolution, ScenarioRegistry

VERSION = "1.0.0-in"

def _review_key(action_type: str, target: str | None) -> str:
    if action_type == "view_document" and target:
        return f"view_document:{target}"
    return action_type


def _decision_shaped_reward(scenario: ClaimScenario, action_type: str, amount: float | None) -> float:
    """Dense terminal reward using hidden truth."""
    h = scenario.hidden
    lo, hi = h.fair_payout_low_inr, h.fair_payout_high_inr
    opt = h.optimal_resolution

    if action_type == "approve_claim":
        if opt == OptimalResolution.APPROVE_FULL:
            if amount is not None and lo <= amount <= hi:
                return 0.45
            return 0.35
        if opt == OptimalResolution.APPROVE_PARTIAL:
            return 0.15
        return -0.15

    if action_type == "offer_partial_settlement":
        if opt == OptimalResolution.APPROVE_PARTIAL:
            if amount is not None and lo <= amount <= hi:
                return 0.45
            if amount is not None:
                return 0.25
            return 0.15
        if opt == OptimalResolution.APPROVE_FULL:
            return 0.2
        return 0.0

    if action_type == "deny_claim":
        if opt == OptimalResolution.DENY:
            return 0.45
        if h.coverage_applies and h.incident_occurred:
            return -0.35
        return 0.1

    if action_type == "close_for_insufficient_evidence":
        if opt == OptimalResolution.CLOSE_INSUFFICIENT:
            return 0.4
        return 0.05

    if action_type == "escalate_to_fraud_investigation":
        if opt == OptimalResolution.ESCALATE_FRAUD:
            return 0.45
        if h.fraud_likelihood > 0.5:
            return 0.2
        return -0.15

    if action_type == "escalate_to_supervisor":
        if opt == OptimalResolution.SUPERVISOR:
            return 0.4
        return 0.1

    return 0.0


class ClaimsDeskEnv:
    """Single-claim insurance desk simulation localized for India."""

    task_id: str
    seed: int
    settings: ClaimsDeskSettings
    _registry: ScenarioRegistry
    _scenario: ClaimScenario | None
    _observation: Observation | None
    _done: bool
    _trajectory: TrajectoryRecord
    _max_steps: int
    _budget: int
    _last_action_valid: bool

    def __init__(
        self,
        task_id: str,
        seed: int = 0,
        settings: ClaimsDeskSettings | None = None,
    ) -> None:
        self.task_id = task_id
        self.seed = seed
        self.settings = settings or ClaimsDeskSettings.from_env()
        self._registry = ScenarioRegistry()
        self._scenario = None
        self._observation = None
        self._done = False
        self._trajectory = TrajectoryRecord()
        self._max_steps = 0
        self._budget = 0
        self._last_action_valid = True

    def reset(self) -> Observation:
        self._scenario = self._registry.get_scenario(self.task_id, self.seed)
        assert self._scenario is not None
        sc = self._scenario
        self._max_steps = min(sc.max_steps, self.settings.default_max_steps)
        self._budget = min(sc.investigation_budget, self.settings.default_investigation_budget)
        self._done = False
        self._trajectory = TrajectoryRecord()
        self._last_action_valid = True
        self._observation = sc.build_initial_observation(
            task_id=self.task_id,
            step_count=0,
            max_steps=self._max_steps,
            budget=self._budget,
        )
        return self._observation.model_copy(deep=True)

    def state(self) -> VisibleEnvState:
        if self._observation is None:
            raise RuntimeError("Call reset() before state()")
        return VisibleEnvState(
            observation=self._observation.model_copy(deep=True),
            last_action_valid=self._last_action_valid,
            trajectory_length=len(self._trajectory.actions),
        )

    def step(self, action: Action) -> StepResult:
        if self._observation is None or self._scenario is None:
            raise RuntimeError("Call reset() before step()")
        if self._done:
            info = EnvInfo(
                termination_reason=TerminationReason.ALREADY_DONE,
                truncated=False,
                invalid_action=True,
                invalid_reason="episode_already_done",
            )
            return StepResult(observation=self._observation.model_copy(deep=True), reward=-0.1, done=True, info=info)

        sc = self._scenario
        obs = self._observation
        vr = validate_action(action)
        
        if vr.valid and vr.category and vr.category.value == "request" and self._budget <= 0:
            self._last_action_valid = False
            rc = compute_step_reward(sc, RewardContext(action_type=action.action_type, category="request", is_valid=False, is_redundant=False, revealed_new_info=False, cleared_contradiction_flag=False, matched_informative_inspect=False, matched_high_value_request=False, appropriate_inconsistency_flag=False, step_index=obs.episode.step_count, budget_before=obs.episode.investigation_budget_remaining, terminal_decision=False, fraud_suspect_alignment=0.0, low_value_request=False, investigation_request_count=len(obs.investigation.requested_items)), truncated=False)
            info = EnvInfo(termination_reason=TerminationReason.NONE, invalid_action=True, invalid_reason="investigation_budget_exhausted", reward_breakdown=rc)
            return StepResult(observation=obs.model_copy(deep=True), reward=rc.total, done=False, info=info)

        if not vr.valid:
            self._last_action_valid = False
            rc = compute_step_reward(sc, RewardContext(action_type=action.action_type, category=None, is_valid=False, is_redundant=False, revealed_new_info=False, cleared_contradiction_flag=False, matched_informative_inspect=False, matched_high_value_request=False, appropriate_inconsistency_flag=False, step_index=obs.episode.step_count, budget_before=obs.episode.investigation_budget_remaining, terminal_decision=False, fraud_suspect_alignment=0.0, low_value_request=False, investigation_request_count=len(obs.investigation.requested_items)), truncated=False)
            info = EnvInfo(termination_reason=TerminationReason.NONE, invalid_action=True, invalid_reason=vr.reason, reward_breakdown=rc)
            return StepResult(observation=obs.model_copy(deep=True), reward=rc.total, done=False, info=info)

        self._last_action_valid = True
        rk = _review_key(action.action_type, action.target)
        is_redundant = rk in obs.investigation.reviewed_items or (vr.category and vr.category.value == "request" and action.action_type in obs.investigation.requested_items)

        self._trajectory.actions.append(action.action_type)
        cat = vr.category.value if vr.category else None
        revealed_new = False
        cleared_flag = False

        if vr.category and vr.category.value == "inspect":
            revealed_new = self._apply_inspect(action, rk)
        elif vr.category and vr.category.value == "request":
            if not is_redundant:
                cleared_flag = self._apply_request(action)
        elif vr.category and vr.category.value == "assessment":
            self._apply_assessment(action)
        elif vr.category and vr.category.value == "routing":
            self._apply_routing(action)

        terminal = is_terminal_operation(action.action_type)
        if terminal:
            self._apply_terminal(action)

        obs.episode.step_count += 1
        obs.episode.max_steps_remaining = max(0, self._max_steps - obs.episode.step_count)
        obs.episode.investigation_budget_remaining = self._budget

        truncated = False
        term_reason = TerminationReason.NONE
        if terminal:
            self._done = True
            term_reason = TerminationReason.DECISION
        elif obs.episode.step_count >= self._max_steps:
            truncated = True
            self._done = True
            term_reason = TerminationReason.MAX_STEPS
        elif not terminal and action.action_type.startswith("request") and self._budget <= 0:
            truncated = True
            self._done = True
            term_reason = TerminationReason.BUDGET_EXHAUSTED

        matched_inform = action.action_type in sc.hidden.informative_inspect_keys
        matched_req = action.action_type in sc.hidden.high_value_requests
        low_value_request = (cat == "request" and (len(sc.hidden.high_value_requests) == 0 or action.action_type not in sc.hidden.high_value_requests))

        fl = sc.hidden.fraud_likelihood
        fraud_align = 0.0
        if action.action_type == "mark_fraud_suspected":
            fraud_align = 0.06 if fl > 0.48 else (-0.12 if fl < 0.22 else -0.045)

        ctx = RewardContext(action_type=action.action_type, category=cat, is_valid=True, is_redundant=is_redundant, revealed_new_info=revealed_new, cleared_contradiction_flag=cleared_flag, matched_informative_inspect=matched_inform and revealed_new, matched_high_value_request=matched_req, appropriate_inconsistency_flag=(action.action_type == "flag_inconsistency" and sc.hidden.has_real_contradiction), step_index=obs.episode.step_count, budget_before=obs.episode.investigation_budget_remaining + (1 if action.action_type.startswith("request") else 0), terminal_decision=terminal, fraud_suspect_alignment=fraud_align, low_value_request=low_value_request, investigation_request_count=len(obs.investigation.requested_items))

        rc = compute_step_reward(sc, ctx, truncated=truncated and not terminal)
        if terminal:
            dr = _decision_shaped_reward(sc, action.action_type, action.amount_inr)
            append_decision_reward(rc, dr)

        reward = rc.total
        info = EnvInfo(termination_reason=term_reason, truncated=truncated, invalid_action=False, reward_breakdown=rc)
        
        self._trajectory.step_count = obs.episode.step_count
        self._trajectory.budget_remaining_end = obs.episode.investigation_budget_remaining
        self._trajectory.reviewed_items = list(obs.investigation.reviewed_items)
        self._trajectory.requested_items = list(obs.investigation.requested_items)

        return StepResult(observation=obs.model_copy(deep=True), reward=reward, done=self._done, info=info)

    def get_trajectory_record(self) -> TrajectoryRecord:
        return deepcopy(self._trajectory)

    def get_metadata(self) -> dict[str, Any]:
        sc = self._scenario
        return {
            "env_name": "claimsdesk-in",
            "version": VERSION,
            "task_id": self.task_id,
            "seed": self.seed,
            "max_steps": self._max_steps,
            "investigation_budget_initial": self._budget,
            "scenario_id": sc.scenario_id if sc else None,
        }

    # --- internals ---

    def _apply_inspect(self, action: Action, review_key: str) -> bool:
        obs = self._observation
        sc = self._scenario
        assert obs is not None and sc is not None

        if review_key in obs.investigation.reviewed_items:
            return False

        obs.investigation.reviewed_items.append(review_key)
        revealed = True

        if action.action_type in sc.inspect_map:
            imap = sc.inspect_map[action.action_type]
            field = imap.get("update_field")
            val = imap.get("value", "")
            
            if field == "repair_estimate_summary":
                obs.evidence.expert_estimate_summary = val
                self._trajectory.repair_estimate_viewed = True
            elif field == "witness_statement_summary":
                obs.evidence.witness_statement_summary = val
                self._trajectory.witness_statement_viewed = True
            elif field == "police_report_summary":
                obs.evidence.official_report_summary = val
                self._trajectory.police_report_opened_or_requested = True
            elif field == "document_summaries" and "target" in imap:
                target = imap["target"]
                obs.evidence.document_summaries[target] = val
                if target not in obs.evidence.available_documents:
                    obs.evidence.available_documents.append(target)

            if imap.get("notes"):
                obs.investigation.notes_or_findings.append(imap["notes"])
            
            if action.action_type in sc.inspect_unlocks_flags:
                for flag in sc.inspect_unlocks_flags[action.action_type]:
                    if flag not in obs.operational_signals.contradiction_flags:
                        obs.operational_signals.contradiction_flags.append(flag)

        elif action.action_type == "view_claim_summary":
            obs.investigation.notes_or_findings.append("Operations summary reviewed.")
        
        elif action.action_type == "view_document" and action.target:
            tid = action.target
            if tid in sc.document_catalog:
                obs.evidence.document_summaries[tid] = sc.document_catalog[tid]
                if tid not in obs.evidence.available_documents:
                    obs.evidence.available_documents.append(tid)

        return revealed

    def _apply_request(self, action: Action) -> bool:
        obs = self._observation
        sc = self._scenario
        assert obs is not None and sc is not None

        if self._budget <= 0:
            obs.investigation.notes_or_findings.append("Budget exhausted.")
            return False

        self._budget -= 1
        obs.episode.investigation_budget_remaining = self._budget

        at = action.action_type
        if at not in obs.investigation.requested_items:
            obs.investigation.requested_items.append(at)

        cleared = False
        ful = sc.request_fulfillment.get(at)
        if ful:
            if "add_docs" in ful:
                for d in ful["add_docs"]:
                    if d not in obs.evidence.available_documents:
                        obs.evidence.available_documents.append(d)
                    if d in sc.document_catalog:
                        obs.evidence.document_summaries[d] = sc.document_catalog[d]
            if "clear_flags" in ful:
                for fl in ful["clear_flags"]:
                    if fl in obs.operational_signals.contradiction_flags:
                        obs.operational_signals.contradiction_flags.remove(fl)
                        cleared = True
            if "notes" in ful:
                obs.investigation.notes_or_findings.append(ful["notes"])

        obs.investigation.notes_or_findings.append(f"Request fulfilled: {at}")
        return cleared

    def _apply_assessment(self, action: Action) -> None:
        obs = self._observation
        assert obs is not None
        if action.action_type == "mark_fraud_suspected":
            self._trajectory.fraud_marked = True
            if "fraud_suspected" not in obs.operational_signals.anomaly_flags:
                obs.operational_signals.anomaly_flags.append("fraud_suspected")
        elif action.action_type == "flag_inconsistency":
            self._trajectory.inconsistency_flagged = True
        obs.investigation.notes_or_findings.append(f"Assessment: {action.action_type}")

    def _apply_routing(self, action: Action) -> None:
        obs = self._observation
        assert obs is not None
        obs.routing_queue = action.action_type.replace("route_to_", "").replace("escalate_to_", "")

    def _apply_terminal(self, action: Action) -> None:
        obs = self._observation
        assert obs is not None
        self._trajectory.decision_action = action.action_type
        self._trajectory.decision_amount_inr = action.amount_inr
        obs.investigation.notes_or_findings.append(f"Terminal action: {action.action_type}")
