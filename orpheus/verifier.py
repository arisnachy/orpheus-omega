from dataclasses import dataclass

@dataclass(frozen=True)
class Verification:
    approved: bool
    checks: dict[str, bool]
    message: str

def verify_result(result):
    checks = {
        'temperature': result.passes_temperature,
        'cooling_delta': result.passes_cooling_delta,
        'cost': result.passes_cost,
        'manufacture': result.passes_manufacture,
        'uncertainty_reported': result.uncertainty_c > 0,
        'no_external_energy': result.hourly_energy_kwh == 0,
        'no_hidden_rejections': len(result.rejected_reasons) == 0,
    }
    approved = all(checks.values())
    return Verification(approved, checks, 'MISSION VERIFIED' if approved else 'MISSION REJECTED')
