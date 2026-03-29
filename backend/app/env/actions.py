"""Action validation and classification."""

from __future__ import annotations

from app.models import (
    ALL_ACTION_TYPES,
    Action,
    ActionCategory,
    action_category,
    is_terminal_action,
)


class ValidationResult:
    __slots__ = ("valid", "reason", "category")

    def __init__(self, valid: bool, reason: str | None = None, category: ActionCategory | None = None) -> None:
        self.valid = valid
        self.reason = reason
        self.category = category


def validate_action(action: Action) -> ValidationResult:
    if action.action_type not in ALL_ACTION_TYPES:
        return ValidationResult(False, f"unknown_action_type:{action.action_type}")
    cat = action_category(action.action_type)
    if cat is None:
        return ValidationResult(False, "unclassified_action")
    if action.action_type == "view_document" and not (action.target and action.target.strip()):
        return ValidationResult(False, "view_document_requires_target")
    return ValidationResult(True, None, cat)


def is_terminal_operation(action_type: str) -> bool:
    """Episode ends after these actions (decision + certain escalations)."""
    if is_terminal_action(action_type):
        return True
    return action_type in ("escalate_to_fraud_investigation", "escalate_to_supervisor")
