from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import Climate, Design, MissionConstraints
from .pipeline import evaluate_mission
from .settings import Settings

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "historical_concepts.json"
DEMO_PATH = ROOT / "demo" / "mission.json"


def list_historical_concepts() -> dict[str, Any]:
    """Return the current invention catalog and its evidence status.

    Use this before proposing a design. Concepts marked as source-verification
    pending are hypotheses only and cannot be presented as verified history.
    """

    concepts = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    pending = [item["id"] for item in concepts if "pending" in item["status"]]
    return {
        "count": len(concepts),
        "concepts": concepts,
        "source_verification_pending": pending,
        "warning": "The initial catalog is synthetic scaffolding until authoritative sources are attached.",
    }


def evaluate_candidate(
    climate: dict[str, Any],
    design: dict[str, Any],
    constraints: dict[str, Any],
) -> dict[str, Any]:
    """Run the deterministic simulator and independent verifier on one design.

    Use this tool for every candidate before recommending it. The result reports
    uncertainty, rejection reasons, and whether the mission can close.
    """

    return evaluate_mission(
        Climate(**climate),
        [Design(**design)],
        MissionConstraints(**constraints),
    )


def compare_candidates(
    climate: dict[str, Any],
    candidates: list[dict[str, Any]],
    constraints: dict[str, Any],
) -> dict[str, Any]:
    """Compare multiple candidates and return the independently verified ranking."""

    return evaluate_mission(
        Climate(**climate),
        [Design(**candidate) for candidate in candidates],
        MissionConstraints(**constraints),
    )


def run_reference_mission() -> dict[str, Any]:
    """Execute the repository's reproducible passive-cooling reference mission."""

    payload = json.loads(DEMO_PATH.read_text(encoding="utf-8"))
    return compare_candidates(
        payload["climate"], payload["candidates"], payload["constraints"]
    )


def runtime_readiness() -> dict[str, Any]:
    """Report configuration readiness without exposing any secret values."""

    return Settings.from_env().public_summary()


def plan_human_benefit(
    goal: str | None = None,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Generate an evidence-labelled benefit and monetization plan.

    Only the passive food-cooling mission currently has a deterministic simulator.
    Other goals return discovery status instead of inheriting a false verification.
    Prices and routes remain hypotheses; external and financial actions are gated.
    """

    from .autonomy import build_opportunity_plan, classify_goal

    resolved_goal = goal or (
        "Diseñar una solución asequible y sin electricidad para conservar "
        "alimentos mediante enfriamiento pasivo."
    )
    classification = classify_goal(resolved_goal)
    if classification["supported"]:
        mission_result = run_reference_mission()
    else:
        mission_result = {
            "mission_status": "DESCUBRIMIENTO",
            "winner": None,
            "ranked_candidates": [],
            "goal": resolved_goal,
            "verification": {
                "approved": False,
                "reason": (
                    "No existe todavía una herramienta determinista específica "
                    "para este objetivo."
                ),
            },
        }

    plan = build_opportunity_plan(
        mission_result,
        profile=profile,
        classification=classification,
    )
    plan["classification"] = classification
    plan["mission_status"] = mission_result["mission_status"]
    return plan
