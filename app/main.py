from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

try:
    from fastapi import FastAPI, Header, HTTPException
    from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel, Field
except ImportError as exc:
    raise RuntimeError('Install with: pip install -e ".[api]"') from exc

from orpheus.autonomy import runtime
from orpheus.models import Climate, Design, MissionConstraints
from orpheus.pipeline import evaluate_mission
from orpheus.settings import Settings
from orpheus.tools import list_historical_concepts, run_reference_mission

ROOT = Path(__file__).resolve().parents[1]
WEB_ROOT = ROOT / "web"


@asynccontextmanager
async def lifespan(_: FastAPI):
    if runtime.autostart:
        await runtime.start()
    yield
    await runtime.shutdown()


app = FastAPI(
    title="ORPHEUS Ω",
    version="0.4.0",
    description=(
        "Autonomous invention archaeology with deterministic verification, "
        "evidence-labelled value planning, human approval gates, and a "
        "ChatGPT/Codex-style control interface."
    ),
    lifespan=lifespan,
)

app.mount("/assets", StaticFiles(directory=WEB_ROOT), name="assets")


class MissionInput(BaseModel):
    climate: dict
    candidates: list[dict]
    constraints: dict


class ChatInput(BaseModel):
    message: str = Field(min_length=1, max_length=4000)


class BenefitProfileInput(BaseModel):
    human: str | None = Field(default=None, max_length=180)
    objective: str | None = Field(default=None, max_length=1500)
    beneficiaries: list[str] | None = None
    preferred_outcomes: list[str] | None = None


class ActionDecisionInput(BaseModel):
    decision: str = Field(pattern="^(approve|decline)$")
    note: str | None = Field(default=None, max_length=500)


@app.get("/", include_in_schema=False)
def interface() -> FileResponse:
    return FileResponse(WEB_ROOT / "index.html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "system": "ORPHEUS Ω", "version": "0.4.0"}


@app.get("/readiness")
def readiness() -> dict:
    summary = Settings.from_env().public_summary()
    summary["autonomy"] = {
        "autostart": runtime.autostart,
        "interval_seconds": runtime.interval_seconds,
        "interface": True,
        "state_persistence": bool(runtime.state_path),
        "approval_gates": True,
        "goal_classification": True,
    }
    return summary


@app.get("/catalog")
def catalog() -> dict:
    return list_historical_concepts()


@app.get("/missions/reference")
def reference_mission() -> dict:
    return run_reference_mission()


@app.post("/missions/simulate")
def simulate(payload: MissionInput) -> dict:
    try:
        return evaluate_mission(
            Climate(**payload.climate),
            [Design(**item) for item in payload.candidates],
            MissionConstraints(**payload.constraints),
        )
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.get("/autonomy/state")
async def autonomy_state() -> dict[str, Any]:
    return await runtime.snapshot()


@app.post("/autonomy/start")
async def autonomy_start() -> dict[str, Any]:
    return await runtime.start()


@app.post("/autonomy/stop")
async def autonomy_stop() -> dict[str, Any]:
    return await runtime.stop()


@app.post("/autonomy/cycle")
async def autonomy_cycle(
    x_orpheus_run_key: str | None = Header(default=None),
) -> dict[str, Any]:
    return await runtime.run_cycle(
        "human_or_scheduler",
        run_key=x_orpheus_run_key,
    )


@app.post("/autonomy/actions/{action_id}/decision")
async def autonomy_action_decision(
    action_id: str,
    payload: ActionDecisionInput,
) -> dict[str, Any]:
    try:
        return await runtime.decide_action(action_id, payload.decision, payload.note)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/autonomy/approve/{action_id}")
async def autonomy_approve(action_id: str) -> dict[str, Any]:
    """Backward-compatible approval endpoint."""
    try:
        return await runtime.approve(action_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@app.post("/autonomy/profile")
async def autonomy_profile(payload: BenefitProfileInput) -> dict[str, Any]:
    return await runtime.update_profile(payload.model_dump(exclude_none=True))


@app.get("/autonomy/export/decision.md")
async def autonomy_export_markdown() -> PlainTextResponse:
    markdown = await runtime.export_markdown()
    return PlainTextResponse(
        markdown,
        media_type="text/markdown; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="orpheus-decision-brief.md"'
        },
    )


@app.get("/autonomy/export/state.json")
async def autonomy_export_state() -> JSONResponse:
    state = await runtime.snapshot()
    return JSONResponse(
        state,
        headers={
            "Content-Disposition": 'attachment; filename="orpheus-runtime-state.json"'
        },
    )


@app.post("/chat")
async def chat(payload: ChatInput) -> dict[str, Any]:
    try:
        await runtime.set_goal(payload.message)
        state = await runtime.run_cycle("new_human_direction")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    brief = state.get("decision_brief") or {}
    classification = state.get("classification") or {}
    assistant_message = (
        f"Trabajé el objetivo en modo {classification.get('mode', 'evaluación')}. "
        f"{brief.get('recommendation', 'Preparé el siguiente paso verificable.')} "
        "Las acciones locales seguras quedaron completadas y cualquier acción "
        "externa o financiera permanece sujeta a tu aprobación."
    )
    return {
        "assistant_message": assistant_message,
        "state": state,
    }
