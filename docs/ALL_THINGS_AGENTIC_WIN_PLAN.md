# ORPHEUS Ω — All Things Agentic Win Plan

## Target

Primary category: **Taskmaster**

Additional prize positioning:

- **Individual/Hobbyist — Best Team/Solo Build**
- **Best Architectural Design**
- **Honorable Mention**

ORPHEUS is positioned as an autonomous workflow rather than a chatbot. A human provides a measurable mission; the system decomposes it, researches technical history, reconstructs failure causes, generates candidate designs, runs deterministic validation, rejects unsupported options, ranks benefit and sustainability paths, and returns approval-gated external actions.

## Why this entry fits the judging rubric

### Innovation & Operational Utility — 40%

ORPHEUS removes the manual work of searching fragmented technical history, deciding why an invention failed, testing whether modern technology changes the result, and converting the verified result into a practical benefit plan.

The demo must show the agent doing work end to end:

1. Receive a measurable mission.
2. Create an autonomous mission contract.
3. Explore and classify historically documented approaches.
4. Generate multiple candidate combinations.
5. Reject at least one candidate using deterministic validation.
6. Select a final candidate with explicit uncertainty.
7. Produce beneficiary, cost, margin, licensing, funding, and pilot hypotheses.
8. Queue external or financial actions for human approval rather than executing them silently.

### Architectural Discipline & Tech Stack — 30%

Evidence now present in the repository:

- A real Google ADK `SequentialAgent` root.
- Twelve specialist `LlmAgent` instances.
- Two actual `ParallelAgent` squads.
- Unique ADK `output_key` state channels.
- Live `Runner.run_async()` event streaming through FastAPI.
- NDJSON trace of visible model output, tool calls, tool results, state changes, completion, and errors.
- A strict mock-mode gate that refuses to fabricate cloud-agent execution.
- Trace privacy controls that suppress model thought text, binaries, and file URIs.
- Gemini 3.5+ configuration for hypothesis generation and technical reasoning.
- FastAPI deterministic control plane.
- Long-running autonomous cycles with start, pause, resume, and manual trigger.
- Persistent mission state and provenance.
- Deterministic simulation separated from model reasoning.
- Independent verifier before mission completion.
- Explicit safety and approval gates.
- Environment-only secrets and payment configuration.
- Cloud Run deployment path and scale-to-zero configuration.
- Automated tests and GitHub Actions.
- Machine-readable architecture topology at `/architecture/agents`.

### Demo & Production Readiness — 30%

The four-minute demo should be one continuous story:

- 0:00–0:25 — The problem: useful inventions can die because they arrived before enabling technology.
- 0:25–0:50 — Start the passive-cooling mission from `/adk` on the deployed service.
- 0:50–1:40 — Show the real ADK events arriving from ORION, the parallel evidence squad, ATLAS-9, SPARK, the decision squad, and KIRA.
- 1:40–2:25 — Show SPARK's deterministic tool call, one rejected candidate, and the selected candidate.
- 2:25–3:05 — Move to `/` and show beneficiary and monetization hypotheses plus the approval queue.
- 3:05–3:35 — Show the actual ADK hierarchy, source provenance, trace privacy, and safety boundaries.
- 3:35–4:00 — Show Cloud Run evidence, repository, green verification, and reproducible setup.

## Required submission evidence

- Public repository URL.
- Reproducible local and Cloud Run setup in README.
- Architecture diagram exported to PNG or PDF.
- Approximately four-minute demo video.
- Proof that the backend ran on Google Cloud.
- Clear disclosure of pre-existing libraries, public datasets, papers, templates, and open-source components.
- Project start date recorded as August 4, 2026.

## Truth boundary

Do not claim field validation, CFD validation, food-safety approval, patent clearance, measured customer demand, confirmed pricing, confirmed grants, confirmed customers, or guaranteed revenue unless real evidence is added.

A source can verify a bounded mechanism-level claim without validating the current ORPHEUS design. Gemini may propose hypotheses. Deterministic tools and an independent verifier decide whether a technical mission passes. The public event trace shows actions and evidence, never private chain-of-thought. The human approves external communication, contracting, publication, payment, and irreversible actions.

## Completed milestones

1. Replaced prompt-only specialist roleplay with a real twelve-agent Google ADK workflow.
2. Added automated tests that inspect the actual sequential and parallel hierarchy.
3. Added explicit session-state transport through unique `output_key` values.
4. Added a public machine-readable architecture endpoint.
5. Replaced all five historical source placeholders with bounded primary or peer-reviewed engineering provenance.
6. Added catalog integrity checks that distinguish source verification from application validation.
7. Added a real ADK Runner bridge with complete event consumption.
8. Added a light `/adk` console for live agent and tool traces.
9. Added tests proving that mock mode cannot impersonate a real run and private thought text cannot enter the trace.
10. Updated the public Devpost project to match the repository's real implementation and remaining proof.

## Immediate blockers before submission

1. Execute `/adk` against a real Gemini or Vertex backend and preserve the trace as demo evidence.
2. Produce and commit the final architecture diagram as PNG or PDF.
3. Deploy once to Google Cloud and preserve visible proof.
4. Record the continuous demo video.
5. Add the final hosted URL if available.
6. Attach ORPHEUS Ω to the All Things Agentic Hackathon and complete the submission fields.
7. Upload the architecture diagram and demo video before final submission.
