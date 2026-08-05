from math import exp
from .models import Climate, Design, MissionConstraints, SimulationResult

def simulate_design(climate, design, constraints):
    climate.validate(); design.validate(); constraints.validate()
    dry = max(0.0, 1.0 - climate.relative_humidity)
    evap = 14.0 * dry * (1-exp(-design.evaporative_area_m2/1.8)) * (0.45+0.55*design.natural_convection_score)
    rad = climate.night_sky_delta_c * (1-exp(-design.radiative_area_m2/2.2)) * min(1.0, design.insulation_r_value/4.0) * 0.55
    storage = min(3.0, design.thermal_mass_kg*0.025) + min(6.0, design.phase_change_kg*0.75)
    raw = evap + rad + storage
    delta = 22.0 * (1-exp(-raw/22.0))
    internal = climate.ambient_c - delta
    uncertainty = 1.5 + 2.0*climate.relative_humidity + (0.5 if design.estimated_cost_usd < 20 else 0.0)
    checks = {
        'temperature': internal + uncertainty <= constraints.target_max_temperature_c + 1e-9,
        'delta': delta - uncertainty >= constraints.minimum_cooling_delta_c,
        'cost': design.estimated_cost_usd <= constraints.max_cost_usd,
        'manufacture': design.locally_manufacturable or not constraints.require_local_manufacture,
    }
    reasons=[]
    if not checks['temperature']: reasons.append('temperature target is not met under uncertainty')
    if not checks['delta']: reasons.append('minimum useful cooling delta is not met under uncertainty')
    if not checks['cost']: reasons.append('estimated cost exceeds mission budget')
    if not checks['manufacture']: reasons.append('design is not locally manufacturable')
    score = 100 + delta*2 - uncertainty*4 + (8 if design.locally_manufacturable else -15) - 30*len(reasons)
    return SimulationResult(
        design.name, round(internal,2), round(delta,2), round(uncertainty,2), 0.0,
        checks['temperature'], checks['delta'], checks['cost'], checks['manufacture'],
        reasons, round(score,2),
        ['steady-state proxy, not CFD','no active electrical cooling','uncertainty required before success']
    )
