from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable


class Risk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolState(str, Enum):
    PROPOSED = "proposed"
    VERIFIED = "verified"
    REGISTERED = "registered"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class Mission:
    objective: str
    required_capability: str
    payload: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Gap:
    capability: str
    reason: str


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    version: str
    capability: str
    description: str
    risk: Risk = Risk.LOW
    permissions: tuple[str, ...] = ()
    deterministic: bool = True

    @property
    def tool_id(self) -> str:
        return f"{self.name}@{self.version}"


@dataclass(slots=True)
class ToolCandidate:
    spec: ToolSpec
    handler: Callable[[dict[str, Any]], dict[str, Any]]
    self_tests: tuple[Callable[[], bool], ...] = ()
    state: ToolState = ToolState.PROPOSED


@dataclass(frozen=True, slots=True)
class GateReport:
    passed: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MissionResult:
    status: str
    capability: str
    tool_id: str | None
    output: dict[str, Any] | None
    receipts: tuple[dict[str, Any], ...]
