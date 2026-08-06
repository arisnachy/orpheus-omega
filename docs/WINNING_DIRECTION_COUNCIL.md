# ORPHEUS Ω — Winning Direction Council

Status: comparative strategy, not a claim of completed implementation  
Primary objective: maximize probability of winning the All Things Agentic Hackathon  
Primary track under evaluation: Taskmaster

## 1. Hard truth

“An agent team for any mission” is a powerful runtime concept but a weak contest pitch by itself.

Why it can lose:

- the value is too broad to understand in seconds;
- the four-minute demo cannot prove “anything”;
- it resembles general assistants and agent platforms from large vendors;
- the judge may see agent names rather than one resolved human problem;
- it invites overbuilding and unfinished integrations;
- it is difficult to measure whether the mission was truly closed.

Therefore:

> Universal mission capability belongs under the hood. The public product needs one universal human pain and one unforgettable proof.

## 2. Scoring model

Estimated scores assume a strong implementation and are weighted against the official rubric:

- Innovation and operational utility: 40 points
- Architectural discipline and stack: 30 points
- Demo and production readiness: 30 points

Scores are strategic estimates, not judge scores.

## 3. Competing directions

| Rank | Direction | Core promise | Innovation /40 | Architecture /30 | Demo /30 | Total /100 | Council verdict |
|---:|---|---|---:|---:|---:|---:|---|
| 1 | ORPHEUS CLOSURE | Finds important open loops and stays until each is provably closed | 39 | 28 | 29 | **96** | Best balance of universality, human utility, novelty, measurable action, and demo clarity |
| 2 | ORPHEUS RECOVER | Finds money, rights, refunds, warranties, benefits, and credits owed to the user, then pursues recovery | 39 | 25 | 30 | **94** | Highest immediate ROI and easiest outcome to understand; narrower but extremely strong |
| 3 | ORPHEUS RESCUE | Resolves household breakdowns from symptom to diagnosis, warranty/vendor action, appointment, and follow-up | 36 | 26 | 29 | **91** | Excellent BYOF story and visual demo; can expand into Closure later |
| 4 | ORPHEUS CARE CIRCLE | Coordinates family care, appointments, documents, transport, school, and follow-up | 38 | 27 | 24 | **89** | Deep human value, but privacy and high-stakes risks complicate the demo |
| 5 | PROOF-CARRYING MISSION FOUNDRY | Converts messy friction into evidence-backed pilot interventions and external action packages | 35 | 30 | 24 | **89** | Technically excellent and prize-worthy for architecture; less immediately relatable |
| 6 | ORPHEUS AHEAD | Anticipatory life steward that notices needs before the user asks | 34 | 27 | 22 | **83** | Futuristic but crowded by Apple, Google, Microsoft, and general agent products |
| 7 | ORPHEUS MISSION CORPS | Forms a temporary agent team for any stated mission and executes it | 31 | 29 | 20 | **80** | Powerful architecture, vague product; likely to look like an agent framework demo |

## 4. Proposal A — ORPHEUS CLOSURE

### Category

**Autonomous Open-Loop Closure Engine**

### Promise

> It finds what life left unfinished—and stays until it is closed.

### The universal human problem

People live with open loops:

- an unanswered important email;
- an expiring warranty;
- a refund never received;
- a medical or school form not completed;
- an application awaiting a reply;
- a repair with no follow-up;
- a package stuck in transit;
- a subscription that increased in price;
- a bill that looks wrong;
- an appointment requiring documents or transport;
- a promise made in a message but never scheduled.

Most assistants answer requests. ORPHEUS CLOSURE maintains continuity across time and systems.

### Core loop

```text
authorized signals
-> detect candidate open loop
-> calculate urgency, value, risk, and confidence
-> ask whether intervention is permitted
-> create typed mission
-> form the minimum specialist team
-> investigate and prepare routes
-> request approval at the correct boundary
-> execute external action
-> monitor replies or state changes
-> escalate or recover from failure
-> close only with evidence
```

### Dynamic mission team

The user does not select agents.

- Scout: detects and classifies an open loop;
- Investigator: gathers documents, rules, evidence, and contacts;
- Planner: generates resolution routes;
- Negotiator: prepares messages, claims, or escalation;
- Executor: performs approved writes;
- Auditor: verifies closure evidence, idempotency, and unresolved risk;
- KIRA: decides whether to close, continue, escalate, or return control.

The full Constelación remains available, but only the minimum team is activated for each mission.

### Why this is broader without becoming vague

The product is not “does everything.” It does one thing across many domains:

> Close important unfinished matters.

