# ORPHEUS Ω

**The Autonomous Invention Archaeologist**

ORPHEUS Ω searches technical history, reconstructs why abandoned inventions failed, tests whether modern technology can revive them, and converts verified work into measurable human benefit and legitimate sustainability paths.

## Version 0.4 — evidence-aware autonomy

The current release replaces the original single-purpose autonomous mockup with a stricter operating model:

- every human objective is classified as **verification** or **discovery**;
- only passive food-cooling goals may use the repository's current deterministic simulator;
- unrelated goals never inherit a false success result from the reference mission;
- every agent stage records a real output summary, timestamps, and status;
- the runtime keeps a cycle history and can optionally persist state to JSON;
- repeated scheduler calls can carry an idempotency key;
- external and financial actions can be approved or declined with a human note;
- KIRA produces a downloadable decision memo and complete JSON state;
- prices, margins, customers, grants, demand, and patent position remain explicitly labelled as hypotheses unless independently verified.

## Autonomous control interface

FastAPI serves a light ChatGPT/Codex-style control interface at `/`. The interface is driven by live runtime data rather than static cards.

It can:

- start, pause, and manually trigger autonomous cycles;
- accept a new direction through chat;
- display the active classification and technical status;
- render the full recommendation, benefit, candidates, economics, limits, and history;
- show the output produced by each agent stage;
- export the KIRA decision memo as Markdown;
- export the full runtime state as JSON;
- review, approve, or decline gated actions;
- show the team, execution progress, events, and recent cycles.

## Autonomous operating model

When autonomous mode is enabled, ORPHEUS runs a complete cycle without waiting for continuous user messages:

1. **ORION** defines the measurable mission contract.
2. **VIGÍA** maps technical history and opportunity paths.
3. **NYX-7** detects failures, contradictions, and dependencies.
4. **VEGA** separates evidence, hypotheses, and unknowns.
5. **ATLAS-9** designs a manufacturable solution and workflow.
6. **SPARK** executes only the deterministic tools that actually apply.
7. **AUREUS-7** creates labelled price, margin, licensing, and funding hypotheses.
8. **BASTION** blocks unsupported, unsafe, or unauthorized actions.
9. **ECHO** preserves provenance, limitations, and the decision memo.
10. **KIRA** integrates the output and returns the highest-value decision to the human.
11. **VANTA-0** provides legitimate alternatives when the main route is blocked.

Safe local actions may run automatically. Communication, publication, contracting, payment, account changes, private-data disclosure, and irreversible actions require explicit human approval.

## Current technical mission

The deterministic mission currently supported by the repository is:

> Design an affordable, locally manufacturable, grid-free food-preservation concept by combining passive-cooling ideas.

The thermal model is a preliminary deterministic proxy. It is **not** CFD, field validation, food-safety approval, patent clearance, measured demand, or measured commercial performance. Historical catalog entries that say source verification is pending must not be presented as verified history.

## Credential-free verification

```powershell
powershell -ExecutionPolicy Bypass -File deployment/test-local.ps1
```

Or:

```bash
python -m pip install -e ".[api]"
python -m unittest discover -s tests -v
python scripts/run_demo.py
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/`.

## Autonomous configuration

```bash
# Start the in-process autonomous loop. Default: true.
ORPHEUS_AUTONOMY_ENABLED=true

# Minimum 30 seconds. Default: 300.
ORPHEUS_AUTONOMY_INTERVAL_SECONDS=300

# Optional JSON persistence for local or single-instance deployments.
ORPHEUS_STATE_PATH=.orpheus/runtime-state.json

# Optional payment-channel readiness flag. The value is never returned by the API.
ORPHEUS_PAYMENT_HANDLE=your-configured-payment-channel
```

For multi-instance Cloud Run persistence and distributed locking, use Firestore or another shared state service. A local JSON path is not a substitute for distributed state.

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
- `POST /autonomy/actions/{action_id}/decision`
- `POST /autonomy/approve/{action_id}` — backward compatibility
- `GET /autonomy/export/decision.md`
- `GET /autonomy/export/state.json`

A scheduler may send `X-Orpheus-Run-Key` to `/autonomy/cycle` to prevent duplicate execution of the same scheduled run within one persisted runtime state.

## Google ADK agent

```bash
python -m pip install -e ".[agent]"
```

The ADK app is in `agent_app/agent.py`. Its `plan_human_benefit` tool now accepts a goal, classifies whether the deterministic mission applies, and returns discovery status instead of inventing technical verification for unsupported objectives.

## Google Cloud activation

```powershell
gcloud auth login
gcloud auth application-default login
powershell -ExecutionPolicy Bypass -File deployment/prepare-cloud.ps1 -ProjectId YOUR_PROJECT_ID
powershell -ExecutionPolicy Bypass -File deployment/deploy-cloud-run.ps1 -ProjectId YOUR_PROJECT_ID -Public
powershell -ExecutionPolicy Bypass -File deployment/configure-autonomy-scheduler.ps1 -ProjectId YOUR_PROJECT_ID
```

See [`docs/CREDENTIALS_AND_DEPLOYMENT.md`](docs/CREDENTIALS_AND_DEPLOYMENT.md) and [`docs/AUTONOMY.md`](docs/AUTONOMY.md).

## Core rule

Gemini may propose hypotheses. Deterministic tools and an independent verifier decide whether a technical mission passes. KIRA may automatically complete safe local work. The human decides whether any external or financial action may proceed.
