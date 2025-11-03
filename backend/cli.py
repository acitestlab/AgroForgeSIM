"""
🌾 AgroForgeSIM Command Line Interface
-------------------------------------
Run simulations from the terminal without the web UI.

Usage examples:
  # Full scenario from YAML (writes JSON result)
  python backend/cli.py simulate backend/examples/scenario_maize.yaml --out run_output.json

  # Full scenario from JSON
  python backend/cli.py simulate backend/examples/scenario_maize.json

  # Use live weather instead of CSV/inline (requires engine.weather + coords)
  python backend/cli.py simulate backend/examples/scenario_maize.yaml --live-weather --lat 6.95 --lon 3.13 --hours 168

  # Quick synthetic test for a crop
  python backend/cli.py quick --crop maize
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import typer
import yaml

from engine.models import SoilLayer, SoilProfile, Management, FieldConfig, WeatherDay
from engine.params import crop_categories  # for validation
from engine.sim import run_field

# Optional live weather provider; CLI remains usable without it
try:
    from engine.weather import WeatherService  # type: ignore
except Exception:  # pragma: no cover - optional dependency at runtime
    WeatherService = None  # type: ignore

app = typer.Typer(help="🌾 AgroForgeSIM Command Line Tools", no_args_is_help=True)


# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------
def _fail(msg: str, code: int = 1) -> None:
    typer.secho(f"❌ {msg}", fg=typer.colors.RED, err=True)
    raise typer.Exit(code=code)


def _load_scenario(scenario_path: Path) -> Dict[str, Any]:
    if not scenario_path.exists():
        _fail(f"File not found: {scenario_path}")
    try:
        if scenario_path.suffix.lower() in {".yml", ".yaml"}:
            return yaml.safe_load(scenario_path.read_text(encoding="utf-8"))
        return json.loads(scenario_path.read_text(encoding="utf-8"))
    except Exception as e:
        _fail(f"Failed to parse scenario file: {e}")
    return {}  # unreachable


def _validate_crop(crop: str) -> str:
    crop_l = crop.lower().strip()
    all_supported = {c.lower() for names in crop_categories.values() for c in names}
    if crop_l not in all_supported:
        _fail(
            f"Unsupported crop '{crop}'. Supported examples include: "
            f"{', '.join(sorted(list(all_supported))[:12])}..."
        )
    return crop_l


def _read_weather_csv(path: Path) -> List[WeatherDay]:
    if not path.exists():
        _fail(f"Weather CSV not found: {path}")
    rows: List[WeatherDay] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(
                    WeatherDay(
                        date=row["date"],
                        tmin=float(row["tmin"]),
                        tmax=float(row["tmax"]),
                        rain=float(row["rain"]),
                        rad=float(row["rad"]),
                        et0=float(row.get("et0") or 0),
                    )
                )
    except Exception as e:
        _fail(f"Failed to read weather CSV: {e}")
    return rows


def _read_weather_inline(seq: List[Dict[str, Any]]) -> List[WeatherDay]:
    try:
        return [WeatherDay(**w) for w in seq]
    except Exception as e:
        _fail(f"Invalid inline weather entries: {e}")
    return []  # unreachable


# ------------------------------------------------------------
# Commands
# ------------------------------------------------------------
@app.command()
def simulate(
    scenario: str = typer.Argument(..., help="Path to scenario YAML/JSON"),
    out: str = typer.Option("run_output.json", "--out", "-o", help="Where to write JSON result"),
    live_weather: bool = typer.Option(False, "--live-weather", help="Use live weather instead of file/inline"),
    lat: Optional[float] = typer.Option(None, help="Latitude (required for --live-weather)"),
    lon: Optional[float] = typer.Option(None, help="Longitude (required for --live-weather)"),
    hours: int = typer.Option(168, help="Forecast horizon in hours for --live-weather"),
) -> None:
    """
    Run a full simulation from a scenario file.

    Scenario schema (YAML/JSON):
      field:
        id: F1
        name: Demo Plot
        area_ha: 2.0
        crop: maize
        plant_date: 2025-03-01
        density_plants_m2: 6.0
        irrigation_mm_day: 0.0
      soil_rootzone_capacity_mm: 150
      weather_csv: backend/examples/weather_sample.csv
      # or:
      # weather: [{date: YYYY-MM-DD, tmin: .., tmax: .., rain: .., rad: .., et0: ..}, ...]
    """
    path = Path(scenario)
    cfg = _load_scenario(path)

    # Field configuration
    if "field" not in cfg:
        _fail("Scenario missing 'field' section")
    f = cfg["field"]
    crop_name = _validate_crop(f["crop"])

    soil = SoilProfile(layers=[SoilLayer(depth_cm=60, fc=cfg.get("soil_rootzone_capacity_mm", 150), wp=40, ks=50)])
    mgmt = Management(
        plant_date=f["plant_date"],
        density_plants_m2=float(f.get("density_plants_m2", 6.0)),
        irrigation_mm_day=float(f.get("irrigation_mm_day", 0.0)),
    )
    field_cfg = FieldConfig(
        id=f["id"],
        name=f["name"],
        area_ha=float(f["area_ha"]),
        soil=soil,
        crop=crop_name,
        management=mgmt,
    )

    # Weather
    weather_days: List[WeatherDay]
    if live_weather:
        if WeatherService is None:
            _fail("Live weather requested but engine.weather is not available in this build.")
        if lat is None or lon is None:
            _fail("--live-weather requires --lat and --lon")
        try:
            ws = WeatherService()  # type: ignore
            series = typer.run(lambda: ws.forecast(lat, lon, hours))  # run coroutine safely
        except Exception as e:
            _fail(f"Live weather fetch failed: {e}")
        weather_days = _read_weather_inline(series)
    else:
        if "weather_csv" in cfg:
            weather_days = _read_weather_csv(Path(cfg["weather_csv"]))
        elif "weather" in cfg:
            weather_days = _read_weather_inline(cfg["weather"])
        else:
            _fail("No weather provided. Add 'weather_csv' or 'weather' to the scenario, or use --live-weather.")

    # Run simulation
    typer.secho(f"🚀 Running simulation for {field_cfg.crop} ({field_cfg.name})...", fg=typer.colors.CYAN)
    result = run_field(field_cfg, weather_days)

    # Prepare output
    payload = {
        "field_id": result.field_id,
        "crop": field_cfg.crop,
        "yield_t_ha": result.yield_t_ha,
        "harvest_date": result.harvest_date,
        "grade": result.grade,
        "series": [d.__dict__ for d in result.series],
    }

    # Write
    out_path = Path(out)
    try:
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    except Exception as e:
        _fail(f"Failed to write output: {e}")

    typer.secho(f"✅ Simulation complete → {out_path}", fg=typer.colors.GREEN)
    typer.secho(f"📊 Yield: {result.yield_t_ha:.2f} t/ha | Harvest: {result.harvest_date}", fg=typer.colors.GREEN)


@app.command()
def quick(
    crop: str = typer.Option("maize", "--crop", "-c", help="Crop name (e.g., maize, cassava, tomato)"),
) -> None:
    """
    Run a quick synthetic 10-day test (no files).
    """
    crop_name = _validate_crop(crop)
    soil = SoilProfile(layers=[SoilLayer(depth_cm=60, fc=150, wp=40, ks=50)])
    mgmt = Management(plant_date="2025-01-01", density_plants_m2=6.0)
    field = FieldConfig(id="Test", name="CLI Demo Field", area_ha=1.0, soil=soil, crop=crop_name, management=mgmt)

    # synthetic weather
    weather = [WeatherDay(date=f"2025-01-{i+1:02d}", tmin=15, tmax=28, rain=2, rad=18, et0=4) for i in range(10)]
    result = run_field(field, weather)

    typer.secho(f"✅ Quick simulation: {result.yield_t_ha:.2f} t/ha | Harvest: {result.harvest_date} | Grade: {result.grade}",
                fg=typer.colors.GREEN)


# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------
if __name__ == "__main__":
    app()
