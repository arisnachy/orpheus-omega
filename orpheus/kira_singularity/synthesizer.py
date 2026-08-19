from __future__ import annotations

import re
from collections import Counter

from .contracts import Risk, ToolCandidate, ToolSpec


class SynthesisError(RuntimeError):
    pass


class BuiltinSynthesizer:
    """Deterministic v0 forge.

    It proves the full forge lifecycle without arbitrary code execution. Later
    synthesizers can generate source artifacts and submit them to stronger sandboxes.
    """

    def synthesize(self, capability: str) -> ToolCandidate:
        if capability != "text.statistics":
            raise SynthesisError(f"No safe v0 synthesis recipe for capability: {capability}")

        def handler(payload: dict[str, object]) -> dict[str, object]:
            text = str(payload.get("text", ""))
            words = re.findall(r"\b\w+\b", text.lower(), flags=re.UNICODE)
            counts = Counter(words)
            return {
                "characters": len(text),
                "words": len(words),
                "unique_words": len(counts),
                "top_words": counts.most_common(5),
            }

        def self_test_empty() -> bool:
            return handler({"text": ""}) == {
                "characters": 0,
                "words": 0,
                "unique_words": 0,
                "top_words": [],
            }

        def self_test_known() -> bool:
            result = handler({"text": "KIRA kira FORGE"})
            return result["words"] == 3 and result["unique_words"] == 2

        spec = ToolSpec(
            name="forge-text-statistics",
            version="0.1.0",
            capability=capability,
            description="Compute deterministic text statistics.",
            risk=Risk.LOW,
            permissions=("pure_compute",),
            deterministic=True,
        )
        return ToolCandidate(spec=spec, handler=handler, self_tests=(self_test_empty, self_test_known))
