"""
ClaimsDesk India Baseline Inference Script
Submission-ready version using OpenAI Python Client.
Localized for India (INR, ₹).
"""

import json
import os
import sys
from typing import Any, Dict, List

from openai import OpenAI

# Internal imports from the professionalized backend
# Note: Ensure PYTHONPATH includes the 'backend' directory
try:
    from app.env.env import ClaimsDeskEnv
    from app.models import Action
    from app.env.graders import grade_trajectory, aggregate_scores
except ImportError:
    print("Error: Could not import backend modules. Ensure PYTHONPATH includes 'backend'.")
    sys.exit(1)

# --- Configuration ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o")
HF_TOKEN = os.getenv("HF_TOKEN")  # Required per OpenEnv spec

SUBMISSION_TASKS = ["StraightThrough", "MissingButLegit", "InflatedCollision"]


class ClaimsAgent:
    """Baseline reasoning agent for ClaimsDesk India."""

    def __init__(self, client: OpenAI, model: str):
        self.client = client
        self.model = model

    def get_action(self, observation: Dict[str, Any], history: List[str]) -> Action:
        """Query LLM for the next action."""
        
        system_prompt = (
            "You are an expert insurance claims adjuster at ClaimsDesk India.\n"
            "Your goal is to triage and resolve claims efficiently and fairly in the Indian market.\n"
            "Currency: Indian Rupee (INR, ₹).\n"
            "You have access to structured data. You must output your next action in JSON format.\n"
            "Available Action Types: view_claim_summary, view_policy_details, view_repair_estimate, "
            "view_claim_history, view_witness_statement, view_police_report, view_document, "
            "request_police_report, request_repair_invoice, mark_fraud_suspected, route_to_manual_review, "
            "approve_claim, deny_claim, offer_partial_settlement.\n\n"
            "JSON Format Example:\n"
            '{"action_type": "view_repair_estimate", "rationale": "I need to see the cost breakdown."}\n'
            '{"action_type": "approve_claim", "amount_inr": 45000.0, "rationale": "Legitimate claim."}'
        )

        user_msg = (
            f"Observation: {json.dumps(observation, indent=2)}\n\n"
            f"Action History: {history}\n\n"
            "What is your next action? Output ONLY valid JSON."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content
            if not raw_content:
                raise ValueError("Empty response from LLM")
            
            data = json.loads(raw_content)
            return Action(**data)
        except Exception as e:
            print(f"Agent Error: {e}")
            return Action(action_type="view_claim_summary", rationale="Fallback due to error")


def run_benchmark():
    """Execute all benchmark tasks and report results for ClaimsDesk India."""
    
    if not OPENAI_API_KEY:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        sys.exit(1)

    client = OpenAI(api_key=OPENAI_API_KEY, base_url=API_BASE_URL)
    agent = ClaimsAgent(client, MODEL_NAME)
    
    all_results = []
    print(f"--- Starting ClaimsDesk India Benchmark (Model: {MODEL_NAME}) ---")

    for task_id in SUBMISSION_TASKS:
        print(f"\nTask: {task_id}")
        env = ClaimsDeskEnv(task_id=task_id)
        obs = env.reset()
        done = False
        step_count = 0
        total_reward = 0.0
        history = []

        while not done and step_count < 45:
            obs_dict = obs.model_dump()
            action = agent.get_action(obs_dict, history)
            
            result = env.step(action)
            obs, reward, done = result.observation, result.reward, result.done
            
            history.append(action.action_type)
            total_reward += reward
            step_count += 1
            
            print(f"  Step {step_count}: {action.action_type} | Reward: {reward:+.2f}")

        # Grading
        scenario = env.get_scenario()
        traj = env.get_trajectory_record()
        grade = grade_trajectory(scenario, traj)
        all_results.append(grade)

        print(f"Finished {task_id} in {step_count} steps. Total Reward: {total_reward:.2f}")
        print(f"Task Score: {grade.score:.2f}")
        for k, v in grade.breakdown.items():
            print(f"  - {k}: {v:.2f}")

    final_score = aggregate_scores(all_results)
    print(f"\n--- Benchmark Complete ---")
    print(f"Final Aggregate Score: {final_score:.2f}")


if __name__ == "__main__":
    # Ensure backend is in path (script is in scripts/, so backend is at ../backend)
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    backend_path = os.path.join(root_dir, "backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    run_benchmark()
