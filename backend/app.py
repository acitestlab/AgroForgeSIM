# backend/app.py
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

import httpx
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
# --- replace the whole fetch_forecast_norm with this version ---
import datetime as _dt

OPENWEATHER_URL = "https://api.openweathermap.org/data/3.0/onecall"
OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"

# --- Import engine API models required by sim/tests ---
from engine.models import Feature, SurveyImportRequest, ScenarioRequest, SimulationResult  # type: ignore

# --- CROP_CATEGORIES is optional in engine.models; fallback to local if missing ---
try:
    from engine.models import CROP_CATEGORIES  # type: ignore
except Exception:
    CROP_CATEGORIES: Dict[str, List[str]] = {
        "Cereals": ["Maize", "Rice", "Sorghum"],
        "Root and Tuber Crops": ["Cassava", "Yams"],
        "Vegetables": [
            "Spinach", "Cucumber", "Broccoli", "Tomato", "Onion", "Okra",
            "Cabbage", "Pepper", "Amaranth",
        ],
        "Fruits": [
            "Mango", "Apple", "Orange", "Banana", "Pineapple",
            "Guava", "Papaya", "Lemon", "Grapes",
        ],
        "Legumes": ["Beans", "Cowpea", "Chickpea", "Lentils", "Fava Beans", "Mung Bean"],
    }

# --- Engine services you still use elsewhere ---
from engine.utils import health_status
from engine.sim import Simulator
from engine.harvest import HarvestPlanner

# ==============================
# Settings (from .env)
# ==============================
class Settings(BaseSettings):
    # API
    API_PREFIX: str = "/api"
    API_TITLE: str = "AgroForgeSIM API"
    API_VERSION: str = "1.0.0"
    API_CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Weather
    OPENWEATHER_API_KEY: str | None = None  # optional; fallback to Open-Meteo if not set/invalid

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        validate_default=True,
    )

settings = Settings()
_cors_origins = [o.strip() for o in settings.API_CORS_ORIGINS.split(",") if o.strip()]

# ==============================
# App, Router, Logger
# ==============================
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    docs_url=f"{settings.API_PREFIX}/docs",
    openapi_url=f"{settings.API_PREFIX}/openapi.json",
    description="AgroForgeSIM backend: crops, weather, simulation, and planning.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api = APIRouter(prefix=settings.API_PREFIX, tags=["AgroForgeSIM"])
alias = APIRouter(tags=["Compat"])  # no prefix (legacy paths)

logger = logging.getLogger("agroforge")
logging.basicConfig(level=logging.INFO)

# Services
simulator = Simulator()
harvest_planner = HarvestPlanner()

# ==============================
# Weather helpers (with fallback)
# ==============================
OPENWEATHER_URL = "https://api.openweathermap.org/data/3.0/onecall"
OPENMETEO_URL = "https://api.open-meteo.com/v1/forecast"

def _has_real_ow_key(key: str | None) -> bool:
    if not key:
        return False
    placeholder_markers = [
        "YOUR_OPENWEATHER_API_KEY",
        "YOUR_OPENWEATHER_API_KEY_HERE",
        "REPLACE_ME",
    ]
    low = key.strip().lower()
    return not any(m.lower() in low for m in placeholder_markers)

