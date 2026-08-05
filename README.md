# ORPHEUS Ω

**The Autonomous Invention Archaeologist**

ORPHEUS Ω searches technical history, reconstructs why abandoned inventions failed, tests whether modern technology can revive them, and converts verified work into measurable human benefit and legitimate sustainability paths.

## Autonomous control interface

The repository now includes a light, ChatGPT/Codex-style control interface served directly by FastAPI at `/`.

The interface is not a static mockup. It reads live runtime state and can:

- start, pause, and manually trigger autonomous cycles;
- accept a new human direction through chat;
- show the agents that are working and the stage completed by each one;
- render deterministic mission results in the main output;
- rank benefit and monetization hypotheses;
- show which local, safe, reversible tasks were completed automatically;
- hold outreach, publication, contracting, payment, and other external actions for explicit human approval;
- display recent events and the pending approval queue.

## Autonomous operating model

When autonomous mode is enabled, ORPHEUS does not wait for continuous user messages. It periodically runs a complete cycle:

1. **ORION** converts the human objective into a measurable contract.
2. **VIGÍA** explores technical history and opportunity paths.
3. **VEGA** separates evidence, hypotheses, and unknowns.
4. **ATLAS** designs a manufacturable solution and workflow.
5. **SPARK** executes deterministic simulations and safe local work.
6. **AUREUS-7** creates price, margin, licensing, funding, and revenue hypotheses.
7. **BASTION** blocks unsafe, unsupported, or unauthorized actions.
8. **ECHO** preserves provenance, assumptions, and limits.
9. **KIRA** integrates the result and returns the highest-value decisions to the human.
10. **VANTA-0** supplies legitimate alternative routes when the primary path is blocked.

Safe local actions may run automatically. External communication, publication, contracting, financial activity, account changes, private-data disclosure, and irreversible actions require explicit human approval.

Commercial figures are planning hypotheses. They are not confirmed customers, grants, prices, patents, demand, or guaranteed revenue.

## Current state

The repository is credential-ready and includes:

- a live autonomous control loop with configurable interval;
- benefit, beneficiary, pricing, margin, licensing, and pilot hypotheses;
- explicit approval gates for external and financial actions;
- a light responsive web interface with chat and full output rendering;
- deterministic climate-aware simulation and independent verification;
- a reproducible passive-cooling reference mission;
- a Google ADK agent with tool calls and a Gemini 3.6 Flash default;
- safe offline/mock mode that makes no model request;
- FastAPI endpoints for health, readiness, catalog inspection, simulation, chat, autonomy, and approvals;
- Cloud Run Docker image and Windows PowerShell deployment scripts;
- environment-only configuration with no committed secrets;
- automated tests and GitHub Actions verification.

## Initial mission

Design an affordable, manufacturable, grid-free food-preservation concept by combining historically documented passive-cooling ideas.

The current thermal model is a preliminary deterministic proxy. It is **not** CFD, field validation, food-safety approval, patent clearance, measured demand, or measured commercial performance. The historical catalog still contains source-verification placeholders and must be replaced with authoritative provenance before final submission.

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

Then open the root URL shown by Uvicorn, normally `http://127.0.0.1:8000/`.

## Autonomous configuration

```bash
# Start autonomous mode when the API starts. Default: true.
ORPHEUS_AUTONOMY_ENABLED=true

# Time between autonomous cycles. Minimum: 30 seconds. Default: 300.
ORPHEUS_AUTONOMY_INTERVAL_SECONDS=300

# Optional. Only readiness status is exposed; the value is never returned.
ORPHEUS_PAYMENT_HANDLE=your-configured-payment-channel
```

The payment handle is intentionally not committed to the public repository.

## Useful endpoints

- `GET /`
- `GET /health`
- `GET /readiness`
- `GET /catalog`
- `GET /missions/reference`
- `POST /missions/simulate`
- `POST /chat`
- `GET /autonomy/state`
- `POST /autonomy/start`
- `POST /autonomy/stop`
- `POST /autonomy/cycle`
- `POST /autonomy/profile`
- `POST /autonomy/approve/{action_id}`

## Google ADK agent

Install the agent dependencies and use Google Agents CLI or ADK tooling:

```bash
python -m pip install -e ".[agent]"
```

The ADK app is in `agent_app/agent.py`, and `agents-cli-manifest.yaml` points to it. The agent now has access to `plan_human_benefit`, which converts a verified mission into a beneficiary map, economic hypotheses, completed safe actions, and approval-gated next actions.

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

Gemini may propose hypotheses. Deterministic tools and an independent verifier decide whether a technical mission passes. The human decides whether external or financial actions may proceed.