That is a stable product primitive with measurable outcomes.

### Flagship demo

**A washing machine fails while its warranty is close to expiring.**

1. A user provides a short voice note and photo/error code.
2. ORPHEUS finds the purchase receipt and warranty email in authorized Gmail/Drive data.
3. It identifies the deadline and required evidence.
4. It creates alternative routes: safe self-check, warranty claim, authorized technician, replacement contingency.
5. It rejects unsafe repair instructions.
6. It prepares the claim packet and service request.
7. The user approves one action bundle.
8. ORPHEUS sends the approved message to a controlled demo inbox, creates a Drive case folder, creates a Calendar follow-up, and stores an Action Receipt in Firestore.
9. A simulated vendor reply arrives through the demo inbox.
10. ORPHEUS resumes, schedules the visit, blocks duplicate booking, and closes the loop with receipt evidence.

### Measurable proof

- open loop detected;
- deadline extracted;
- documents linked;
- candidate routes generated;
- unsafe route rejected;
- approval captured;
- external message sent;
- folder and follow-up created;
- reply detected;
- duplicate action blocked;
- mission closed with evidence.

## 5. Proposal B — ORPHEUS RECOVER

### Promise

> It finds value owed to you and pursues recovery with your approval.

### Missions

- expiring warranty claims;
- refunds not received;
- duplicate or incorrect charges;
- price protection or credits;
- unused subscriptions;
- travel disruption claims;
- insurance or benefits documentation;
- deposits and reimbursements;
- overdue client invoices;
- merchant disputes.

### Strength

A judge sees immediate value: dollars or rights recovered.

### Weakness

Financial actions and legal claims require careful boundaries. The demo should stop at an approved claim or controlled test transaction rather than autonomously moving real money.

### Best use

Make `Recover` the first Mission Pack inside ORPHEUS CLOSURE.

## 6. Proposal C — ORPHEUS RESCUE

### Promise

> When something in your home breaks, ORPHEUS owns the path from symptom to resolution.

### Missions

- appliance failure;
- water leak or pump problem;
- internet outage;
- air-conditioning failure;
- vehicle or device maintenance;
- warranty and repair coordination.

### Strength

Concrete, visual, personal, and easy to demonstrate with real artifacts.

### Weakness

The product may appear limited to home maintenance unless framed as a Mission Pack.

### Best use

Use `Rescue` as the flagship demo and `Closure` as the category.

## 7. Proposal D — ORPHEUS CARE CIRCLE

### Promise

> A persistent agent team that keeps family care from falling through the cracks.

### Missions

- appointments and referrals;
- school forms and events;
- medications and refill reminders;
- transport and caregiver coordination;
- benefits and insurance paperwork;
- follow-up after results;
- document readiness.

### Strength

Enormous human value and a strong unlikely-hero narrative.

### Weakness

Medical, child, and family data create higher privacy and safety obligations. It is harder to prove a complete real action safely in four minutes.

## 8. Proposal E — Proof-Carrying Mission Foundry

### Promise

> Converts an unresolved problem into competing interventions, falsifies weak routes, and publishes an auditable pilot package.

### Strength

Best architecture story: typed Mission IR, evidence graph, candidate portfolio, approvals, receipts, durable state, evaluation, and evolution.

### Weakness

A “pilot foundry” is less immediately human than “this warranty was about to expire and ORPHEUS resolved it.”

### Best use

Retain its proof-carrying primitives as the architecture of ORPHEUS CLOSURE. Do not lead the public pitch with abstract architecture.

## 9. Proposal F — ORPHEUS AHEAD

### Promise

> Notices what matters before the user asks.

### Strength

Feels futuristic and supports proactive event-driven behavior.

### Weakness

The general-assistant space is crowded. Personal context, cross-app actions, scheduling, monitoring, and proactive notifications are becoming standard platform capabilities.

### Best use

“Ahead” becomes the detection layer of CLOSURE, not the entire product.

## 10. Council debate

### ORION

Winning requires a single recognizable transformation, not maximum feature count. Select `open loop -> verified closure` as the stable product contract.

### NYX-7

Reject “agent team for everything” as public positioning. It is impossible to falsify, impossible to prove in four minutes, and easy for judges to classify as generic agent theater.

### VEGA

Closure is measurable. Define explicit terminal evidence for each mission type and a false-closure test set.

### ATLAS-9

Use a universal Mission IR underneath domain-specific Mission Packs. This preserves breadth without allowing each domain to become custom spaghetti.

### FORJA CORE

Build one end-to-end connector path first: Gmail + Drive + Calendar + Firestore. Add no second ecosystem until idempotency, approvals, crash recovery, and receipts pass.

