from __future__ import annotations

from copy import deepcopy
from typing import Any


AGENT_TOPOLOGY: dict[str, Any] = {
    "version": "0.5.0",
    "framework": "Google Agent Development Kit (ADK)",
    "root": {
        "name": "orpheus_omega",
        "type": "SequentialAgent",
        "purpose": "Deterministic orchestration of the complete invention-archaeology workflow.",
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
            "name": "spark",
            "type": "LlmAgent",
            "execution": "sequential",
            "output_key": "execution_result",
            "tools": ["plan_human_benefit", "run_reference_mission"],
        },
        {
            "order": 5,
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
            "order": 6,
            "name": "kira",
            "type": "LlmAgent",
            "execution": "sequential",
            "output_key": "kira_decision",
        },
    ],
    "specialist_agent_count": 12,
    "parallel_groups": 2,
    "state_transport": "ADK session state through unique output_key values",
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
    },
}


def get_agent_topology() -> dict[str, Any]:
    """Return a safe copy of the public ADK orchestration topology."""

    return deepcopy(AGENT_TOPOLOGY)