async def fetch_forecast_norm(lat: float, lon: float, hours: int) -> List[Dict[str, Any]]:
    """
    Return a list of daily dicts: [{date, tmin, tmax, rain, rad, et0}, ...]
    - Uses OpenWeather if a real key is present.
    - Otherwise uses Open-Meteo forecast (max 16 days). If horizon > 16 days,
      we extend by repeating the last forecast day so the simulator always
      gets the requested length.
    """
    days_requested = max(1, int(round(hours / 24))) if hours else 7
    days_requested = min(days_requested, 365)  # guard against absurd horizons
    ow_key = settings.OPENWEATHER_API_KEY or os.getenv("OPENWEATHER_API_KEY")

    async with httpx.AsyncClient(timeout=20) as client:
        # 1) Try OpenWeather first only if we have a real key
        if _has_real_ow_key(ow_key):
            try:
                r = await client.get(
                    OPENWEATHER_URL,
                    params={
                        "lat": lat,
                        "lon": lon,
                        "exclude": "minutely,hourly,alerts",
                        "units": "metric",
                        "appid": ow_key,
                    },
                )
                if r.status_code == 200:
                    j = r.json()
                    daily = j.get("daily") or []
                    out: List[Dict[str, Any]] = []
                    for d in daily[:days_requested]:
                        t = d.get("temp") or {}
                        out.append({
                            "date": d.get("dt"),  # epoch seconds
                            "tmin": t.get("min"),
                            "tmax": t.get("max"),
                            "rain": d.get("rain", 0.0) or 0.0,
                            "rad": None,   # not provided by One Call 3.0
                            "et0": None,   # not provided by One Call 3.0
                        })
                    if out:
                        # If OW returns fewer days than requested (rare), pad forward
                        while len(out) < days_requested:
                            last = out[-1].copy()
                            # if epoch, add 86400 seconds
                            if isinstance(last["date"], (int, float)):
                                last["date"] = int(last["date"]) + 86400
                            out.append(last)
                        return out
                # any non-200 falls through to Open-Meteo
            except Exception as e:
                logger.info("OpenWeather failed or not available: %s", e)

        # 2) Fallback: Open-Meteo forecast (max 16 days)
        try:
            days_for_api = min(days_requested, 16)  # <-- cap to 16
            r2 = await client.get(
                OPENMETEO_URL,
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": (
                        "temperature_2m_min,temperature_2m_max,"
                        "precipitation_sum,shortwave_radiation_sum,"
                        "et0_fao_evapotranspiration"
                    ),
                    "forecast_days": days_for_api,
                    "timezone": "auto",
                },
            )
            r2.raise_for_status()
            d = r2.json()
            daily = d.get("daily", {})
            dates = daily.get("time", []) or []
            tmin = daily.get("temperature_2m_min", []) or []
            tmax = daily.get("temperature_2m_max", []) or []
            rain = daily.get("precipitation_sum", []) or []
            rad  = daily.get("shortwave_radiation_sum", []) or []
            et0  = daily.get("et0_fao_evapotranspiration", []) or []

            out: List[Dict[str, Any]] = []
            for i, day in enumerate(dates[:days_for_api]):
                out.append({
                    "date": day,  # ISO date "YYYY-MM-DD"
                    "tmin": tmin[i] if i < len(tmin) else None,
                    "tmax": tmax[i] if i < len(tmax) else None,
                    "rain": rain[i] if i < len(rain) else 0.0,
                    "rad":  rad[i]  if i < len(rad)  else None,
                    "et0":  et0[i]  if i < len(et0)  else None,
                })

            # If horizon > 16d, extend by repeating the last day (deterministic filler)
            if out and len(out) < days_requested:
                def _parse_iso(s: str) -> _dt.date:
                    try:
                        return _dt.date.fromisoformat(str(s)[:10])
                    except Exception:
                        return _dt.date.today()

                last_date = _parse_iso(out[-1]["date"])
                last_vals = {k: out[-1][k] for k in ("tmin", "tmax", "rain", "rad", "et0")}
                needed = days_requested - len(out)
                for i in range(needed):
                    nd = last_date + _dt.timedelta(days=i + 1)
                    out.append({
                        "date": nd.isoformat(),
                        **last_vals,
                    })

            if not out:
                raise HTTPException(status_code=502, detail="No daily forecast from Open-Meteo")

            return out

        except httpx.HTTPError as e:
            # Surface a friendly status that allows frontends/tests to detect disabled weather.
            raise HTTPException(status_code=501, detail=f"Weather provider error: {e}") from e
# ==============================
# Local response models
# ==============================
class CropsOut(BaseModel):
    categories: Dict[str, List[str]]
    total: int
    total_crops: int
    supported_crop_categories: Dict[str, List[str]]


class SurveyImportIn(BaseModel):
    name: str
    type: str | None = None
    features: List[Feature] = Field(default_factory=list)

    def to_engine(self) -> SurveyImportRequest:
        allowed = {
            "dxf": "DXF",
            "kml": "KML",
            "geojson": "GeoJSON",
            "shapefile": "Shapefile",
            "csv": "CSV",
            "other": "Other",
        }
        raw = (self.type or "GeoJSON").strip().lower()
        mapped = allowed.get(raw, "Other")
        return SurveyImportRequest(name=self.name, type=mapped, features=self.features)


# ==============================
# Endpoints
# ==============================
@api.get("/health")
def health() -> Dict[str, Any]:
    """Basic liveness + unix time, used by probes and FE."""
    payload = health_status()
    payload.update({
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
    })
    return payload

@api.get("/crops", response_model=CropsOut)
def list_crops() -> CropsOut:
    cats = CROP_CATEGORIES
    return CropsOut(
        categories=cats,
        supported_crop_categories=cats,
        total=sum(len(v) for v in cats.values()),
        total_crops=sum(len(v) for v in cats.values()),
    )

