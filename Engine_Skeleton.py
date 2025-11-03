from dataclasses import dataclass
import math, random
from typing import Dict, List

@dataclass
class CropParams:
    tb: float; lai_max: float; rue: float; hi: float
    gdd: Dict[str,int]; kc: Dict[str,float]
    stress_sens: Dict[str,float]

@dataclass
class FieldState:
    lai: float = 0.1
    biomass: float = 0.0
    gdd_accum: float = 0.0
    soil_water: float = 150.0  # mm in root zone
    stage: str = "pre_emerg"
    stress_w: float = 1.0
    stress_n: float = 1.0

def gdd(tmin, tmax, tb): return max(0.0, ((tmin+tmax)/2.0) - tb)

def kc_for_stage(stage, kc):
    return {"ini": kc["ini"], "veg": (kc["ini"]+kc["mid"])/2,
            "mid": kc["mid"], "end": kc["end"]}.get(stage, kc["ini"])

def step_day(crop: CropParams, st: FieldState, weather, et0):
    # Phenology
    st.gdd_accum += gdd(weather["tmin"], weather["tmax"], crop.tb)
    if st.gdd_accum < crop.gdd["emerg"]: st.stage = "ini"
    elif st.gdd_accum < crop.gdd["flower"]: st.stage = "veg"
    elif st.gdd_accum < crop.gdd["maturity"]: st.stage = "mid"
    else: st.stage = "end"

    # ET and water balance (simple)
    kc = kc_for_stage(st.stage, crop.kc)
    etc_pot = kc * et0
    transp_pot = min(etc_pot, max(0, st.lai/ crop.lai_max)*etc_pot)
    inflow = weather["rain"] + weather.get("irrig",0)
    runoff = max(0.0, inflow - 20.0) * 0.3
    st.soil_water += (inflow - runoff)
    transp_act = min(transp_pot, st.soil_water)
    st.soil_water -= transp_act
    soil_evap = max(0.0, etc_pot - transp_act) * (1.0 - min(1.0, st.lai/3.0))
    st.soil_water -= soil_evap
    st.soil_water = max(0.0, st.soil_water)

    st.stress_w = 0.001 + transp_act / (transp_pot + 1e-6)
    st.stress_w = max(0.0, min(1.0, st.stress_w))

    # LAI and biomass
    dLAI = 0.15 * st.lai * (1 - st.lai/crop.lai_max) * st.stress_w
    st.lai = min(crop.lai_max, st.lai + dLAI)

    # Radiation use (approx: MJ/m2/day from weather["rad"])
    apar = weather["rad"] * (1 - math.exp(-0.65 * st.lai))
    dB = crop.rue * apar * st.stress_w
    st.biomass += dB

    return st

def estimate_yield(crop: CropParams, st: FieldState, stress_hist):
    hi_penalty = 1.0 - crop.stress_sens["flower_water"]*(1-stress_hist.get("flower_min",1.0))
    hi = max(0.3, crop.hi * hi_penalty)
    yield_t_ha = (st.biomass * hi) / 1000.0  # assuming biomass kg/ha to t/ha
    return yield_t_ha
