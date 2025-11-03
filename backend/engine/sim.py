# backend/engine/sim.py
from __future__ import annotations

import math
from datetime import datetime
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from .models import (
    # request/response + engine models
    SimulationResult,
    DayPoint,
    FieldState,
    FieldConfig,
    WeatherDay,
    DayResult,
    RunResult,
    StageParams,
    CropParams,
    SoilProfile,
    SoilLayer,
    Management,
    HarvestTask,
    HarvestPlanner,
    FarmLayout,
    ScenarioConfig,
    AgroForgeSimulation,
)
from .params import get_crop_defaults as _select_crop


# ============================================================
# Simulator wrapper used by FastAPI
# ============================================================

class Simulator:
    """
    Thin orchestrator used by FastAPI to run a single-field simulation.

    - Accepts a ScenarioRequest-like object (pydantic model in engine.models)
    - Accepts provider weather payload (dict) from WeatherService
    - Returns SimulationResult (pydantic) for the API layer
    """

    def run(self, req: Any, weather_payload: Dict[str, Any]) -> SimulationResult:
        # 1) Normalize weather payload → list[WeatherDay]
        weather_days = self._to_daily_weather(weather_payload)
        if not weather_days:
            raise ValueError("No weather data available for simulation horizon")

        # 2) Build a minimal FieldConfig (crop, soil, management)
        crop = _select_crop(req.crop)
        soil = SoilProfile(layers=[SoilLayer(depth_cm=60, fc=150, wp=40, ks=50)])
        mgmt = Management(
            plant_date=req.start_date,
            density_plants_m2=getattr(req, "density_plants_m2", 4.0),
            irrigation_mm_day=getattr(req, "irrigation_mm_day", 0.0),
        )
        field_cfg = FieldConfig(
            id="field-1",
            name=f"{req.crop} @ ({req.lat:.3f},{req.lon:.3f})",
            area_ha=float(getattr(req, "area_ha", 1.0)),
            soil=soil,
            crop=crop,
            management=mgmt,
        )

        # 3) Run and convert to SimulationResult
        run_res = run_field(field_cfg, weather_days)

        return SimulationResult(
            field_id=run_res.field_id,
            yield_t_ha=run_res.yield_t_ha,
            harvest_date=run_res.harvest_date,
            grade=run_res.grade,
            series=[
                DayPoint(
                    date=d.date,
                    stage=d.stage,
                    lai=d.lai,
                    biomass_dm_kg_ha=d.biomass_dm_kg_ha,
                    soil_water_mm=d.soil_water_mm,
                    stress_w=d.stress_w,
                    stress_n=d.stress_n,
                    n_stock_kg_ha=d.n_stock_kg_ha,
                    p_stock_kg_ha=d.p_stock_kg_ha,
                    k_stock_kg_ha=d.k_stock_kg_ha,
                    gdd_progress=d.gdd_progress,
                    gdd_target=d.gdd_target,
                    crop=d.crop,
                )
                for d in run_res.series
            ],
            summary={
                "area_ha": field_cfg.area_ha,
                "lat": getattr(req, "lat", None),
                "lon": getattr(req, "lon", None),
                "crop": req.crop,
                "start_date": req.start_date,
                "days": len(run_res.series),
            },
        )

    # -------------------------
    # Internals
    # -------------------------
    def _to_daily_weather(self, payload: Dict[str, Any]) -> List[WeatherDay]:
        """
        Accepts either 'daily' or 'hourly' structures from WeatherService.
        Produces a list[WeatherDay] for the simulator.
        """
        # Daily
        if "daily" in payload:
            d = payload["daily"]
            dates = d.get("time") or d.get("date") or []
            tmin = d.get("temperature_2m_min") or d.get("tmin") or [20.0] * len(dates)
            tmax = d.get("temperature_2m_max") or d.get("tmax") or [30.0] * len(dates)
            rain = (
                d.get("precipitation_sum")
                or d.get("rain_sum")
                or d.get("rain")
                or [0.0] * len(dates)
            )
            rad = (
                d.get("shortwave_radiation_sum")
                or d.get("radiation_sum")
                or [18.0] * len(dates)  # MJ/m²/day fallback
            )
            et0 = d.get("et0")  # may be None; fallback computed in step_day
            out: List[WeatherDay] = []
            for i, dt in enumerate(dates):
                out.append(
                    WeatherDay(
                        date=str(dt),
                        tmin=float(tmin[i]),
                        tmax=float(tmax[i]),
                        rain=float(rain[i]),
                        rad=float(rad[i]),
                        et0=float(et0[i]) if et0 else None,
                    )
                )
            return out

        # Hourly → aggregate to daily
        if "hourly" in payload:
            h = payload["hourly"]
            times = h.get("time") or h.get("datetime") or []
            temp = h.get("temperature_2m") or h.get("temperature") or []
            rain = h.get("precipitation") or h.get("rain") or []
            rad = h.get("shortwave_radiation") or h.get("radiation") or []

            bucket: Dict[str, Dict[str, float]] = defaultdict(
                lambda: {"tmin": 1e9, "tmax": -1e9, "rain": 0.0, "rad": 0.0, "count": 0.0}
            )
            for i, ts in enumerate(times):
                day = str(ts)[:10]  # 'YYYY-MM-DD'
                t = float(temp[i]) if i < len(temp) else 25.0
                r = float(rain[i]) if i < len(rain) else 0.0
                s = float(rad[i]) if i < len(rad) else 0.75

                b = bucket[day]
                b["tmin"] = min(b["tmin"], t)
                b["tmax"] = max(b["tmax"], t)
                b["rain"] += r
                b["rad"] += s
                b["count"] += 1.0

            out: List[WeatherDay] = []
            for day, vals in sorted(bucket.items()):
                # If radiation is per-hour W/m², keep a rough daily proxy
                daily_rad = (
                    (vals["rad"] / max(1.0, vals["count"])) * 24.0
                    if vals["count"] >= 6
                    else vals["rad"]
                )
                out.append(
                    WeatherDay(
                        date=day,
                        tmin=float(vals["tmin"]),
                        tmax=float(vals["tmax"]),
                        rain=float(vals["rain"]),
                        rad=float(daily_rad),
                        et0=None,  # compute fallback later
                    )
                )
            return out

        # Unknown provider format
        return []


