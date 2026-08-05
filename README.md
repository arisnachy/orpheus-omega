# ORPHEUS Ω

**The Autonomous Invention Archaeologist**

ORPHEUS Ω searches technical history, reconstructs why abandoned inventions failed, tests whether modern technology can revive them, and converts verified work into measurable human benefit and legitimate sustainability paths.

## Version 0.5 — real Google ADK multi-agent architecture

Version 0.5 replaces the former single ADK agent whose specialist roles existed only inside one instruction prompt. The Gemini execution surface is now a real Google Agent Development Kit workflow composed of twelve specialist `LlmAgent` instances, two concurrent `ParallelAgent` groups, and one deterministic `SequentialAgent` root.

The ADK pipeline is:

1. **ORION** creates the measurable mission contract.
2. **VIGÍA**, **NYX-7**, and **VEGA** run concurrently to inspect provenance, risk, and verification requirements.
3. **ATLAS-9** creates candidate architectures and rejection rules.
4. **SPARK** calls the repository's applicable deterministic tools.
5. **AUREUS-7**, **BASTION**, **ECHO**, **RIFT**, and **VANTA-0** run concurrently to evaluate sustainability, approval gates, provenance, blockers, and alternative routes.
6. **KIRA** resolves disagreements and returns the final evidence-controlled decision.

Every specialist writes to a unique ADK `output_key`, so downstream agents receive explicit session state rather than relying on theatrical role names in a shared prompt. The real topology is available as machine-readable JSON at `GET /architecture/agents`.

## Primary-source provenance

The passive-cooling catalog is no longer synthetic scaffolding. Each of its five mechanisms now includes:

- at least two stable primary or peer-reviewed engineering sources;
- DOI or stable proceedings URL;
- evidence type;
- a bounded statement of exactly what the source supports;
- known mechanism limitations;
- an explicit distinction between **source verification** and **ORPHEUS application validation**.

A published experiment can verify that a mechanism exists without validating the current ORPHEUS geometry, target climate, food safety, manufacturability, patent position, or economics. `GET /catalog` reports both states separately and fails its provenance contract when a source lacks a title, stable URL, evidence type, or bounded support statement.

## Two honest execution surfaces

The repository intentionally separates two surfaces:

- `agent_app/agent.py` is the real Gemini + Google ADK multi-agent workflow.
- `orpheus/autonomy.py` is the credential-free deterministic control plane used by the FastAPI interface, scheduler, reproducible demo, tests, approval queue, and offline verification.

This separation keeps the project testable without credentials while preserving a genuine cloud-agent implementation. The next integration milestone is to stream ADK events into the same control interface without weakening the offline verification path.

## Evidence-aware autonomy

Every human objective is classified as **verification** or **discovery**:

- only passive food-cooling goals may use the repository's current deterministic simulator;
- unrelated goals never inherit a false success result from the reference mission;
- every local runtime stage records an output summary, timestamps, and status;
- the runtime keeps cycle history and can optionally persist state to JSON;
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
- show the output produced by each local execution stage;
- export the KIRA decision memo as Markdown;
- export the full runtime state as JSON;
- review, approve, or decline gated actions;
- show the team, execution progress, events, and recent cycles;
- expose the real ADK hierarchy through `/architecture/agents`.

## Safety and approval boundary

Safe local, reversible, non-financial actions may run automatically. Communication, publication, contracting, payment, account changes, private-data disclosure, and irreversible actions require explicit human approval.

Gemini may propose hypotheses. Deterministic tools and an independent verifier decide whether a supported technical mission passes. KIRA may automatically complete safe local work. The human decides whether any external or financial action may proceed.

## Current technical mission

The deterministic mission currently supported by the repository is:

> Design an affordable, locally manufacturable, grid-free food-preservation concept by combining passive-cooling ideas.

The thermal model is a preliminary deterministic proxy. It is **not** CFD, field validation, food-safety approval, patent clearance, measured demand, or measured commercial performance. The catalog's sources document bounded mechanism-level evidence; all current ORPHEUS applications remain pending mission-specific validation.

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

## Verify the real ADK topology

```bash
python -m pip install -e ".[agent]"
python -c "from agent_app.agent import root_agent; print(root_agent.name, [a.name for a in root_agent.sub_agents])"
python -m unittest discover -s tests -p "test_agent_architecture.py" -v
```

The architecture test verifies that:

- the root is an actual `SequentialAgent`;
- both specialist squads are actual `ParallelAgent` instances;
- twelve specialists are actual `LlmAgent` instances;
- every specialist has a unique state `output_key`;
- SPARK owns the deterministic execution tools;
- the public topology endpoint matches the runtime hierarchy.

## Run the Google ADK agent

```bash
python -m pip install -e ".[agent]"
adk web .
```

Select `agent_app` in the ADK interface and provide a measurable mission. Configure Gemini through environment variables before a real model run.

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
- `GET /architecture/agents`
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

## Google Cloud activation

```powershell
gcloud auth login
gcloud auth application-default login
powershell -ExecutionPolicy Bypass -File deployment/prepare-cloud.ps1 -ProjectId YOUR_PROJECT_ID
powershell -ExecutionPolicy Bypass -File deployment/deploy-cloud-run.ps1 -ProjectId YOUR_PROJECT_ID -Public
powershell -ExecutionPolicy Bypass -File deployment/configure-autonomy-scheduler.ps1 -ProjectId YOUR_PROJECT_ID
```

See [`docs/CREDENTIALS_AND_DEPLOYMENT.md`](docs/CREDENTIALS_AND_DEPLOYMENT.md), [`docs/AUTONOMY.md`](docs/AUTONOMY.md), and [`docs/ALL_THINGS_AGENTIC_WIN_PLAN.md`](docs/ALL_THINGS_AGENTIC_WIN_PLAN.md).

## Core rule

No agent name, interface card, model narrative, or citation count alone counts as evidence. A claim advances only when the relevant source, bounded support statement, tool, test, and approval state support it.
