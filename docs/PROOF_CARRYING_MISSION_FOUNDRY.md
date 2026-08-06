# ORPHEUS Ω — Proof-Carrying Mission Foundry

Status: winning product direction and implementation contract  
Primary category: Taskmaster  
Flagship mission: passive, electricity-free food preservation for an underserved local operator  
Truth boundary: this document defines the target product. Features are not considered complete until their acceptance evidence exists.

## 1. Executive decision

ORPHEUS Ω will not be presented as a passive-cooling application, an invention-archaeology chatbot, or a generic collection of agents.

It will become a **Proof-Carrying Mission Foundry**:

> ORPHEUS compiles messy human friction into an executable mission, discovers evidence, generates competing interventions, attempts to falsify them, executes approved external actions, records proof and rollback information, observes the result, and evolves the next mission cycle.

The passive-cooling mission remains the flagship demonstration because it is concrete, visual, socially useful, measurable, locally manufacturable, and capable of failing honestly. It is the first Mission Pack, not the product boundary.

## 2. Product thesis

Most agents begin after a user has already translated a problem into a clean task. ORPHEUS begins earlier and finishes later.

It handles the complete transformation:

```text
messy friction
  -> structured Friction Genome
  -> typed Mission IR
  -> evidence graph
  -> candidate portfolio
  -> falsification and deterministic gates
  -> human-approved external action
  -> proof-carrying pilot package
  -> observed outcome
  -> evolved mission memory
```

ORPHEUS is not valuable because it has 18 named agents. It is valuable because the system produces a verifiable state change outside the chat and can explain exactly why that action was allowed.

## 3. The new primitives

### 3.1 Friction Genome

A normalized representation of a real-world problem assembled from text, voice, images, files, measurements, prior attempts, constraints, stakeholders, local context, uncertainty, and approval policy.

Minimum fields:

- beneficiary and operator;
- desired outcome;
- measurable success threshold;
- budget and time constraints;
- geography and environment;
- available materials, skills, and infrastructure;
- safety and legal boundaries;
- prior attempts and observed failures;
- unknowns requiring research;
- actions allowed automatically;
- actions requiring approval;
- evidence freshness requirements.

### 3.2 Mission IR

A typed, versioned intermediate representation compiled from the Friction Genome. It is the contract between agents, tools, state, UI, and recovery.

Required objects:

- `MissionContract`;
- `EvidenceClaim`;
- `CandidateIntervention`;
- `ExperimentPlan`;
- `PolicyDecision`;
- `ActionProposal`;
- `ApprovalRecord`;
- `ActionReceipt`;
- `OutcomeObservation`;
- `EvolutionDecision`.

Every object must include an ID, schema version, mission ID, producer, timestamp, confidence, provenance references, and validation status.

### 3.3 Candidate Portfolio

ORPHEUS must produce multiple genuinely different routes rather than one polished answer.

Each candidate must expose:

- mechanism;
- expected benefit;
- local manufacturing route;
- bill of materials;
- dependencies;
- evidence claims;
- uncertainty;
- test method;
- rejection rule;
- safety risks;
- rollback or disposal path;
- reasons it may fail in the beneficiary's actual context.

### 3.4 Proof-Carrying Action

No external action is considered legitimate unless the action carries its proof bundle.

A proof bundle contains:

- the mission objective and constraints;
- the selected candidate and rejected alternatives;
- evidence links supporting each load-bearing claim;
- deterministic test results;
- uncertainty and unresolved risks;
- policy checks;
- approval identity and timestamp where required;
- exact action payload;
- idempotency key;
- expected state change;
- rollback or compensation plan;
- action result and external receipt;
- hashes for generated artifacts.

This is the main differentiator. ORPHEUS does not merely take action; it takes **auditable, reversible, evidence-linked action**.

### 3.5 Field Twin

A living digital representation of one intervention in one beneficiary context. It stores the assumptions, environmental conditions, configuration, measurements, photos, observations, deviations, and outcome history of the pilot.

A Field Twin is not a simulated claim of physical success. It is the operational record used to compare predicted and observed performance.

### 3.6 Evolution Ledger

RECURSOR-Ω records how the system itself changed after a mission:

