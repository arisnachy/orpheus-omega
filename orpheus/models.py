from dataclasses import dataclass, asdict, field

@dataclass(frozen=True)
class Climate:
    ambient_c: float
    relative_humidity: float
    night_sky_delta_c: float = 8.0
    def validate(self):
        if not -20 <= self.ambient_c <= 60: raise ValueError("ambient_c out of range")
        if not 0 <= self.relative_humidity <= 1: raise ValueError("relative_humidity must be 0..1")
        if not 0 <= self.night_sky_delta_c <= 25: raise ValueError("night_sky_delta_c must be 0..25")

@dataclass(frozen=True)
class Design:
    name: str
    evaporative_area_m2: float = 0.0
    radiative_area_m2: float = 0.0
    thermal_mass_kg: float = 0.0
    phase_change_kg: float = 0.0
    insulation_r_value: float = 1.0
    natural_convection_score: float = 0.5
    estimated_cost_usd: float = 0.0
    locally_manufacturable: bool = True
    def validate(self):
        for key, value in self.__dict__.items():
            if key not in {"name", "locally_manufacturable"} and value < 0:
                raise ValueError(f"{key} cannot be negative")
        if not 0 <= self.natural_convection_score <= 1:
            raise ValueError("natural_convection_score must be 0..1")

@dataclass(frozen=True)
class MissionConstraints:
    max_cost_usd: float
    target_max_temperature_c: float
    minimum_cooling_delta_c: float
    require_local_manufacture: bool = True
    def validate(self):
        if self.max_cost_usd <= 0: raise ValueError("max_cost_usd must be positive")
        if self.minimum_cooling_delta_c <= 0: raise ValueError("minimum_cooling_delta_c must be positive")

@dataclass
class SimulationResult:
    design_name: str
    estimated_internal_c: float
    cooling_delta_c: float
    uncertainty_c: float
    hourly_energy_kwh: float
    passes_temperature: bool
    passes_cooling_delta: bool
    passes_cost: bool
    passes_manufacture: bool
    rejected_reasons: list[str] = field(default_factory=list)
    score: float = 0.0
    assumptions: list[str] = field(default_factory=list)
    @property
    def accepted(self): return not self.rejected_reasons
    def to_dict(self):
        data = asdict(self); data['accepted'] = self.accepted; return data
