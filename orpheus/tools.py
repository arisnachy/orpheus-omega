from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .models import Climate, Design, MissionConstraints
from .pipeline import evaluate_mission
from .settings import Settings

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "data" / "historical_concepts.json"
DEMO_PATH = ROOT / "demo" / "mission.json"
CROSSREF_WORKS_URL = "https://api.crossref.org/works"
RESEARCH_TIMEOUT_SECONDS = 12
MAX_RESEARCH_RESULTS = 8


def _clean_text(value: Any) -> str | None:
    if isinstance(value, str):
        cleaned = " ".join(value.split())
        return cleaned or None
    if isinstance(value, list):
        for item in value:
            cleaned = _clean_text(item)
            if cleaned:
                return cleaned
    return None


def _published_year(item: dict[str, Any]) -> int | None:
    for field in ("published-print", "published-online", "published", "issued"):
        date_parts = ((item.get(field) or {}).get("date-parts") or [])
        if date_parts and date_parts[0]:
            try:
                return int(date_parts[0][0])
            except (TypeError, ValueError, IndexError):
                continue
    return None


def _authors(item: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for author in item.get("author") or []:
        if not isinstance(author, dict):
            continue
        given = _clean_text(author.get("given")) or ""
        family = _clean_text(author.get("family")) or ""
        name = " ".join(part for part in (given, family) if part).strip()
        if name:
            names.append(name)
        if len(names) >= 6:
            break
    return names


def search_scholarly_evidence(query: str, limit: int = 5) -> dict[str, Any]:
    """Search live scholarly metadata through the public Crossref REST API.

    Use this tool to obtain current titles, publication years, authors, DOI links,
    venues, and citation metadata relevant to a mission. The returned records are
    discovery evidence only: metadata relevance does not validate a mechanism,
    design, safety claim, patent position, or commercial conclusion.
    """

    normalized_query = " ".join(str(query or "").split())
    if len(normalized_query) < 3:
        raise ValueError("query must contain at least three visible characters")
    if len(normalized_query) > 500:
        raise ValueError("query must contain at most 500 characters")

    try:
        bounded_limit = max(1, min(int(limit), MAX_RESEARCH_RESULTS))
    except (TypeError, ValueError) as exc:
        raise ValueError("limit must be an integer") from exc

    params = {
        "query.bibliographic": normalized_query,
        "rows": bounded_limit,
        "sort": "relevance",
        "order": "desc",
    }
    request_url = f"{CROSSREF_WORKS_URL}?{urlencode(params)}"
    request = Request(
        request_url,
        headers={
            "Accept": "application/json",
            "User-Agent": (
                "ORPHEUS-OMEGA/0.9 "
                "(https://github.com/arisnachy/orpheus-omega; scholarly-metadata-research)"
            ),
        },
    )

    retrieved_at = datetime.now(timezone.utc).isoformat()
    try:
        with urlopen(request, timeout=RESEARCH_TIMEOUT_SECONDS) as response:
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
        return {
            "status": "unavailable",
            "provider": "Crossref REST API",
            "query": normalized_query,
            "retrieved_at": retrieved_at,
            "results": [],
            "error_type": type(exc).__name__,
            "message": "Live scholarly metadata could not be retrieved for this run.",
            "truth_boundary": (
                "No external evidence was obtained. The mission must not treat this "
                "failed lookup as supporting evidence."
            ),
        }

    raw_items = (((payload or {}).get("message") or {}).get("items") or [])
    results: list[dict[str, Any]] = []
    for item in raw_items[:bounded_limit]:
        if not isinstance(item, dict):
            continue
        doi = _clean_text(item.get("DOI"))
        doi_url = f"https://doi.org/{doi}" if doi else None
        record_url = _clean_text(item.get("URL")) or doi_url
        title = _clean_text(item.get("title"))
        if not title:
            continue
        score = item.get("score")
        try:
            relevance_score = round(float(score), 3) if score is not None else None
        except (TypeError, ValueError):
            relevance_score = None
        results.append(
            {
                "title": title,
                "authors": _authors(item),
                "year": _published_year(item),
                "venue": _clean_text(item.get("container-title")),
                "type": _clean_text(item.get("type")),
                "doi": doi,
                "url": record_url,
                "citation_count": item.get("is-referenced-by-count"),
                "relevance_score": relevance_score,
            }
        )

    return {
        "status": "ok",
        "provider": "Crossref REST API",
        "provider_endpoint": CROSSREF_WORKS_URL,
        "query": normalized_query,
        "retrieved_at": retrieved_at,
        "result_count": len(results),
        "results": results,
        "truth_boundary": (
            "These are live bibliographic metadata records. Titles, DOI links, and "
            "publication metadata support discovery and provenance checking only; "
            "they do not by themselves verify the ORPHEUS application."
        ),
    }


def _live_research_enabled() -> bool:
    """Avoid network calls in mock/CI mode while enabling them for real Gemini runs."""

    return Settings.from_env().llm_backend in {"gemini_api", "vertex_ai"}


def _concept_source_issues(concept: dict[str, Any]) -> list[str]:
    """Return provenance defects without trying to access the network at runtime."""

    issues: list[str] = []
    concept_id = str(concept.get("id") or "unknown")
    sources = concept.get("sources") or []
    if concept.get("source_verification") != "verified":
        issues.append(f"{concept_id}: source_verification is not verified")
    if not sources:
        issues.append(f"{concept_id}: no sources attached")
    for index, source in enumerate(sources, start=1):
        prefix = f"{concept_id}: source {index}"
        if not source.get("title"):
            issues.append(f"{prefix} has no title")
        if not source.get("url"):
            issues.append(f"{prefix} has no stable URL")
        if not source.get("evidence_type"):
            issues.append(f"{prefix} has no evidence_type")
        if not source.get("supports"):
            issues.append(f"{prefix} has no bounded support statement")
    return issues


def list_historical_concepts() -> dict[str, Any]:
    """Return the concept catalog, provenance, validation gaps, and live research.

    A verified source establishes only the bounded mechanism-level claim stated in
    ``supports``. It does not validate the current ORPHEUS design, target climate,
    food safety, manufacturability, patent position, or commercial performance.
    """

    concepts = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    source_issues = [
        issue
        for concept in concepts
        for issue in _concept_source_issues(concept)
    ]
    pending_sources = [
        item["id"]
        for item in concepts
        if item.get("source_verification") != "verified"
    ]
    application_pending = [
        item["id"]
        for item in concepts
        if item.get("application_validation") != "verified"
    ]
    source_count = sum(len(item.get("sources") or []) for item in concepts)

    if source_issues:
        warning = (
            "The catalog contains provenance defects. Entries with defects remain "
            "hypotheses until corrected."
        )
    else:
        warning = (
            "Primary sources document the bounded mechanisms only. Every current "
            "ORPHEUS candidate still requires mission-specific simulation, prototype, "
            "field, safety, and commercial validation as applicable."
        )

    if _live_research_enabled():
        live_research = search_scholarly_evidence(
            "passive evaporative radiative cooling food preservation", limit=5
        )
    else:
        live_research = {
            "status": "disabled",
            "provider": "Crossref REST API",
            "results": [],
            "reason": "Live research is disabled in mock/CI mode.",
        }

    return {
        "count": len(concepts),
        "source_count": source_count,
        "concepts": concepts,
        "source_verification_pending": pending_sources,
        "application_validation_pending": application_pending,
        "provenance_complete": not source_issues,
        "provenance_issues": source_issues,
        "live_research": live_research,
        "warning": warning,
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

    summary = Settings.from_env().public_summary()
    summary["public_research"] = {
        "enabled": _live_research_enabled(),
        "provider": "Crossref REST API",
        "requires_additional_api_key": False,
        "scope": "live scholarly metadata, DOI links, authors, venues, and years",
        "not_in_scope": "general web browsing or full-text validation",
    }
    return summary


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
    if _live_research_enabled():
        plan["live_research"] = search_scholarly_evidence(resolved_goal, limit=5)
    else:
        plan["live_research"] = {
            "status": "disabled",
            "provider": "Crossref REST API",
            "results": [],
            "reason": "Live research is disabled in mock/CI mode.",
        }
    return plan