- which assumption failed;
- which agent or tool should have detected it earlier;
- which policy or test prevented damage;
- which route was more effective;
- which repeated defect became a regression test;
- which prompt, tool contract, schema, or routing rule changed;
- whether the change improved a golden evaluation.

No self-improvement claim is allowed without a before/after evaluation.

## 4. Primary category and category strategy

ORPHEUS will enter **Taskmaster** because the visible product is a complete multi-step workflow that acts, routes information, manages details, and produces an external outcome.

It will deliberately borrow strengths from the other categories without diluting the submission:

- Collaborative Partner: clarification and structured beneficiary feedback;
- Fortified Enterprise Fleet: agent registry, persistent state, policy enforcement, identity, observability, and long-running execution.

The public story remains one sentence:

> From an unresolved human problem to a proof-carrying pilot—autonomously.

## 5. The unlikely hero

The flagship beneficiary is not an enterprise analyst. It is a small operator with limited money, infrastructure, technical staff, and time.

The first demonstration uses an electricity-free food-preservation mission for a market vendor, small farmer, household, or community operator in a hot climate.

This creates a strong contrast:

- advanced multi-agent infrastructure;
- directed at a neglected, low-resource operational problem;
- producing a locally manufacturable intervention rather than another corporate report.

The beneficiary must remain explicit throughout the UI, state, evidence, and final package.

## 6. Flagship uninterrupted demonstration

The four-minute demonstration must show one uninterrupted transformation.

### Scene 1 — messy friction enters

The user submits a short voice note, photo, or text:

> Produce spoils during power interruptions. Budget is under US$65. Materials must be locally available. No electricity. Climate is hot and humid. The operator can record temperature twice per day.

The system creates a Friction Genome and highlights assumptions and missing data.

### Scene 2 — autonomous mission compilation

ORION compiles the Mission IR. The UI shows the measurable success threshold, approval policy, and execution graph.

### Scene 3 — evidence and candidates

VIGÍA retrieves live sources. ATLAS produces at least four candidates. The candidate board exposes mechanisms, cost, uncertainty, tests, rejection rules, and local manufacturability.

### Scene 4 — falsification

NYX-7, VEGA, RECURSOR-Ω, and NÉMESIS-Ω reject weak or unsupported routes. The audience sees at least one candidate fail for a concrete reason.

### Scene 5 — approved external action

KIRA proposes a pilot package. The human approves it. ORPHEUS then performs an actual external write:

- creates a Drive folder;
- creates a pilot brief;
- creates a Google Sheet BOM and measurement log;
- creates a Calendar follow-up;
- optionally drafts or sends an approved beneficiary/maker message;
- persists an Action Receipt and artifact hashes in Firestore.

No write occurs before approval.

### Scene 6 — state, recovery, and outcome loop

The demo shows the mission record in Firestore and Cloud Run logs. A duplicate action is attempted and blocked by the idempotency key. A simulated restart resumes from the checkpoint without duplicating the package.

A sample outcome observation is then attached to the Field Twin. ORPHEUS compares prediction to observation and records the next learning step without claiming physical validation that did not occur.

## 7. External action package

The first load-bearing connector is Google Workspace because the artifacts are easy for judges to inspect and demonstrate a real state change.

The `PilotPackagePublisher` must create exactly one package after approval:

```text
ORPHEUS-PILOT-{mission_id}/
  01-mission-brief.md or Google Doc
  02-evidence-ledger.csv or Google Sheet
  03-candidate-comparison.csv or Google Sheet
  04-selected-pilot-bom.csv or Google Sheet
  05-build-and-test-protocol.md or Google Doc
  06-risk-and-uncertainty-register.md or Google Doc
  07-measurement-log Google Sheet
  08-beneficiary-brief.md or Google Doc
  09-action-receipt.json
```

Acceptance conditions:

- zero writes before approval;
- exactly one package after approval;
- retrying the same action produces no duplicate files;
- each artifact is linked from the Action Receipt;
- each artifact has a content hash;
- generated claims link to evidence IDs;
- secrets and private chain-of-thought are never written;
- failure leaves a recoverable checkpoint and an explicit partial result.

## 8. Google Cloud architecture

### Required runtime

