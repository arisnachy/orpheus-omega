# ORPHEUS Ω

**The Autonomous Invention Archaeologist**

ORPHEUS Ω searches technical history, reconstructs why abandoned inventions failed, tests whether modern technology can revive them, and converts verified work into measurable human benefit and legitimate sustainability paths.

## Version 0.9 — FORJA engineering and evolutionary control

The Gemini execution surface is a real Google Agent Development Kit workflow composed of:

- **18 specialist `LlmAgent` instances**;
- **4 real `ParallelAgent` squads**;
- one deterministic `SequentialAgent` root;
- unique ADK `output_key` state channels for every specialist;
- deterministic tools isolated under SPARK;
- explicit human approval boundaries;
- a live browser trace driven by `Runner.run_async()` events.

No agent name, interface card, event count, or model narrative alone counts as evidence.

## Real ADK pipeline

1. **ORION** creates the measurable mission contract.
2. **VIGÍA**, **NYX-7**, and **VEGA** run concurrently to inspect provenance, risk, and verification requirements.
3. **ATLAS-9** creates candidate architectures and rejection rules.
4. **FORJA Ω** runs three engineering specialists concurrently:
   - `forja_core` defines typed architecture, state, tool, retry, timeout, and security contracts;
   - `forja_test` defines acceptance tests, regression gates, and failure injection before execution;
   - `forja_ux` defines a chat-first proof interface backed only by runtime evidence.
5. **SPARK** calls the repository's applicable deterministic tools and reports raw results.
6. **RECURSOR-Ω** and **NÉMESIS-Ω** run concurrently:
   - RECURSOR detects plan weaknesses, programming defects, repeated failures, false closure, technical debt, and defects in the work method itself;
   - NÉMESIS tries to falsify the preferred route and find a stronger lawful alternative without bypassing safety, authorization, privacy, intellectual property, platform, or hackathon rules.
7. **HELIX-8** runs after both audits and scores only demonstrated evidence from 1 to 5 for operational utility, architecture, and demo/production readiness.
8. **AUREUS-7**, **BASTION**, **ECHO**, **RIFT**, and **VANTA-0** run concurrently to evaluate sustainability, approval gates, provenance, blockers, and alternate paths.
9. **KIRA Ω** resolves disagreements and returns the final evidence-controlled decision.

KIRA may not declare completion when RECURSOR returns `FAIL` or HELIX says mandatory submission viability is `FAIL`.

The machine-readable topology is available at `GET /architecture/agents`.

## Hypermodern mission chat

`GET /adk` serves a light, responsive, ChatGPT/Codex-style mission interface with three proof-oriented zones:

- **Constellation rail:** loads the actual 18-agent topology and marks agents from real event authors and state deltas;
- **Mission conversation:** renders user direction, visible agent output, tool calls, tool results, errors, and KIRA's final response as one continuous chat;
- **Evidence inspector:** counts real events, tool calls, errors, final-response observation, backend, model, dependency state, and session identity.

The interface does not generate fake agent activity. When Gemini or Vertex AI is not configured, the execution button remains disabled and the readiness errors stay visible.

## Live Google ADK event bridge

The bridge exposes:

- `GET /adk/readiness` — reports whether a real Gemini or Vertex-backed run can start;
- `POST /adk/run` — executes one invocation and returns its bounded event list;
- `POST /adk/stream` — streams every event as newline-delimited JSON.

The public trace can show:

- event author and sequence;
- visible model output;
- deterministic tool calls and bounded arguments;
- tool results;
- explicit session-state and artifact deltas;
- completion or failure records;
- KIRA's final visible response.

### Trace privacy boundary

The public trace contains actions and evidence, not private chain-of-thought. ADK parts marked as `thought` are counted but their text is never transmitted. Binary payloads are reduced to safe metadata, private file URIs are not exposed, and serialized payloads are depth- and size-bounded.

## Primary-source provenance

Each passive-cooling concept contains at least two stable primary or peer-reviewed engineering sources with:

- DOI or stable proceedings URL;
- evidence type;
- bounded support statement;
- mechanism and known limitations;
- separate `source_verification` and `application_validation` states.

A published experiment may verify a mechanism without validating the current ORPHEUS geometry, target climate, food safety, manufacturability, patent position, demand, or economics.

## Two honest execution surfaces