### FORJA TEST

The demo must include one failure or rejection, one restart/resume, and one duplicate-action attempt. A happy-path-only demo will not prove the architecture.

### FORJA UX

Do not show 18 agents as the primary interface. Show:

- `Detected`;
- `Why now`;
- `Proposed resolution`;
- `Approval required`;
- `Action in progress`;
- `Waiting`;
- `Resolved with proof`.

The specialist team belongs in an expandable audit view.

### AUREUS-7

RECOVER has the clearest economic value and monetization. Use warranties, refunds, and reimbursements as high-value Closure mission packs.

### BASTION

Proactive detection must be opt-in and source-specific. No external write before approval unless an action class was explicitly pre-authorized. Financial transfers, contracts, medical decisions, and irreversible actions always require human approval.

### ECHO

Every closure needs a receipt: what changed, where, when, why, under whose approval, with what evidence, and what remains uncertain.

### RIFT

When a route fails, ORPHEUS must preserve the case and choose another route rather than starting over or declaring failure generically.

### NÉMESIS-Ω

Attack the strongest proposal: CLOSURE can become creepy surveillance, generate false urgency, or annoy the user. The product therefore needs intervention thresholds, confidence, quiet mode, explainable detection, dismissal learning, and a “never monitor this source/category” control.

### KIRA Ω

Adopt CLOSURE as the leading direction. Integrate AHEAD as anticipation, RECOVER and RESCUE as mission packs, and Proof-Carrying Mission Foundry as the internal architecture.

## 11. Final recommended product

### Name

**ORPHEUS Ω CLOSURE**

### Category

**Autonomous Open-Loop Closure Engine**

### Primary tagline

**It finds what life left unfinished—and stays until it is closed.**

### Technical one-liner

**A Google ADK mission system that detects authorized open loops, forms the minimum specialist team, executes approved cross-app actions, survives delays and failures, and closes only with evidence.**

### Product architecture

```text
ORPHEUS AHEAD
proactive detection and prioritization
        ↓
ORPHEUS MISSION CORPS
minimum dynamic team for the case
        ↓
PROOF-CARRYING MISSION FOUNDRY
mission state, candidates, evidence, policy, approval
        ↓
MISSION PACK
Recover / Rescue / Care / Admin / Opportunity
        ↓
ACTION GATEWAY
Gmail / Drive / Calendar / controlled external services
        ↓
CLOSURE LEDGER
receipts, checkpoints, retries, replies, outcome evidence
```

### Flagship Mission Pack

**RESCUE + RECOVER: warranty resolution for a failed appliance.**

This is personal BYOF, understandable, safe enough for a controlled demo, rich enough to justify a multi-agent system, and visibly action-oriented.

## 12. Why this can win

### Innovation and utility

- begins before a clean user request exists;
- solves a universal human problem;
- forms a dynamic specialist team;
- performs real cross-app work;
- remains responsible across waiting periods;
- closes only with proof.

### Architectural discipline

- typed missions and closure contracts;
- durable Firestore checkpoints;
- Pub/Sub or event-driven continuation;
- human approval boundaries;
- idempotent writes;
- tool isolation;
- recovery and compensation;
- audit receipts;
- quota-aware execution;
- golden evals for false closure.

### Demo and production readiness

- one uninterrupted mission;
- visible Gmail/Drive/Calendar changes;
- Firestore state and Cloud Run logs;
- a real pause and resume;
- a duplicate action blocked;
- a final closure receipt.

## 13. Scope lock

For the hackathon, do not build a universal consumer operating system.

Build:

- one open-loop detector using controlled Gmail/Drive inputs;
- one Mission Pack for appliance warranty resolution;
- one dynamic team route;
- one approval gate;
- one external write bundle;
- one reply/resume event;
- one idempotency proof;
- one closure receipt;
- two additional golden Mission Packs in tests only.

## 14. Kill criteria

Do not select CLOSURE if the implementation cannot demonstrate before submission:

- a real external state change;
- durable waiting and resume;
- explicit approval;
- duplicate prevention;
- a meaningful candidate rejection;
- verified terminal evidence;
- a simple two-sentence pitch.

If these cannot be completed, fall back to the narrower ORPHEUS RECOVER demo rather than submitting an unfinished universal product.

## 15. Decision status

Recommended, not yet final.

Do not rewrite the public Devpost submission until:

1. the council recommendation is accepted;
2. the end-to-end vertical slice is implemented;
3. a cloud-backed run produces closure evidence;
4. the video story is reproducible.
