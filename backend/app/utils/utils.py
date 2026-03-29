"""Utility functions for the ClaimsDesk environment."""

from __future__ import annotations

def format_inr(amount: float) -> str:
    """Format amount in INR (₹) with Indian numbering style."""
    if amount is None: return "₹0.00"
    return f"₹{amount:,.2f}"
