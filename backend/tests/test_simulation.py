"""
🧪 AgroForgeSIM Engine – Simulation Tests

Validates the core daily simulation loop with deterministic, offline inputs.
- Uses run_field(...) with proper FieldConfig and WeatherDay series
- Ensures yields are computed and series length matches input
- Checks a basic agronomic effect (irrigation vs. rainfed) on a dry spell
"""

from backend.engine.sim import run_field
from backend.engine.models import (
    SoilLayer,
    SoilProfile,
    Management,
    FieldConfig,
    WeatherDay,
)
from backend.engine.params import get_crop_defaults


def _synthetic_weather(days: int = 10):
    """Create a short, plausible daily weather series."""
    out = []
    for i in range(days):
        # Mildly varying temps; light rainfall every 3rd day; reasonable radiation and ET0
        out.append(
            WeatherDay(
                date=f"2025-03-{i+1:02d}",
                tmin=19.0 + (i % 3) * 0.5,
                tmax=30.0 + (i % 4) * 0.6,
                rain=2.0 if i % 3 == 0 else 0.0,
                rad=18.0 - (i % 2) * 0.6,
                et0=4.0 + (i % 2) * 0.2,
            )
        )
    return out


def test_run_field_maize_basic():
    """Runs a 10-day maize simulation and checks core outputs are sensible."""
    crop = get_crop_defaults("maize")
    soil = SoilProfile(layers=[SoilLayer(depth_cm=60, fc=150, wp=40, ks=50)])
    mgmt = Management(plant_date="2025-03-01", density_plants_m2=6.0, irrigation_mm_day=0.0)
    field = FieldConfig(id="F1", name="Demo Plot", area_ha=2.0, soil=soil, crop=crop, management=mgmt)

    weather = _synthetic_weather(10)
    result = run_field(field, weather)

    assert result.field_id == "F1"
    assert len(result.series) == 10
    # Yield can be small for short runs, but should be computed (non-negative)
    assert result.yield_t_ha is not None
    assert result.yield_t_ha >= 0.0
    # Harvest date should be populated (last or maturity day)
    assert isinstance(result.harvest_date, str) and len(result.harvest_date) >= 10


def test_irrigation_effect_on_dry_spell():
    """
    On a dry sequence, adding irrigation should not reduce yield.
    This is a coarse check to ensure water stress handling is wired.
    """
    crop = get_crop_defaults("maize")
    soil = SoilProfile(layers=[SoilLayer(depth_cm=60, fc=150, wp=40, ks=50)])

    # Very dry 10 days
    dry_weather = [
        WeatherDay(date=f"2025-04-{i+1:02d}", tmin=20.0, tmax=31.0, rain=0.0, rad=18.0, et0=4.2)
        for i in range(10)
    ]

    # Rainfed
    mgmt_dry = Management(plant_date="2025-04-01", density_plants_m2=6.0, irrigation_mm_day=0.0)
    field_dry = FieldConfig(id="F2", name="Dry Plot", area_ha=1.0, soil=soil, crop=crop, management=mgmt_dry)
    res_dry = run_field(field_dry, dry_weather)

    # Irrigated
    mgmt_irrig = Management(plant_date="2025-04-01", density_plants_m2=6.0, irrigation_mm_day=3.0)
    field_irrig = FieldConfig(id="F3", name="Irrigated Plot", area_ha=1.0, soil=soil, crop=crop, management=mgmt_irrig)
    res_irrig = run_field(field_irrig, dry_weather)

    assert res_dry.yield_t_ha is not None and res_irrig.yield_t_ha is not None
    assert res_irrig.yield_t_ha >= res_dry.yield_t_ha
