# ORPHEUS Ω

**The Autonomous Invention Archaeologist**

ORPHEUS Ω searches technical history, reconstructs why abandoned inventions failed, and tests whether modern technology can revive them.

## Current state

The repository is now credential-ready:

- deterministic climate-aware simulation and independent verification;
- a reproducible passive-cooling reference mission;
- a Google ADK agent with tool calls and a Gemini 3.6 Flash default;
- safe offline/mock mode that makes no model request;
- FastAPI endpoints for health, readiness, catalog inspection, and simulation;
- Cloud Run Docker image and Windows PowerShell deployment scripts;
- environment-only configuration with no committed secrets;
- automated tests and GitHub Actions verification.

## Initial mission

Design an affordable, manufacturable, grid-free food-preservation concept by combining historically documented passive-cooling ideas.

The current thermal model is a preliminary deterministic proxy. It is **not** CFD, field validation, food-safety approval, patent clearance, or measured performance. The historical catalog still contains source-verification placeholders and must be replaced with authoritative provenance before final submission.

## Credential-free verification

```powershell
powershell -ExecutionPolicy Bypass -File deployment/test-local.ps1
```

Or with an existing Python environment:

```bash
python -m pip install -e ".[api]"
python -m unittest discover -s tests -v
python scripts/run_demo.py
uvicorn app.main:app --reload
```

Useful endpoints:

- `GET /health`
- `GET /readiness`
- `GET /catalog`
- `GET /missions/reference`
- `POST /missions/simulate`

## Google ADK agent

Install the agent dependencies and use Google Agents CLI or ADK tooling:

```bash
python -m pip install -e ".[agent]"
```

The ADK app is in `agent_app/agent.py`, and `agents-cli-manifest.yaml` points to it.

## Google Cloud activation

After redeeming credits and selecting the final Google Cloud project:

```powershell
gcloud auth login
gcloud auth application-default login
powershell -ExecutionPolicy Bypass -File deployment/prepare-cloud.ps1 -ProjectId YOUR_PROJECT_ID
powershell -ExecutionPolicy Bypass -File deployment/deploy-cloud-run.ps1 -ProjectId YOUR_PROJECT_ID -Public
```

See [`docs/CREDENTIALS_AND_DEPLOYMENT.md`](docs/CREDENTIALS_AND_DEPLOYMENT.md) for the exact boundary between what is already testable and what requires real cloud credentials.

## Core rule

Gemini may propose hypotheses. Deterministic tools and an independent verifier decide whether a mission passes.