# ============================================================
# Basic physiological utilities
# ============================================================

def gdd_day(tmin: float, tmax: float, tb: float) -> float:
    """Growing-degree day for a single day using simple average method."""
    return max(0.0, ((tmin + tmax) / 2.0) - tb)


def etc_from_kc(et0: float, kc: float) -> float:
    """Crop evapotranspiration (ETc) from reference ET0 and stage coefficient Kc."""
    return max(0.0, et0 * kc)


def crop_stage_prefix(current_stage_name: str, stages: List[StageParams]) -> List[StageParams]:
    """Return an ordered list of stages up to and including the current stage name."""
    out: List[StageParams] = []
    for s in stages:
        out.append(s)
        if s.name == current_stage_name:
            break
    return out


# ============================================================
# Stage, water & nutrient functions
# ============================================================

def _advance_stage(st: FieldState, crop: CropParams) -> None:
    stage = crop.stages[st.stage_index]
    cond = False
    if stage.gdd_target is not None:
        cond = st.gdd_accum >= stage.gdd_target
    elif stage.dap_target is not None:
        cond = st.dap >= stage.dap_target
    if cond and st.stage_index < len(crop.stages) - 1:
        st.stage_index += 1


def _water_balance(
    st: FieldState, soil: SoilProfile, inflow_mm: float, etc_pot: float
) -> Tuple[float, float]:
    """Bucket model: rainfall/irrigation inflow; transpiration & soil evaporation outflows."""
    runoff = max(0.0, inflow_mm - soil.runoff_threshold_mm) * 0.3
    st.soil_water_mm += (inflow_mm - runoff)
    st.soil_water_mm = min(st.soil_water_mm, soil.rootzone_capacity)

    transp_pot = etc_pot * min(1.0, st.lai / 3.0)
    transp_act = min(transp_pot, st.soil_water_mm)
    st.soil_water_mm -= transp_act

    soil_evap = max(0.0, etc_pot - transp_act) * (1.0 - min(1.0, st.lai / 3.0))
    soil_evap = min(soil_evap, st.soil_water_mm)
    st.soil_water_mm -= soil_evap

    st.stress_w = max(0.001, min(1.0, (transp_act + 1e-6) / (transp_pot + 1e-6)))
    return transp_act, soil_evap


def _nutrients(
    st: FieldState, stage: StageParams, crop: CropParams, daily_uptake_cap: float = 8.0
) -> None:
    """Simplified nutrient uptake tracking; sets nitrogen stress proxy."""
    # Track per-stage uptake by nutrient
    for key, target in stage.nuptake_target.items():
        stock = getattr(st, f"{key.lower()}_stock_kg_ha")
        taken_so_far = st.notes.get(f"{key}_taken_{stage.name}", 0.0)
        needed = max(0.0, target - taken_so_far)
        take = min(daily_uptake_cap, needed) * st.stress_w
        setattr(st, f"{key.lower()}_stock_kg_ha", stock + take)
        st.notes[f"{key}_taken_{stage.name}"] = taken_so_far + take

    # Nitrogen stress proxy across stages up to current
    demanded = sum(s.nuptake_target.get("N", 0.0) for s in crop_stage_prefix(stage.name, crop.stages))
    taken = sum(v for k, v in st.notes.items() if k.startswith("N_taken_"))
    ratio = min(1.0, (taken + 1e-6) / (demanded + 1e-6)) if demanded > 0 else 1.0
    st.stress_n = max(0.4, ratio)


# ============================================================
# Single-day step & single-field run
# ============================================================

