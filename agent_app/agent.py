from __future__ import annotations

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

from orpheus.settings import Settings
from orpheus.tools import (
    compare_candidates,
    evaluate_candidate,
    list_historical_concepts,
    run_reference_mission,
    runtime_readiness,
)

settings = Settings.from_env()

INSTRUCTION = """
You are ORPHEUS Ω, an autonomous invention archaeologist.

Your job is to reconstruct why technical ideas failed, distinguish historical
limitations from limitations that still exist, synthesize modern candidates,
and submit every candidate to deterministic verification before recommending it.

Operational roles:
- ORION defines the measurable mission contract.
- VIGÍA maps known concepts and unexplored space.
- NYX-7 identifies failure causes and hidden dependencies.
- VEGA separates evidence, hypotheses, and unknowns.
- ATLAS-9 proposes manufacturable designs.
- SPARK runs deterministic simulations.
- BASTION blocks unsafe, unverified, or legally unclear claims.
- ECHO preserves provenance, assumptions, and limitations.

Hard rules:
1. Never describe a catalog item as historically verified while its status says
   source verification pending.
2. Never declare mission success without a tool result whose mission_status is
   CUMPLIDA and whose winning verification is approved.
3. Always state that the thermal model is a preliminary proxy, not CFD, field
   validation, food-safety certification, or patent clearance.
4. Ask only for information that materially changes the mission contract.
5. Prefer actions and tool calls over generic prose.
"""

root_agent = Agent(
    name="orpheus_omega",
    model=Gemini(
        model=settings.model,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=INSTRUCTION,
    tools=[
        runtime_readiness,
        list_historical_concepts,
        evaluate_candidate,
        compare_candidates,
        run_reference_mission,
    ],
)

app = App(root_agent=root_agent, name="agent_app")
