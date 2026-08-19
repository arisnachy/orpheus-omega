from __future__ import annotations

from .contracts import GateReport, Risk, ToolCandidate


class Gate0:
    """Fail-closed admission gate for newly synthesized tools.

    v0 intentionally allows only side-effect-free tools. Broader permissions can be
    added later as explicit capability classes with their own evaluators/sandboxes.
    """

    ALLOWED_PERMISSIONS = frozenset({"pure_compute"})

    def evaluate(self, candidate: ToolCandidate) -> GateReport:
        reasons: list[str] = []
        spec = candidate.spec

        if not spec.name.strip() or not spec.version.strip() or not spec.capability.strip():
            reasons.append("missing_identity")
        if spec.risk is Risk.HIGH:
            reasons.append("high_risk_not_admissible_in_v0")
        unknown = set(spec.permissions) - self.ALLOWED_PERMISSIONS
        if unknown:
            reasons.append(f"forbidden_permissions:{','.join(sorted(unknown))}")
        if not candidate.self_tests:
            reasons.append("missing_self_tests")
        else:
            for index, test in enumerate(candidate.self_tests):
                try:
                    if test() is not True:
                        reasons.append(f"self_test_{index}_failed")
                except Exception as exc:
                    reasons.append(f"self_test_{index}_error:{type(exc).__name__}")

        return GateReport(passed=not reasons, reasons=tuple(reasons))
