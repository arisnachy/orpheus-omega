from __future__ import annotations

from .audit import AuditLedger
from .contracts import Gap, Mission, MissionResult, ToolState
from .gate0 import Gate0
from .registry import ToolRegistry
from .synthesizer import BuiltinSynthesizer, SynthesisError


class SingularityEngine:
    """MISSION -> GAP -> INVENT -> TEST -> VERIFY -> REGISTER -> USE."""

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        gate: Gate0 | None = None,
        synthesizer: BuiltinSynthesizer | None = None,
        ledger: AuditLedger | None = None,
    ) -> None:
        self.registry = registry or ToolRegistry()
        self.gate = gate or Gate0()
        self.synthesizer = synthesizer or BuiltinSynthesizer()
        self.ledger = ledger or AuditLedger()

    def detect_gap(self, mission: Mission) -> Gap | None:
        if self.registry.has_capability(mission.required_capability):
            return None
        return Gap(
            capability=mission.required_capability,
            reason="required capability is absent from the verified registry",
        )

    def execute(self, mission: Mission) -> MissionResult:
        self.ledger.append(
            "mission.received",
            {"objective": mission.objective, "capability": mission.required_capability},
        )

        gap = self.detect_gap(mission)
        if gap is not None:
            self.ledger.append("gap.detected", {"capability": gap.capability, "reason": gap.reason})
            try:
                candidate = self.synthesizer.synthesize(gap.capability)
            except SynthesisError as exc:
                self.ledger.append("forge.unavailable", {"capability": gap.capability, "reason": str(exc)})
                return self._result("NO_SAFE_TOOL", mission.required_capability, None, None)

            self.ledger.append("tool.invented", {"tool_id": candidate.spec.tool_id})
            report = self.gate.evaluate(candidate)
            self.ledger.append(
                "gate0.evaluated",
                {"tool_id": candidate.spec.tool_id, "passed": report.passed, "reasons": list(report.reasons)},
            )
            if not report.passed:
                candidate.state = ToolState.REJECTED
                return self._result("GATE0_REJECTED", mission.required_capability, candidate.spec.tool_id, None)

            candidate.state = ToolState.VERIFIED
            registered = self.registry.register(candidate)
            self.ledger.append("tool.registered", {"tool_id": registered.spec.tool_id})

        tool = self.registry.get_for_capability(mission.required_capability)
        output = tool.handler(mission.payload)
        self.ledger.append("tool.used", {"tool_id": tool.spec.tool_id})
        return self._result("SUCCESS", mission.required_capability, tool.spec.tool_id, output)

    def _result(
        self,
        status: str,
        capability: str,
        tool_id: str | None,
        output: dict[str, object] | None,
    ) -> MissionResult:
        return MissionResult(
            status=status,
            capability=capability,
            tool_id=tool_id,
            output=output,
            receipts=self.ledger.export(),
        )
