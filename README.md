# Vectaflow Enterprise Revenue Yield & Elasticity Engine

Vectaflow is an enterprise-grade dynamic pricing and revenue optimization simulation environment. It models marketplace consumer demand curves and optimizes yields using dynamic algorithms and machine learning:

1. **Thompson Sampling Pricing Agent**: A binomial Multi-Armed Bandit (MAB) reinforcement learning agent tracking priors via Beta(alpha, beta) distributions to balance price exploration and exploitation.
2. **SGD Elasticity Model**: A Polynomial Logistic Regression model trained from scratch with Stochastic Gradient Descent (SGD) and L2 regularization to fit demand curves and compute analytical price elasticity.
3. **Marketplace Simulator**: A multi-variable consumer marketplace simulating competitor pricing responses, seasonal traffic flows, inventory limitations, and manual customer interactions.

---

## Repository Structure

```text
├── Dockerfile                  # Slim production Docker image definition
├── docker-compose.yml          # Local container orchestration file
├── pyproject.toml              # PEP 517/621 packaging definitions
├── requirements.txt            # Python dependencies (pinned)
├── src/
│   └── vectaflow/
│       ├── app.py              # FastAPI server (API endpoints & static host)
│       ├── simulator.py        # E-commerce marketplace simulator
│       ├── static/             # Static UI assets (HTML5/CSS3/JS)
│       └── algorithms/
│           ├── elasticity_model.py  # SGD Polynomial Logistic Regression model
│           └── pricing_agent.py     # Thompson Sampling RL bandit agent
└── tests/
    ├── test_api.py             # Endpoint integration tests
    └── test_pricing.py         # Algorithm and model unit tests
```

---

## Quick Start

### 1. Local Development Setup

Prerequisites: Python 3.10 or higher.

```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install package in editable development mode along with testing requirements
pip install -e .[dev]
```

### 2. Run the Application

Start the FastAPI application server locally using uvicorn:

```powershell
python -m uvicorn vectaflow.app:app --host 127.0.0.1 --port 8000 --reload
```

Open your web browser and navigate to: `http://127.0.0.1:8000/`

---

## Containerized Run (Docker)

Use docker-compose to orchestrate and deploy the containerized stack:

```bash
# Build and run container
docker-compose up --build -d

# View container logs
docker-compose logs -f
```

The containerized dashboard will be available at `http://localhost:8000/`

---

## Running Automated Tests

Run the test suite to verify algorithm correctness and API endpoint health:

```powershell
$env:PYTHONPATH="src"
python -m unittest discover tests/
```
