---
title: ClaimsDesk India
emoji: 🏥
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
license: mit
tags:
  - openenv
---

# ClaimsDesk India: Professional AI Insurance Intelligence
[![OpenEnv](https://img.shields.io/badge/OpenEnv-Benchmark-blue)](https://openenv.org)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 1. Overview
**ClaimsDesk India** is a professional-grade, enterprise-ready AI insurance intelligence platform and OpenEnv benchmark. It evaluates AI agents on their ability to manage complex insurance operations within the **Indian market context**, covering **Health, Property, and Motor** insurance domains.

The platform simulates a high-stakes claims adjuster's workspace, where agents must navigate:
- **🇮🇳 Indian Localization**: All transactions in **INR (₹)**, localized Indian names, and regional context (Mumbai, Delhi, Bengaluru).
- **🏥 Multi-Domain Triage**: Beyond vehicle claims—handles complex Health (Surgery) and Property (Fire/Monsoon) claim scenarios.
- **🛡️ Enterprise Architecture**: Robust `backend/` and `frontend/` separation built for scale and portability.
- **🔍 Fraud & Logic Intelligence**: Evaluation of dense reasoning trajectories, not just final decisions.

## 2. Professional Architecture
The project has been refactored into a high-standards enterprise structure:
- **`backend/`**: FastAPI server with modular `app/` structure (models, env, graders, rewards, scenarios).
- **`frontend/`**: Modern React dashboard built with Vite, featuring real-time KPI monitoring and a human-in-the-loop action console.
- **`deployment/`**: Multi-stage Docker configuration for seamless deployment to Hugging Face or private clouds.

## 3. Benchmark Scenarios (India Context)
| Task ID | Domain | Location | Difficulty | Description |
| :--- | :--- | :--- | :--- | :--- |
| `StraightThrough` | **Health** | Mumbai | Easy | Legitimate hospital surgery claim. Tests compliance and efficient processing in INR. |
| `MissingButLegit` | **Property** | Delhi | Medium | Fire damage with missing official reports. Tests evidence gathering and local regulation handling. |
| `InflatedCollision` | **Motor** | Bengaluru | Hard | High-value collision with shop-inflation signals. Tests fraud detection and rigorous negotiation. |

## 4. Setup & Execution

### Local Development
1. **Install Python backend**:
   ```bash
   pip install fastapi uvicorn pydantic pydantic-settings httpx
   ```
2. **Setup Frontend**:
   ```bash
   cd frontend && npm install && npm run build && cd ..
   ```
3. **Run Platform (Unified)**:
   ```bash
   $env:PYTHONPATH="backend"; python backend/main.py
   ```

### Running Benchmark
To execute the submission-ready baseline inference script (requires OpenAI API Key):
```bash
$env:PYTHONPATH="backend"; python inference.py
```

## 5. Grading & Evaluation
ClaimsDesk India uses a **Trajectory-Aware Grader** (`[0.0, 1.0]`):
- **Resolution Correctness (30%)**: Alignment with hidden fair-market INR settlement bands.
- **Evidence Diligence (25%)**: Professional inspection of critical local documents (Vahan, Fire Service).
- **Fraud Calibration (20%)**: Accurate identification of suspicious signals in the Indian context.
- **Operational Efficiency (25%)**: Resolution within professional step and budget limits.

---
*Developed for the OpenEnv Enterprise Benchmark Challenge.*