- `agent_app/agent.py` is the real Gemini + Google ADK multi-agent workflow.
- `orpheus/autonomy.py` is the credential-free deterministic control plane used by the primary FastAPI interface, scheduler, reproducible demo, approval queue, and offline tests.
- `orpheus/adk_bridge.py` connects the real ADK Runner to `/adk` only after a real backend passes readiness checks.

The deterministic surface keeps the repository testable without credentials. It is not presented as proof that Gemini, Vertex AI, or Cloud Run executed.

## Current deterministic mission boundary

The repository currently has one complete deterministic simulator:

> Design an affordable, locally manufacturable, grid-free food-preservation concept by combining passive-cooling ideas.

Unrelated goals remain in discovery until a relevant simulator, dataset, external tool, or reproducible verification protocol exists. The thermal model is a preliminary proxy, not CFD, field validation, food-safety approval, patent clearance, measured demand, or measured commercial performance.

## Safety and authorization

Safe, local, reversible, non-financial actions may run automatically. The following require explicit human approval:

- external communication;
- publication;
- contracting;
- payment;
- account changes;
- private-data disclosure;
- irreversible actions.

Urgency, competitive pressure, requests to ignore rules, and agent preference never remove these gates.

## Credential-free verification

```bash
python -m pip install -e ".[all]"
python -m unittest discover -s tests -v
python scripts/run_demo.py
python -m compileall agent_app app orpheus tests scripts
node --check web/app.js
node --check web/adk.js
uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/` for the deterministic autonomous cockpit;
- `http://127.0.0.1:8000/adk` for the real ADK mission chat.

In credential-free mode, `/adk` remains visible but correctly refuses to imitate a cloud-backed run.

## Run with Gemini API

Configure the key in the environment; never commit it.

```powershell
python -m pip install -e ".[all]"
$env:ORPHEUS_RUNTIME_MODE="local"
$env:ORPHEUS_LLM_BACKEND="gemini_api"
$env:ORPHEUS_MODEL="YOUR_AVAILABLE_GEMINI_MODEL"
$env:GOOGLE_API_KEY="YOUR_KEY"
uvicorn app.main:app --reload
```

Confirm `GET /adk/readiness` reports `ready: true` before launching a mission.

## Run with Vertex AI

```powershell
python -m pip install -e ".[all]"
gcloud auth application-default login
$env:ORPHEUS_RUNTIME_MODE="google_cloud"
$env:ORPHEUS_LLM_BACKEND="vertex_ai"
$env:ORPHEUS_MODEL="YOUR_AVAILABLE_GEMINI_MODEL"
$env:GOOGLE_GENAI_USE_VERTEXAI="true"
$env:GOOGLE_CLOUD_PROJECT="YOUR_PROJECT_ID"
$env:GOOGLE_CLOUD_LOCATION="global"
uvicorn app.main:app --reload
```

The current ADK bridge uses `InMemorySessionService`, which is appropriate for one-process demonstrations. Continued sessions across multiple Cloud Run instances still require a shared persistent session service and distributed locking.

## Google Cloud activation

```powershell
gcloud auth login
gcloud auth application-default login
powershell -ExecutionPolicy Bypass -File deployment/prepare-cloud.ps1 -ProjectId YOUR_PROJECT_ID
powershell -ExecutionPolicy Bypass -File deployment/deploy-cloud-run.ps1 -ProjectId YOUR_PROJECT_ID -Public
powershell -ExecutionPolicy Bypass -File deployment/configure-autonomy-scheduler.ps1 -ProjectId YOUR_PROJECT_ID
```

## Useful endpoints

- `GET /`
- `GET /adk`
- `GET /health`
- `GET /readiness`
- `GET /architecture/agents`
- `GET /adk/readiness`
- `POST /adk/run`
- `POST /adk/stream`
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
- `GET /autonomy/export/decision.md`
- `GET /autonomy/export/state.json`

## Hackathon truth boundary

The official per-criterion maximum is **5/5**. The official final score can reach **6/6** through permitted bonus contributions. “10/5” is an internal aspiration for clarity and impact, not a fabricated rubric score.

Still required before a winning submission can be claimed:

1. real Gemini or Vertex execution preserved as evidence;
2. Cloud Run deployment and visible Google Cloud proof;
3. shared durable session state and crash-safe resume;
4. one human-approved external beneficiary action;
5. golden evaluations and adversarial security gates;
6. final architecture PNG/PDF;
7. public four-minute English demo video;
8. completed Devpost submission.

## Core rule

A claim advances only when the relevant source, tool, test, state transition, approval, and closure evidence support it.
