import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from orpheus.models import Climate, Design, MissionConstraints
from orpheus.pipeline import evaluate_mission
p=json.loads((ROOT/'demo'/'mission.json').read_text())
print(json.dumps(evaluate_mission(Climate(**p['climate']),[Design(**x) for x in p['candidates']],MissionConstraints(**p['constraints'])),indent=2))