@api.get("/weather/current")
async def current_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Keep a simple current endpoint; derive from normalized forecast[0]."""
    try:
        days = await fetch_forecast_norm(lat, lon, hours=24)
        d0 = days[0] if days else {}
        return {
            "avg_temp": None if d0.get("tmin") is None or d0.get("tmax") is None else round((d0["tmin"] + d0["tmax"]) / 2, 2),
            "precip": d0.get("rain"),
            "provider": "openweather" if _has_real_ow_key(settings.OPENWEATHER_API_KEY) else "open-meteo",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("weather/current failed")
        raise HTTPException(status_code=502, detail=str(e))

@api.get("/weather/forecast")
async def forecast_weather(lat: float, lon: float, hours: int = 48) -> List[Dict[str, Any]]:
    """Daily forecast normalized for the simulator."""
    try:
        return await fetch_forecast_norm(lat, lon, hours=hours)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("weather/forecast failed")
        raise HTTPException(status_code=502, detail=str(e))

@api.post("/simulate", response_model=SimulationResult)
async def simulate(req: ScenarioRequest) -> SimulationResult:
    """
    Run the simplified simulator.
      - Pull normalized forecast for (lat, lon, horizon_hours)
      - Convert to provider_payload structure expected by Simulator
    """
    try:
        daily_list = await fetch_forecast_norm(req.lat, req.lon, hours=req.horizon_hours)
        # Convert normalized list -> arrays for simulator
        daily = {
            "time": [d["date"] for d in daily_list],
            "temperature_2m_min": [d.get("tmin") for d in daily_list],
            "temperature_2m_max": [d.get("tmax") for d in daily_list],
            "precipitation_sum": [d.get("rain", 0.0) for d in daily_list],
            "shortwave_radiation_sum": [d.get("rad", 0.0) for d in daily_list],
            "et0": [d.get("et0") for d in daily_list],
        }
        provider_payload = {"daily": daily}
        return simulator.run(req, provider_payload)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("simulate failed")
        raise HTTPException(status_code=400, detail=str(e))

def _import_survey(payload: SurveyImportRequest, requested_type: str | None = None) -> Dict[str, Any]:
    return {
        "status": "ok",
        "name": payload.name,
        "type": (requested_type or payload.type).lower(),
        "features": [f.model_dump() for f in payload.features],
        "message": "Survey converter placeholder (DXF/KML→GeoJSON pending).",
    }


@api.post("/surveys/import")
async def import_survey(payload: SurveyImportIn) -> Dict[str, Any]:
    return _import_survey(payload.to_engine(), payload.type)


@api.post("/survey/import")
async def import_survey_singular(payload: SurveyImportIn) -> Dict[str, Any]:
    return _import_survey(payload.to_engine(), payload.type)

@api.post("/harvest/plan")
async def harvest_plan(req: ScenarioRequest) -> Dict[str, Any]:
    try:
        daily_list = await fetch_forecast_norm(req.lat, req.lon, hours=req.horizon_hours)
        plan = harvest_planner.plan(req, daily_list)
        return plan
    except Exception as e:
        logger.exception("harvest/plan failed")
        raise HTTPException(status_code=400, detail=str(e))

# --------- Legacy/compat alias routes (no /api prefix) ---------
@alias.get("/status")
def status_alias() -> Dict[str, Any]:
    """Compatibility wrapper for legacy `/status` health probe."""
    return health()


@alias.get("/crops")
def crops_alias() -> CropsOut:
    """Expose `/crops` without the `/api` prefix for older clients."""
    return list_crops()


@alias.get("/weather/current")
async def weather_current_alias(lat: float, lon: float):
    return await current_weather(lat=lat, lon=lon)


@alias.get("/weather/forecast")
async def weather_forecast_alias(lat: float, lon: float, hours: int = 48):
    return await forecast_weather(lat=lat, lon=lon, hours=hours)


@alias.post("/surveys/import")
async def surveys_import_alias(payload: SurveyImportIn) -> Dict[str, Any]:
    return await import_survey(payload)

# Mount the routers
app.include_router(api)
app.include_router(alias)

@app.get("/", tags=["System"])
def root() -> Dict[str, Any]:
    return {
        "service": settings.API_TITLE,
        "version": settings.API_VERSION,
        "docs": f"{settings.API_PREFIX}/docs",
        "endpoints": [
            f"{settings.API_PREFIX}/health",
            f"{settings.API_PREFIX}/crops",
            f"{settings.API_PREFIX}/weather/current",
            f"{settings.API_PREFIX}/weather/forecast",
            f"{settings.API_PREFIX}/simulate",
            f"{settings.API_PREFIX}/survey/import",
            f"{settings.API_PREFIX}/harvest/plan",
            "/weather/current",
            "/weather/forecast",
        ],
    }
