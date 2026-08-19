from __future__ import annotations

import json

from .contracts import Mission
from .engine import SingularityEngine


def run_demo() -> dict[str, object]:
    engine = SingularityEngine()
    result = engine.execute(
        Mission(
            objective="Analyze a text even though no text-analysis tool is installed yet",
            required_capability="text.statistics",
            payload={"text": "KIRA invents tools. KIRA verifies tools. KIRA reuses tools."},
        )
    )
    return {
        "status": result.status,
        "tool_id": result.tool_id,
        "output": result.output,
        "registry": engine.registry.snapshot(),
        "audit_chain_valid": engine.ledger.verify_chain(),
        "receipts": result.receipts,
    }


if __name__ == "__main__":
    print(json.dumps(run_demo(), indent=2, ensure_ascii=False))
