# ClaimsDesk India: Enterprise AI Claims Intelligence

[![OpenEnv](https://img.shields.io/badge/OpenEnv-Benchmark-blue)](https://openenv.org)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3.10/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)

**ClaimsDesk India** is a high-fidelity, enterprise-grade AI environment designed for the automated triage, investigation, and resolution of insurance claims in the Indian market. Built on the **OpenEnv** specification, it provides a strictly typed, reproducible benchmark for AI agents handling complex multi-domain insurance scenarios (Health, Property, Motor).

---

## 🏗️ Core Architecture: "Decision-Engine-as-a-Service"

Unlike traditional legacy systems, ClaimsDesk is built with an **Integration-First** philosophy. It provides a "Headless AI" core that can be embedded directly into existing insurer workflows via RESTful APIs and Webhooks.

### Key Capabilities
- **🇮🇳 Localized Intelligence**: Native support for **INR (₹)** transactions and regional Indian regulations (Mumbai, Delhi, Bengaluru).
- **🏥 Multi-Domain Precision**: Pre-configured scenarios for Health (Surgery), Property (Fire/Monsoon), and Motor (Collision).
- **🛡️ Fraud-Centric Grading**: A mathematically rigorous `Trajectory-Aware Grader` that evaluates agent reasoning, not just final outcomes.
- **⚡ Lightning-Fast Deployment**: Containerized architecture optimized for sub-15s startup on Hugging Face or private cloud environments.

---

## 📂 Repository Structure

```text
.
├── backend/            # FastAPI Decision Core & Environment Logic
│   ├── app/
│   │   ├── env/        # OpenEnv Gym Environment (ClaimsDeskEnv)
│   │   ├── utils/      # Indian Market Localization Helpers
│   │   └── models.py   # Pydantic Typing (Action, Observation, Reward)
│   └── main.py         # Production API Entrypoint
├── frontend/           # React KPIs & Human-in-the-Loop Action Console
├── scripts/            # Automated Benchmarking & Evaluation Tools
├── server/             # Multi-mode Deployment Wrappers
├── openenv.yaml        # Benchmark Metadata & Task Definitions
└── pyproject.toml      # Python Packaging & Workspace Config
```

---

## 🚀 Getting Started

### 1. Developer Setup
Initialize the environment locally:
```bash
# Install backend dependencies
pip install -e .

# Build frontend assets
npm run build --prefix frontend
```

### 2. Running the Environment
Start the unified platform (API + Dashboard):
```bash
# Add backend to your search path
$env:PYTHONPATH="backend" 
python backend/main.py
```

### 3. Executing the Benchmark
Run the baseline AI agent against the pre-configured Indian scenarios:
```bash
python scripts/benchmark.py
```

---

## 📈 Integration Strategy for Insurers

ClaimsDesk is designed to be **integrated**, not just used standalone. For big insurance companies, the recommended implementation path is:

1. **Passive Audit Mode**: Ingest historical claims data via the API to find leakage and fraud signals.
2. **Shadow Triage**: Run ClaimsDesk parallel to human adjusters to build confidence intervals.
3. **Automated STP (Straight-Through Processing)**: Connect the `/step` endpoint to your core claims system (e.g., GuideWire) for sub-5s automated approval.

---
*Developed for the OpenEnv Enterprise Benchmark Challenge. Localized for the Indian Insurance Market.*
