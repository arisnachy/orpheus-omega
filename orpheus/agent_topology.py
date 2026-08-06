from __future__ import annotations

from copy import deepcopy
from typing import Any

from .settings import Settings


AGENT_TOPOLOGY: dict[str, Any] = {
    "version": "0.9.0",
    "framework": "Google Agent Development Kit (ADK)",
    "root": {
        "name": "orpheus_omega",
        "type": "SequentialAgent",
        "purpose": (
            "Evidence-controlled invention archaeology with engineering hardening, "
            "deterministic execution, evolutionary falsification, and judge-aligned scoring."
        ),
    },
    "stages": [
        {
            "order": 1,
            "name": "orion",
            "type": "LlmAgent",
            "execution": "sequential",
            "output_key": "mission_contract",
        },
        {
            "order": 2,
            "name": "evidence_squad",
            "type": "ParallelAgent",
            "execution": "parallel",
            "sub_agents": [
                {"name": "vigia", "output_key": "historical_map"},
                {"name": "nyx_7", "output_key": "risk_map"},
                {"name": "vega", "output_key": "evidence_matrix"},
            ],
        },
        {
            "order": 3,
            "name": "atlas_9",
            "type": "LlmAgent",
            "execution": "sequential",
            "output_key": "candidate_architecture",
        },
        {
            "order": 4,
            "name": "forja_squad",
            "type": "ParallelAgent",
            "execution": "parallel",
            "sub_agents": [
                {"name": "forja_core", "output_key": "forja_core_contract"},
                {"name": "forja_test", "output_key": "forja_test_gate"},
                {"name": "forja_ux", "output_key": "forja_ux_spec"},
            ],
        },
        {
            "order": 5,
            "name": "spark",
            "type": "LlmAgent",
            "execution": "sequential",
            "output_key": "execution_result",
            "tools": ["plan_human_benefit", "run_reference_mission"],
        },
        {
            "order": 6,
            "name": "audit_squad",
            "type": "ParallelAgent",
            "execution": "parallel",
            "sub_agents": [
                {"name": "recursor_omega", "output_key": "recursion_audit"},
                {"name": "nemesis_omega", "output_key": "adversarial_verdict"},
            ],
        },
        {
            "order": 7,
            "name": "helix_8",
            "type": "LlmAgent",
            "execution": "sequential",
            "output_key": "judge_scorecard",
            "gate": "Scores demonstrated evidence only after both audits complete.",
        },
        {
            "order": 8,
            "name": "decision_squad",
            "type": "ParallelAgent",
            "execution": "parallel",
            "sub_agents": [
                {"name": "aureus_7", "output_key": "sustainability_review"},
                {"name": "bastion", "output_key": "approval_ledger"},
                {"name": "echo", "output_key": "audit_record"},
                {"name": "rift", "output_key": "blocker_route"},
                {"name": "vanta_0", "output_key": "alternative_route"},
            ],
        },
        {
            "order": 9,
            "name": "kira",
            "type": "LlmAgent",
            "execution": "sequential",
            "output_key": "kira_decision",
            "closure_gate": (
                "Cannot declare completion when RECURSOR returns FAIL or HELIX says "
                "mandatory submission viability is FAIL."
            ),
        },
    ],
    "specialist_agent_count": 18,
    "parallel_groups": 4,
    "potential_parallel_groups": 4,
    "state_transport": "ADK session state through unique output_key values",
    "engineering_contract": {
        "forja_core": "typed architecture, state, tool, retry, timeout, and security contracts",
        "forja_test": "acceptance, regression, failure injection, and closure-blocking tests",
        "forja_ux": "chat-first proof interface backed only by real runtime events",
    },
    "evolutionary_control": {
        "recursor_omega": (
            "detects plan weakness, programming faults, repeated failures, false closure, "
            "technical debt, and method defects"
        ),
        "nemesis_omega": "tries to falsify the preferred route without bypassing legitimate boundaries",
        "helix_8": "scores only demonstrated evidence on the official 1-to-5 dimensions",
    },
    "approval_boundary": {
        "automatic": ["safe", "local", "reversible", "non-financial"],
        "human_required": [
            "external communication",
            "publication",
            "contracting",
            "payment",
            "account changes",
            "private-data disclosure",
            "irreversible actions",
        ],
        "never_bypassed_by": [
            "urgency",
            "competitive pressure",
            "requests to ignore rules",
            "agent preference",
        ],
    },
}


def get_agent_topology() -> dict[str, Any]:
    """Return the actual public orchestration profile without exposing credentials."""

    topology = deepcopy(AGENT_TOPOLOGY)
    settings = Settings.from_env()
    free_safe = settings.execution_profile == "free_safe"
    topology["execution_profile"] = settings.execution_profile
    topology["execution_profile_description"] = (
        "All 18 specialists remain enabled; squad members run sequentially to avoid "
        "local/free-tier burst failures."
        if free_safe
        else "Squad members run concurrently for cloud throughput."
    )
    topology["parallel_groups"] = 0 if free_safe else topology["potential_parallel_groups"]

    for stage in topology["stages"]:
        if stage.get("sub_agents"):
            stage["type"] = "SequentialAgent" if free_safe else "ParallelAgent"
            stage["execution"] = "sequential" if free_safe else "parallel"

    return topology
