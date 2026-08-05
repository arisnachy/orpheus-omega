# ORPHEUS Ω engineering guidance

- Preserve deterministic verification as the authority for mission closure.
- Never allow an LLM response alone to set `mission_status=CUMPLIDA`.
- Keep all credentials in environment variables or managed service identity.
- Do not claim the synthetic concept catalog is authoritative evidence.
- Every new agent tool must return JSON-compatible data and include a precise docstring.
- Run unit tests and `scripts/run_demo.py` after every behavioral change.
- The hackathon target is Taskmaster using Gemini 3.5 or newer, Google ADK, and Google Cloud.