- Cloud Run: API, Mission Runner, and streaming interface;
- Firestore: Mission IR, checkpoints, approvals, proof ledger, Field Twins;
- Pub/Sub: asynchronous mission and follow-up events;
- Cloud Storage: immutable artifact snapshots and demo evidence;
- Secret Manager: connector credentials;
- Cloud Logging and Trace/OpenTelemetry: auditable execution;
- Gemini through Vertex AI for the final hosted demonstration;
- Google ADK as the orchestration runtime.

### Optional load-bearing bonus models

Additional models are only integrated when they materially improve the mission:

- Gemma: independent low-cost verifier or policy checker;
- a vision-capable Gemini model: interpret photos, sketches, labels, or field observations;
- Veo only if a generated assembly visualization becomes a genuine beneficiary artifact, not decorative bonus chasing.

## 9. Agent topology as responsibilities, not branding

Agents remain only where separation of responsibility is defensible.

- ORION: Mission Compiler and success contract;
- VIGÍA: evidence acquisition and provenance;
- NYX-7: risk discovery and contradiction testing;
- VEGA: experiment design, metrics, and rejection thresholds;
- ATLAS-9: candidate portfolio and system design;
- FORJA CORE: typed contracts, state, retries, idempotency, and recovery;
- FORJA TEST: golden missions, failure injection, and regression gates;
- FORJA UX: beneficiary clarity and judge-visible proof;
- SPARK: deterministic tools and external actions;
- RECURSOR-Ω: evolutionary audit and debt ledger;
- NÉMESIS-Ω: adversarial falsification and lawful alternative search;
- HELIX-8: rubric scoring using evidence only;
- AUREUS-7: resource and sustainability strategy;
- BASTION: policy, identity, approval, and privacy;
- ECHO: provenance and proof ledger;
- RIFT: recovery routes;
- VANTA-0: unconventional lawful alternatives;
- KIRA Ω: conflict resolution and final action decision.

A specialist is not considered active unless it produces a typed state object, test, action, decision, or verified finding.

## 10. Interface contract

The interface stays light and chat-first, but the chat is only the control surface.

### Main zones

- collapsible mission rail;
- central conversation and mission timeline;
- collapsible proof inspector;
- persistent composer;
- candidate portfolio board;
- approval surface;
- artifact and action receipt panel;
- Field Twin outcome panel.

### Public work capsules

Each capsule shows:

- action currently being performed;
- public output summary;
- tool calls and results;
- evidence count;
- state object produced;
- failure and recovery status;
- completion gate.

Private chain-of-thought remains protected.

### Required visible state changes

The UI must visibly show:

- mission compiled;
- candidate generated;
- candidate rejected;
- approval requested;
- approval granted or denied;
- external write started;
- external receipt returned;
- checkpoint persisted;
- duplicate prevented;
- outcome observation attached;
- next cycle proposed.

## 11. Evaluation architecture

Golden missions must cover at least three domains while the video remains focused on one:

1. passive food preservation;
2. household water resilience;
3. open-source technical repair or maintenance.

This proves transfer without turning the demo into a generic platform tour.

Metrics:

- mission compilation validity;
- evidence precision and provenance completeness;
- candidate diversity;
- unsupported-claim rate;
- candidate rejection correctness;
- policy bypass rate;
- duplicate external action rate;
- crash-resume completion rate;
- artifact completeness;
- action receipt integrity;
- beneficiary task completion;
- cost, latency, and model-call budget;
- before/after improvement on repeated failures.

Mandatory red-team cases:

- prompt injection in a retrieved source;
- malicious tool output;
- PII in input or artifact;
- approval bypass attempt;
- malformed Mission IR;
- agent loop or timeout;
- quota exhaustion;
- external write succeeds but receipt persistence fails;
- retry after partial failure;
- duplicate approval event;
- stale evidence;
- unsupported physical-success claim.

## 12. What makes the concept distinctive

The novelty is not any single component. It is the complete, enforced loop:

1. unstructured human friction is compiled into a typed mission;
2. multiple interventions compete rather than one answer being polished;
3. adversarial agents and deterministic gates can kill the preferred route;
4. the winning route must carry evidence, policy, rollback, and uncertainty;
5. the system performs a real external action only after the required approval;
6. the action produces a persistent, machine-readable receipt;
7. field observations update a living intervention record;
8. system evolution is accepted only after measurable regression improvement.

This is **proof-carrying autonomy for neglected real-world problems**.

