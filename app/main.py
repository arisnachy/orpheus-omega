try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ImportError as exc:
    raise RuntimeError('Install with: pip install -e ".[api]"') from exc
from orpheus.models import Climate, Design, MissionConstraints
from orpheus.pipeline import evaluate_mission

app=FastAPI(title='ORPHEUS Ω',version='0.1.0')
class MissionInput(BaseModel):
    climate: dict
    candidates: list[dict]
    constraints: dict
@app.get('/health')
def health(): return {'status':'ok','system':'ORPHEUS Ω'}
@app.post('/missions/simulate')
def simulate(payload: MissionInput):
    return evaluate_mission(Climate(**payload.climate),[Design(**x) for x in payload.candidates],MissionConstraints(**payload.constraints))
