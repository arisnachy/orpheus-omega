# KIRA Singularity Engine — v0.1

## Goal

Turn KIRA from a fixed assistant into a controlled capability-expansion runtime. The engine does **not** grant itself unrestricted permissions. It may identify a missing capability, forge a candidate tool, test it, pass it through Gate 0, register it, use it, and leave tamper-evident receipts.

## Canonical lifecycle

`MISSION -> GAP -> INVENT -> TEST -> VERIFY -> REGISTER -> USE -> REUSE`

### Invariants

1. **Fail closed.** If synthesis or verification cannot prove a tool admissible, the mission returns without installing it.
2. **No silent capability escalation.** v0 admits only `pure_compute` tools.
3. **Every new tool must ship with self-tests.**
4. **Registry is capability-oriented.** Missions ask for capabilities, not implementation names.
5. **Auditability.** Every mission/forge/gate/register/use transition emits a SHA-256 chained receipt.
6. **Reuse before reinvention.** Existing verified capabilities are used directly; the forge is invoked only on a true gap.

## v0.1 proof

The demo starts with an empty registry and receives a mission requiring `text.statistics`. The engine detects the missing capability, asks the deterministic v0 forge for a candidate, executes candidate self-tests, passes Gate 0, registers `forge-text-statistics@0.1.0`, executes the tool, verifies the receipt hash-chain, and reuses the registered tool on later missions without forging it again.

## Why the first forge is deterministic

Arbitrary generated-code execution would create a false sense of autonomy while weakening isolation. v0 therefore proves the lifecycle using a deterministic synthesizer. The interfaces are intentionally separable so a later LLM-backed forge can emit source artifacts into a real sandbox and still be subject to the same Gate 0 and registry contracts.

## Roadmap

### v0.2 — Artifact forge
- Candidate source emitted as an artifact, never directly executed.
- AST policy inspection and dependency manifest.
- Reproducible test bundle.
- Signed tool manifest.

### v0.3 — Isolated execution
- Disposable container/microVM runner.
- CPU, memory, wall-clock and filesystem limits.
- Default-deny network egress.
- Explicit permission broker for connectors.

### v0.4 — Evidence-driven promotion
- Adversarial tests.
- Regression suite.
- Benchmark versus existing tools.
- Rollback and quarantine.

### v0.5 — Composition
- Planner can combine multiple verified tools into a new composite capability.
- Composite tools inherit the union of permissions and must pass Gate 0 again.

### v1.0 — Controlled self-expansion
- LLM-backed candidate generation.
- Multi-agent review (inventor, breaker, verifier).
- Persistent capability catalog.
- Tool provenance, version pinning and revocation.
- Human approval policy for medium/high-risk capability classes.

## Security boundary

The engine may expand *capability*, not *authority*. A generated tool cannot obtain permissions that the runtime did not explicitly grant. Intelligence can grow while privilege remains bounded.
