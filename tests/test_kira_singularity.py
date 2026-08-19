from orpheus.kira_singularity import (
    AuditLedger,
    Gate0,
    Mission,
    Risk,
    SingularityEngine,
    ToolCandidate,
    ToolSpec,
)


def test_engine_detects_gap_forges_registers_and_reuses_tool():
    engine = SingularityEngine()
    mission = Mission(
        objective="Measure text",
        required_capability="text.statistics",
        payload={"text": "alpha beta alpha"},
    )

    first = engine.execute(mission)
    assert first.status == "SUCCESS"
    assert first.output["words"] == 3
    assert engine.registry.snapshot() == ("forge-text-statistics@0.1.0",)

    receipt_count = len(first.receipts)
    second = engine.execute(mission)
    assert second.status == "SUCCESS"
    assert len(second.receipts) == receipt_count + 2
    assert engine.ledger.verify_chain() is True


def test_gate0_rejects_unapproved_side_effect_permission():
    candidate = ToolCandidate(
        spec=ToolSpec(
            name="unsafe",
            version="1.0.0",
            capability="unsafe.demo",
            description="must be blocked",
            risk=Risk.MEDIUM,
            permissions=("shell_exec",),
        ),
        handler=lambda payload: payload,
        self_tests=(lambda: True,),
    )
    report = Gate0().evaluate(candidate)
    assert report.passed is False
    assert any(reason.startswith("forbidden_permissions:") for reason in report.reasons)


def test_unknown_capability_fails_closed():
    result = SingularityEngine().execute(
        Mission(objective="Do unknown work", required_capability="unknown.capability")
    )
    assert result.status == "NO_SAFE_TOOL"
    assert result.output is None


def test_audit_ledger_detects_valid_chain():
    ledger = AuditLedger()
    ledger.append("a", {"n": 1})
    ledger.append("b", {"n": 2})
    assert ledger.verify_chain() is True
