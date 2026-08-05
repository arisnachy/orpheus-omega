# ORPHEUS Ω

**The Autonomous Invention Archaeologist**

ORPHEUS Ω searches technical history, reconstructs why abandoned inventions failed, and tests whether modern technology can revive them.

## Initial mission

Design an affordable, manufacturable, grid-free food-preservation device by combining historically documented passive-cooling concepts.

## What this initial scaffold proves

- deterministic, climate-aware cooling estimates;
- explicit rejection reasons for weak, expensive, or unmanufacturable designs;
- ranking of competing concepts;
- an independent verifier that alone can close the mission;
- reproducible tests and a runnable demo.

It does **not** yet claim field validation, food-safety approval, patent clearance, or experimentally measured performance.

## Run

```bash
python -m unittest discover -s tests -v
python scripts/run_demo.py
```

Optional API:

```bash
pip install -e ".[api]"
uvicorn app.main:app --reload
```

## Core rule

Gemini and the agents may propose hypotheses. Deterministic tools and an independent verifier decide whether the mission passes.
