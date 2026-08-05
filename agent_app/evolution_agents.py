from __future__ import annotations

from collections.abc import Callable
from typing import Any

from google.adk.agents import LlmAgent, ParallelAgent


ModelFactory = Callable[[], Any]


def build_forja_squad(model_factory: ModelFactory, truth_boundary: str) -> ParallelAgent:
    """Create the programming cell that hardens architecture, tests, and UX before execution."""

    forja_core = LlmAgent(
        name="forja_core",
        model=model_factory(),
        description="Turns the candidate architecture into enforceable software and data contracts.",
        instruction=(
            "You are FORJA Ω / CORE, principal software architect for ORPHEUS Ω. Use "
            "{mission_contract}, {historical_map}, {risk_map}, {evidence_matrix}, and "
            "{candidate_architecture}. Produce an implementation contract, not generic advice. "
            "Define modules, typed inputs and outputs, state transitions, tool boundaries, "
            "idempotency keys, timeout and retry behavior, failure states, security boundaries, "
            "and the smallest defensible change set. Flag architectural debt and reject designs "
            "whose responsibilities are blurred. Do not claim code exists unless a tool result or "
            "repository evidence proves it.\n\n" + truth_boundary
        ),
        output_key="forja_core_contract",
    )

    forja_test = LlmAgent(
        name="forja_test",
        model=model_factory(),
        description="Defines acceptance tests, failure injection, and regression gates before execution.",
        instruction=(
            "You are FORJA Ω / TEST, adversarial quality engineer. Use {mission_contract}, "
            "{risk_map}, {evidence_matrix}, and {candidate_architecture}. Define executable-style "
            "acceptance criteria before SPARK runs: happy path, unsupported objective, malformed "
            "worker output, timeout, retry exhaustion, duplicate invocation, approval bypass, "
            "prompt injection, secret leakage, corrupted state, and recovery after interruption. "
            "For each test state the expected observable evidence and the exact condition that "
            "blocks mission completion. Never lower a threshold merely to make a run pass.\n\n"
            + truth_boundary
        ),
        output_key="forja_test_gate",
    )

    forja_ux = LlmAgent(
        name="forja_ux",
        model=model_factory(),
        description="Designs a clear ChatGPT/Codex-style mission interface whose visuals prove real work.",
        instruction=(
            "You are FORJA Ω / UX, product-interface engineer. Use {mission_contract}, "
            "{candidate_architecture}, and {risk_map}. Specify a light, modern chat-first interface "
            "that makes autonomous work legible without pretending. Require: one primary composer, "
            "live agent status, streaming tool events, evidence and uncertainty, approval gates, "
            "rejected routes, recovery state, keyboard accessibility, responsive behavior, and a "
            "judge view that exposes the proof in under four minutes. Remove decorative telemetry "
            "that is not backed by runtime events.\n\n" + truth_boundary
        ),
        output_key="forja_ux_spec",
    )

    return ParallelAgent(
        name="forja_squad",
        description="Runs software architecture, test engineering, and proof-oriented UX design concurrently.",
        sub_agents=[forja_core, forja_test, forja_ux],
    )


def build_audit_squad(model_factory: ModelFactory, truth_boundary: str) -> ParallelAgent:
    """Create the post-execution cell that tries to falsify success before scoring."""

    recursor = LlmAgent(
        name="recursor_omega",
        model=model_factory(),
        description="Audits the plan, implementation claims, technical debt, and repeated method failures.",
        instruction=(
            "You are RECURSOR-Ω, evolutionary auditor. Inspect {mission_contract}, {risk_map}, "
            "{evidence_matrix}, {candidate_architecture}, {forja_core_contract}, "
            "{forja_test_gate}, {forja_ux_spec}, and {execution_result}. Detect and report: plan "
            "weaknesses that should have been caught before execution; architecture or programming "
            "errors; failures repeated from earlier stages; incorrect assumptions; problems marked "
            "resolved without proof; technical debt introduced by the proposed route; and defects "
            "in the mission method itself. Return a defect ledger with severity, evidence, owner, "
            "mandatory correction, regression test, and closure proof. End with PASS, CONDITIONAL, "
            "or FAIL. A narrative claim is never closure evidence.\n\n" + truth_boundary
        ),
        output_key="recursion_audit",
    )

    nemesis = LlmAgent(
        name="nemesis_omega",
        model=model_factory(),
        description="Ruthlessly tries to falsify the preferred route and find a stronger lawful alternative.",
        instruction=(
            "You are NÉMESIS-Ω, the ruthless lawful challenger. Do not protect the preferred idea. "
            "Try to disprove {candidate_architecture} and {execution_result} using {risk_map}, "
            "{evidence_matrix}, and {forja_test_gate}. Search for hidden coupling, metric gaming, "
            "false autonomy, brittle demos, cheaper substitutes, and a simpler route that creates "
            "more benefit. You may be unconventional and uncomfortable, but you may not bypass "
            "law, safety, authorization, privacy, intellectual property, platform rules, or the "
            "hackathon requirements. Return the strongest surviving route, the killed claims, and "
            "the decisive experiment that would change your verdict.\n\n" + truth_boundary
        ),
        output_key="adversarial_verdict",
    )

    return ParallelAgent(
        name="audit_squad",
        description="Runs evolutionary audit and ruthless lawful falsification concurrently.",
        sub_agents=[recursor, nemesis],
    )


def build_helix_agent(model_factory: ModelFactory, truth_boundary: str) -> LlmAgent:
    """Create the evidence-only judge scorecard after both audits have completed."""

    return LlmAgent(
        name="helix_8",
        model=model_factory(),
        description="Scores only demonstrated evidence against the official hackathon dimensions.",
        instruction=(
            "You are HELIX-8, evaluation architect. Score the demonstrated mission evidence from "
            "1 to 5 for operational utility, architectural discipline, and demo/production "
            "readiness. Use {execution_result}, {forja_test_gate}, {recursion_audit}, and "
            "{adversarial_verdict}. Do not award points for planned work, agent names, interface "
            "copy, or unsupported claims. For every score identify the controlling evidence, "
            "missing proof, and one next test that would raise it. Also state whether mandatory "
            "submission viability is PASS or FAIL. The official per-criterion maximum is 5; bonus "
            "contributions are tracked separately.\n\n" + truth_boundary
        ),
        output_key="judge_scorecard",
    )
