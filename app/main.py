from __future__ import annotations

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError as exc:
    raise RuntimeError('Install with: pip install -e ".[api]"') from exc

from orpheus.models import Climate, Design, MissionConstraints
from orpheus.pipeline import evaluate_mission
from orpheus.settings import Settings
from orpheus.tools import list_historical_concepts, run_reference_mission

app = FastAPI(title="ORPHEUS Ω", version="0.2.0")


class MissionInput(BaseModel):
    climate: dict
    candidates: list[dict]
    constraints: dict


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "system": "ORPHEUS Ω", "version": "0.2.0"}


@app.get("/readiness")
def readiness() -> dict:
    return Settings.from_env().public_summary()


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
