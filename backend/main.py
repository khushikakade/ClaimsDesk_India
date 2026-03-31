"""
ClaimsDesk AI Platform API - Localized for India (INR, ₹).
"""

from __future__ import annotations

import os
import random
from datetime import datetime, timedelta
from typing import Any, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


# Updated imports for new structure
from app.env.env import ClaimsDeskEnv
from app.models import Action, StepResult, IncidentType, PolicyType

app = FastAPI(title="ClaimsDesk India - AI Operations Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Sessions & Sessions Manager ---
_sessions: dict[str, ClaimsDeskEnv] = {}

# --- API Models ---
class ResetBody(BaseModel):
    task_id: str = "StraightThrough"  # default task so body is not required
    seed: int = 0
    session_id: str = "default"

class ActionBody(BaseModel):
    action_type: str
    amount_inr: Optional[float] = None
    rationale: Optional[str] = None

# --- Persistent Mock Claims Data (Indian Context) ---

class MockClaim(BaseModel):
    claim_id: str
    claimant_name: str
    claim_type: IncidentType
    amount: float
    status: str = "pending_review"
    urgency: float = Field(ge=0, le=1)
    submission_date: str
    policy_type: PolicyType
    incident_date: str
    ai_priority: str = "medium"
    suspicion_level: float = Field(ge=0, le=1)
    description: str
    ai_analysis: Optional[dict[str, Any]] = None

_MOCK_CLAIMS: dict[str, MockClaim] = {}

def _initialize_mock_data():
    indian_names = [
        "Arjun Mehta", "Priya Sharma", "Rahul Verma", "Sneha Kapoor", 
        "Aravind Iyer", "Ananya Reddy", "Vikram Rathore", "Ishaan Malhotra",
        "Zoya Khan", "Aditya Gupta", "Meera Nair", "Rohan Das"
    ]
    
    # 1. Benchmark Scenarios (Mapped to Indian Context)
    benchmarks = [
        {
            "task": "StraightThrough",
            "name": "Arjun Mehta",
            "type": IncidentType.VEHICLE_COLLISION,
            "amt": 45000, # ₹45k
            "desc": "Collision in Mumbai traffic (Western Express Highway). All documents verified.",
            "risk": 0.05
        },
        {
            "task": "MissingButLegit",
            "name": "Priya Sharma",
            "type": IncidentType.VEHICLE_COLLISION,
            "amt": 28000, # ₹28k
            "desc": "Parking lot scrape in Delhi (Connaught Place). Police report missing due to delay.",
            "risk": 0.25
        },
        {
            "task": "InflatedCollision",
            "name": "Rahul Verma",
            "type": IncidentType.VEHICLE_COLLISION,
            "amt": 185000, # ₹1.85 Lakh
            "desc": "Multi-car pileup in Bangalore (Electronic City). Damage estimate exceeds visual evidence.",
            "risk": 0.65
        }
    ]

    for b in benchmarks:
        cid = f"CLM-IND-{b['task'][:3].upper()}"
        _MOCK_CLAIMS[cid] = MockClaim(
            claim_id=cid,
            claimant_name=b['name'],
            claim_type=b['type'],
            amount=b['amt'],
            status="pending_review",
            urgency=0.4 if b['risk'] < 0.3 else 0.8,
            submission_date=(datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            policy_type=PolicyType.MOTOR_PACKAGE,
            incident_date=(datetime.now() - timedelta(days=3)).strftime("%Y-%m-%d"),
            ai_priority="high" if b['risk'] > 0.5 else "medium",
            suspicion_level=b['risk'],
            description=b['desc'],
            ai_analysis={
                "triage_priority": "high" if b['risk'] > 0.5 else "medium",
                "ai_confidence": 0.9,
                "reasoning_summary": f"Context: Indian localization for {b['task']}."
            }
        )

    # 2. Expanded Domains (Health, Property, etc.)
    domains = [
        (IncidentType.HEALTH_SURGERY, PolicyType.HEALTH_CONCIERGE, 250000, "Apollo Hospital - Knee Surgery claim."),
        (IncidentType.PROPERTY_FIRE, PolicyType.PROPERTY_ALL_RISK, 850000, "Fire damage at residential property in Pune."),
        (IncidentType.TRAVEL_CANCELLATION, PolicyType.TRAVEL_WORLD, 35000, "International flight cancellation - Air India."),
        (IncidentType.HEALTH_CRITICAL_ILLNESS, PolicyType.HEALTH_CONCIERGE, 500000, "Critical illness benefit claim."),
        (IncidentType.PROPERTY_FLOOD, PolicyType.PROPERTY_ALL_RISK, 120000, "Monsoon flood damage in Chennai."),
        (IncidentType.LIFE_BENEFIT, PolicyType.LIFE_TERM, 2000000, "Life term insurance maturity benefit.")
    ]

    for i, (it, pt, amt, desc) in enumerate(domains):
        cid = f"CLM-OPS-{200+i}"
        sl = random.random()
        _MOCK_CLAIMS[cid] = MockClaim(
            claim_id=cid,
            claimant_name=random.choice(indian_names),
            claim_type=it,
            amount=amt,
            status=random.choice(["pending_review", "approved", "escalated"]),
            urgency=random.random(),
            submission_date=(datetime.now() - timedelta(days=random.randint(0, 10))).strftime("%Y-%m-%d"),
            policy_type=pt,
            incident_date=(datetime.now() - timedelta(days=random.randint(5, 15))).strftime("%Y-%m-%d"),
            ai_priority=random.choice(["low", "medium", "high"]),
            suspicion_level=sl,
            description=desc,
            ai_analysis={
                "triage_priority": "high" if sl > 0.7 else "medium",
                "ai_confidence": round(random.uniform(0.7, 0.99), 2),
                "reasoning_summary": "Multidomain risk assessment for Indian operations."
            }
        )

_initialize_mock_data()

# --- API Endpoints ---

@app.get("/api/tasks")
def list_tasks():
    # Mapped to localized Indian benchmark scenarios
    return [
        {"id": "StraightThrough", "name": "Health Surgery (Mumbai)", "difficulty": "easy"},
        {"id": "MissingButLegit", "name": "Property Fire (Delhi)", "difficulty": "medium"},
        {"id": "InflatedCollision", "name": "Vehicle Collision (Bengaluru)", "difficulty": "hard"},
    ]

@app.get("/api/dashboard/summary")
def get_dashboard_summary():
    claims = list(_MOCK_CLAIMS.values())
    return {
        "stats": {
            "total_claims": len(claims),
            "pending_review": len([c for c in claims if c.status == "pending_review"]),
            "suspicious_claims": len([c for c in claims if c.suspicion_level > 0.5]),
            "escalated_claims": len([c for c in claims if c.status == "escalated"]),
            "avg_processing_time": "1.2 days"
        },
        "high_risk": [c for c in sorted(claims, key=lambda x: x.suspicion_level, reverse=True)[:5]]
    }

@app.get("/api/claims")
def list_claims(status: Optional[str] = None):
    claims = list(_MOCK_CLAIMS.values())
    if status and status != "All":
        if status == "Urgent":
            claims = [c for c in claims if c.urgency > 0.7]
        elif status == "Suspicious":
            claims = [c for c in claims if c.suspicion_level > 0.5]
        else:
            claims = [c for c in claims if c.status == status.lower()]
    return sorted(claims, key=lambda x: x.submission_date, reverse=True)

@app.get("/api/claims/{claim_id}")
def get_claim(claim_id: str):
    if claim_id not in _MOCK_CLAIMS:
        raise HTTPException(status_code=404, detail="Claim not found")
    return _MOCK_CLAIMS[claim_id]

@app.post("/api/simulation/reset")
def reset_simulation(body: Optional[ResetBody] = None):
    if body is None:
        body = ResetBody()
    env = ClaimsDeskEnv(task_id=body.task_id, seed=body.seed)
    obs = env.reset()
    _sessions[body.session_id] = env
    return {"observation": obs.model_dump(mode="json"), "metadata": env.get_metadata()}

# Aliases for OpenEnv Spec Compliance (Top-Level)
@app.post("/reset")
def spec_reset(body: Optional[ResetBody] = None):
    return reset_simulation(body)

@app.post("/step")
@app.post("/api/simulation/step")  # UI alias — fixes 405 from frontend
def spec_step(action: Action):
    # This assumes session_id "default" is the target for step validation
    if "default" not in _sessions:
        raise HTTPException(status_code=400, detail="Call /reset first")
    return _sessions["default"].step(action).model_dump(mode="json")

@app.get("/state")
def spec_state():
    if "default" not in _sessions:
        raise HTTPException(status_code=400, detail="Call /reset first")
    return _sessions["default"].state().model_dump(mode="json")

# Mount frontend using absolute paths to avoid Docker cwd issues
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dist_path = os.path.join(base_dir, "frontend", "dist")

if not os.path.exists(dist_path):
    print(f"Warning: React frontend dist not found at {dist_path}. Falling back to parent...")
    dist_path = os.path.join(os.path.dirname(base_dir), "frontend", "dist")

if os.path.exists(dist_path):
    app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
else:
    print(f"CRITICAL WARNING: No static files found to mount at {dist_path}!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

