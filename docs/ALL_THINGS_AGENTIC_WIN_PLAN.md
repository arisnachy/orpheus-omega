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
3. Explore and classify historical approaches.
4. Generate multiple candidate combinations.
5. Reject at least one candidate using deterministic validation.
6. Select a final candidate with explicit uncertainty.
7. Produce beneficiary, cost, margin, licensing, funding, and pilot hypotheses.
8. Queue external or financial actions for human approval rather than executing them silently.

### Architectural Discipline & Tech Stack — 30%

Evidence to surface:

- Google ADK multi-agent orchestration.
- Gemini 3.5+ for hypothesis generation and technical reasoning.
- FastAPI control plane.
- Long-running autonomous cycles with start, pause, resume, and manual trigger.
- Persistent mission state and provenance.
- Deterministic simulation separated from model reasoning.
- Independent verifier before mission completion.
- Explicit safety and approval gates.
- Environment-only secrets and payment configuration.
- Cloud Run deployment path and scale-to-zero configuration.
- Automated tests and GitHub Actions.

### Demo & Production Readiness — 30%

The four-minute demo should be one continuous story:

- 0:00–0:25 — The problem: useful inventions can die because they arrived before enabling technology.
- 0:25–0:50 — Start the passive-cooling mission from the live interface.
- 0:50–1:40 — Show the autonomous agent timeline and intermediate decisions.
- 1:40–2:25 — Show one candidate rejected by deterministic evidence and the final candidate selected.
- 2:25–3:05 — Show beneficiary and monetization hypotheses plus the approval queue.
- 3:05–3:35 — Show architecture and safety boundaries.
- 3:35–4:00 — Show Cloud Run evidence, repository, tests, and reproducible setup.

## Required submission evidence

- Public repository URL.
- Reproducible local and Cloud Run setup in README.
- Architecture diagram exported to PNG or PDF.
- Approximately four-minute demo video.
- Proof that the backend ran on Google Cloud.
- Clear disclosure of pre-existing libraries, public datasets, templates, and open-source components.
- Project start date recorded as August 4, 2026.

## Truth boundary

Do not claim field validation, CFD validation, food-safety approval, patent clearance, measured customer demand, confirmed pricing, confirmed grants, confirmed customers, or guaranteed revenue unless real evidence is added.

Gemini may propose hypotheses. Deterministic tools and an independent verifier decide whether a technical mission passes. The human approves external communication, contracting, publication, payment, and irreversible actions.

## Immediate blockers before submission

1. Replace historical source placeholders with authoritative provenance.
2. Produce and commit the final architecture diagram.
3. Deploy once to Google Cloud and preserve visible proof.
4. Record the continuous demo video.
5. Add the final hosted URL if available.
6. Complete the Devpost submission fields and upload the architecture diagram.
