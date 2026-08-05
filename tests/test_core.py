import unittest
from orpheus.models import Climate, Design, MissionConstraints
from orpheus.simulator import simulate_design
from orpheus.verifier import verify_result
from orpheus.pipeline import evaluate_mission

class CoreTests(unittest.TestCase):
 def setUp(self): self.c=MissionConstraints(65,24,7)
 def test_humidity_hurts_evaporation(self):
  d=Design('evap',evaporative_area_m2=2,thermal_mass_kg=10,estimated_cost_usd=20)
  dry=simulate_design(Climate(34,.25),d,self.c); humid=simulate_design(Climate(34,.9),d,self.c)
  self.assertGreater(dry.cooling_delta_c,humid.cooling_delta_c)
 def test_over_budget_rejected(self):
  r=simulate_design(Climate(34,.4),Design('expensive',phase_change_kg=12,estimated_cost_usd=300,locally_manufacturable=False),self.c)
  self.assertFalse(verify_result(r).approved); self.assertIn('estimated cost exceeds mission budget',r.rejected_reasons)
 def test_weak_design_rejected(self):
  r=simulate_design(Climate(34,.95),Design('weak',evaporative_area_m2=.2,estimated_cost_usd=10),self.c)
  self.assertFalse(verify_result(r).approved)
 def test_hybrid_can_win(self):
  m=evaluate_mission(Climate(34,.45,9),[
   Design('weak',evaporative_area_m2=.2,estimated_cost_usd=10),
   Design('hybrid',evaporative_area_m2=4.1,radiative_area_m2=6.0,thermal_mass_kg=30,phase_change_kg=8.0,insulation_r_value=4.0,natural_convection_score=1.0,estimated_cost_usd=64)
  ],self.c)
  self.assertEqual('CUMPLIDA',m['mission_status']); self.assertEqual('hybrid',m['winner']['design'])
 def test_requires_candidate(self):
  with self.assertRaises(ValueError): evaluate_mission(Climate(30,.5),[],self.c)
