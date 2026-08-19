from __future__ import annotations

from dataclasses import replace

from .contracts import ToolCandidate, ToolState


class ToolRegistry:
    def __init__(self) -> None:
        self._by_capability: dict[str, ToolCandidate] = {}
        self._by_id: dict[str, ToolCandidate] = {}

    def has_capability(self, capability: str) -> bool:
        return capability in self._by_capability

    def get_for_capability(self, capability: str) -> ToolCandidate:
        return self._by_capability[capability]

    def register(self, candidate: ToolCandidate) -> ToolCandidate:
        registered = replace(candidate, state=ToolState.REGISTERED)
        self._by_capability[registered.spec.capability] = registered
        self._by_id[registered.spec.tool_id] = registered
        return registered

    def snapshot(self) -> tuple[str, ...]:
        return tuple(sorted(self._by_id))