def step_day(field: FieldConfig, st: FieldState, w: WeatherDay) -> FieldState:
    """Advance the field one day with weather forcing."""
    crop = field.crop
    stage = crop.stages[st.stage_index]

    st.date = w.date
    st.dap += 1
    st.gdd_accum += gdd_day(w.tmin, w.tmax, crop.tb)

    # ET0 from weather (fallback: simple Hargreaves-like)
    et0 = w.et0 if w.et0 is not None else max(2.0, 0.0023 * (w.tmax - w.tmin) * ((w.tmin + w.tmax) / 2.0) + 2.0)
    etc = etc_from_kc(et0, stage.kc)

    inflow = w.rain + (field.management.irrigation_mm_day or 0.0)

    _water_balance(st, field.soil, inflow, etc)
    _nutrients(st, stage, crop)

    # LAI logistic gain with stress factors
    lai_gain = stage.lai_gain * st.lai * (1.0 - st.lai / crop.lai_max) * st.stress_w * st.stress_n
    st.lai = min(crop.lai_max, st.lai + lai_gain)

    # Biomass accumulation from APAR (Beer-Lambert)
    apar = w.rad * (1.0 - math.exp(-0.65 * st.lai))
    dB = stage.rue * apar * st.stress_w * st.stress_n
    st.biomass_dm_kg_ha += dB

    _advance_stage(st, crop)
    return st


def run_field(field: FieldConfig, weather: List[WeatherDay]) -> RunResult:
    """Run a daily simulation for a single field over a weather series."""
    series: List[DayResult] = []
    st = FieldState(date=weather[0].date, soil_water_mm=min(120.0, field.soil.rootzone_capacity))

    for w in weather:
        st = step_day(field, st, w)
        maturity = min(
            1.0,
            (st.gdd_accum or 0.0) / (field.crop.stages[-1].gdd_target or st.gdd_accum or 1.0),
        )
        series.append(
            DayResult(
                date=w.date,
                stage=field.crop.stages[st.stage_index].name,
                lai=st.lai,
                biomass_dm_kg_ha=st.biomass_dm_kg_ha,
                soil_water_mm=st.soil_water_mm,
                stress_w=st.stress_w,
                stress_n=st.stress_n,
                n_stock_kg_ha=st.n_stock_kg_ha,
                p_stock_kg_ha=st.p_stock_kg_ha,
                k_stock_kg_ha=st.k_stock_kg_ha,
                gdd_progress=st.gdd_accum,
                gdd_target=field.crop.stages[-1].gdd_target,
                crop=field.crop.species,
            )
        )

    # Post-process yield & harvest date
    from .harvest import estimate_yield
    y, hdate, grade = estimate_yield(field, series)
    return RunResult(field_id=field.id, series=series, yield_t_ha=y, harvest_date=hdate, grade=grade)


# ============================================================
# Multi-field/farm run
# ============================================================

def run_multi_field(layout: FarmLayout, scenario: ScenarioConfig) -> AgroForgeSimulation:
    """
    Execute multi-field simulations for all field-type nodes in a scenario.
    Updates the layout’s zone colors from maturity & stress and builds a harvest plan.
    """
    results: Dict[str, RunResult] = {}
    planner = HarvestPlanner()
    field_cfgs: List[FieldConfig] = []

    for node in scenario.nodes:
        if node.type != "field":
            continue

        crop = _select_crop(node.params["crop"])
        soil = SoilProfile(
            layers=[
                # If a soil survey exists, replace these defaults per-zone
                SoilLayer(
                    depth_cm=int(node.params.get("soil_depth_cm", 60)),
                    fc=float(node.params.get("soil_fc", 150)),
                    wp=float(node.params.get("soil_wp", 40)),
                    ks=float(node.params.get("soil_ks", 50)),
                )
            ]
        )

        mgmt = Management(
            plant_date=node.params["plant_date"],
            density_plants_m2=float(node.params.get("density", 6.0)),
            irrigation_mm_day=float(node.params.get("irrigation", 0.0)),
        )

        field_cfg = FieldConfig(
            id=node.id,
            name=node.label,
            area_ha=float(node.params.get("area_ha", 1.0)),
            soil=soil,
            crop=crop,
            management=mgmt,
        )
        field_cfgs.append(field_cfg)

        res = run_field(field_cfg, scenario.weather)
        results[node.id] = res

        # Update layout visuals from latest state
        last = res.series[-1]
        maturity = min(1.0, (last.gdd_progress or 0.0) / (last.gdd_target or 1.0))
        water_stress = last.stress_w
        layout.update_zone_growth(field_cfg.id, maturity, water_stress)

        # Queue harvest task
        planner.add_task(
            HarvestTask(
                field_id=field_cfg.id,
                crop=field_cfg.crop.species,
                planned_date=res.harvest_date or str(datetime.now().date()),
                expected_yield_t_ha=res.yield_t_ha or 0.0,
                maturity_ratio=maturity,
            )
        )

    # Compose full simulation artifact
    sim = AgroForgeSimulation(
        scenario=scenario,
        fields=field_cfgs,   # ✅ FIX: pass FieldConfig list, not RunResult list
        layout=layout,
        planner=planner,
        timestamp=str(datetime.now()),
        notes="Multi-field AgroForgeSIM completed successfully.",
    )
    return sim