## 13. Scope control

Broad product, narrow proof.

For the hackathon, ORPHEUS must not attempt to become a full marketplace, autonomous purchasing system, universal browser operator, scientific laboratory, manufacturer, or regulatory authority.

The required end-to-end path is:

```text
one beneficiary friction
-> one mission compilation
-> live evidence
-> at least four candidates
-> at least one rejection
-> one approved pilot package
-> one real external write
-> one durable receipt
-> one recovery/idempotency proof
-> one outcome feedback event
```

Anything that does not strengthen this path is secondary.

## 14. Rubric mapping

### Innovation and operational utility

Evidence required:

- action beyond chat;
- a visible beneficiary;
- a messy, unusual input;
- autonomous multi-step progression;
- multiple candidates and real rejection;
- an actual external state change;
- a proof-carrying receipt;
- a follow-up cycle.

### Architectural discipline

Evidence required:

- typed Mission IR;
- event-sourced or checkpointed state;
- strict agent responsibility boundaries;
- tool isolation;
- identity and approval gates;
- idempotency and compensation;
- error classification and recovery;
- observability;
- golden evaluations and red-team gates.

### Demo and production readiness

Evidence required:

- hosted Cloud Run URL;
- Firestore state visible;
- Cloud logs/traces visible;
- unedited external action;
- reproducible README;
- architecture diagram;
- public repository;
- four-minute public video in English or with English subtitles.

## 15. Implementation critical path

### P0 — Mission compiler

- define schemas;
- compile Friction Genome into Mission IR;
- expose machine-readable state and UI;
- validate and reject malformed missions.

### P0 — Proof-carrying action

- approval state machine;
- Pilot Package Publisher;
- Google Drive/Docs/Sheets/Calendar connector;
- idempotency key;
- Action Receipt;
- rollback/compensation record.

### P0 — Durable mission runtime

- Firestore session/checkpoint service;
- Pub/Sub continuation events;
- crash-safe resume;
- multi-instance duplicate prevention;
- quota-aware scheduling.

### P0 — Evaluation and security

- golden missions;
- OpenTelemetry traces;
- red-team gates;
- proof integrity tests;
- error and recovery dashboards.

### P0 — Cloud proof and demo

- Cloud Run deployment;
- architecture diagram;
- hosted no-login or documented test access;
- four-minute demo script;
- unedited recording;
- final Devpost submission.

### P1 — Multimodal intake

- voice note;
- photo or sketch;
- field observation attachment;
- structured extraction into Friction Genome.

### P1 — Evolution loop

- outcome comparison;
- RECURSOR change proposal;
- golden-eval experiment;
- promote or reject the change based on evidence.

## 16. Kill criteria

The direction fails and must be revised if any of these remain true near submission:

- the system only produces text;
- no external state change exists;
- the video cannot show one uninterrupted mission;
- agents are names without enforceable outputs;
- the system cannot reject its preferred candidate;
- a retry duplicates external artifacts;
- state is lost after restart;
- physical success is claimed without field evidence;
- the user must manually coordinate each agent;
- the public pitch needs more than two sentences to explain the value.

## 17. Final positioning

Name:

**ORPHEUS Ω — Proof-Carrying Mission Foundry**

Primary tagline:

**From an unresolved human problem to a proof-carrying pilot—autonomously.**

Technical one-liner:

**A Google ADK mission compiler that turns messy human friction into competing interventions, falsifies weak routes, executes approved external actions, and evolves from auditable outcomes.**

Flagship story:

**A low-resource operator needs to preserve food without electricity. ORPHEUS researches the evidence, designs locally manufacturable candidates, rejects unsafe or unsuitable routes, publishes an approved pilot package to Google Workspace, records an immutable action receipt, and learns from measured field outcomes.**

## 18. Truth boundary

This direction is ambitious by design, but no component is considered delivered merely because it appears in this document.

Current strengths already present in the repository include the real Google ADK topology, evidence retrieval, candidate generation, deterministic tools, evolutionary audit, public work capsules, Markdown rendering, and an honest local/free-safe execution profile.

The decisive winning capabilities still require implementation and evidence: typed Mission IR, durable Firestore state, real external action, action receipts, crash-safe resume, field feedback, full evaluation results, Cloud Run proof, architecture diagram, and demo video.
