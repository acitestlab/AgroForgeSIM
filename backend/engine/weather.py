# backend/engine/weather.py
from __future__ import annotations

"""
☁️ AgroForgeSIM Weather Utilities & Service
==========================================
- File parsing: CSV → WeatherDay
- Live providers: Open-Meteo (default, no key) and OpenWeather (optional)
- Normalization: All forecasts returned as a list[dict] compatible with engine.models.WeatherDay
"""

import csv
import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from .models import WeatherDay

# -------------------------------
# CSV utilities (file-driven runs)
# -------------------------------

def parse_weather_csv(path: str) -> List[WeatherDay]:
    """
    Parse a weather CSV file into WeatherDay records.
    CSV Columns: date,tmin,tmax,rain,rad,et0
    """
    days: List[WeatherDay] = []
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                days.append(
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
                # Skip malformed rows but continue parsing
                print(f"⚠️ Skipping malformed row: {row} ({e})")
    return days


def estimate_et0(tmin: float, tmax: float, rad: float) -> float:
    """
    Simple Hargreaves-like ET0 estimation (placeholder).
    Assumes `rad` is MJ/m2/day. Calibrate for your region as needed.
    """
    try:
        dt = max(0.0, tmax - tmin)
        return 0.0023 * (dt ** 0.5) * rad
    except Exception:
        return 0.0


# ----------------------------------
# Live providers (normalized outputs)
# ----------------------------------

_DEFAULT_TIMEOUT = httpx.Timeout(20.0, connect=10.0)
_DEFAULT_HEADERS = {"User-Agent": "AgroForgeSIM/1.0 (+https://example.com)"}


class WeatherService:
    """
    Unified weather provider.

    provider:
      - "open-meteo" (default): no API key, robust daily params incl. ET0 (FAO)
      - "openweather": requires OPENWEATHER_API_KEY, uses One Call daily

    All `forecast()` returns a list[dict] shaped like WeatherDay:
      {"date": "YYYY-MM-DD", "tmin": float, "tmax": float,
       "rain": float, "rad": float, "et0": float}
    """
    def __init__(
        self,
        openweather_api_key: Optional[str] = None,
        open_meteo_base_url: Optional[str] = None,
        cache_hours: int = 6,
        **kwargs: Any,
    ) -> None:
        """
        WeatherService constructor compatible with app.py.

        Back-compat aliases for OpenWeather:
          - openweather_key, owm_api_key, api_key
        """
        # ---- alias support for older configs ----
        if not openweather_api_key:
            for alt in ("openweather_key", "owm_api_key", "api_key"):
                if alt in kwargs and kwargs[alt]:
                    openweather_api_key = kwargs[alt]
                    break

        # sensible defaults
        self.openweather_api_key = openweather_api_key
        self.api_key = openweather_api_key  # used by methods
        self.open_meteo_base_url = (
            open_meteo_base_url or "https://api.open-meteo.com/v1/forecast"
        )
        self.cache_hours = int(cache_hours)

        # Provider selection: if we have an OpenWeather key, use it; else Open-Meteo
        self.provider = "openweather" if self.openweather_api_key else "open-meteo"

        # simple in-memory cache; keep if you already had one
        if not hasattr(self, "_cache"):
            self._cache: Dict[str, Any] = {}

    # ---------- public API ----------

    async def current(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Current surface conditions (normalized):
          {"temp_c": float, "humidity": float, "windspeed": float, "provider": str, "ts": iso}
        """
        if self.provider == "openweather" and self.api_key:
            url = (
                "https://api.openweathermap.org/data/2.5/weather"
                f"?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            )
            data = await _get_json(url)
            return {
                "temp_c": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "windspeed": data["wind"].get("speed", 0.0),
                "provider": "openweather",
                "ts": _iso_now(),
            }

        # Open-Meteo (default)
        url = (
            f"{self.open_meteo_base_url}"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        )
        data = await _get_json(url)
        cur = data.get("current", {})
        return {
            "temp_c": cur.get("temperature_2m"),
            "humidity": cur.get("relative_humidity_2m"),
            "windspeed": cur.get("wind_speed_10m"),
            "provider": "open-meteo",
            "ts": cur.get("time") or _iso_now(),
        }

    async def forecast(self, lat: float, lon: float, hours: int = 48) -> List[Dict[str, Any]]:
        """
        Return a list of day dictionaries compatible with WeatherDay.
        Uses daily aggregation to drive the simulation engine.
        """
        days = max(1, math.ceil(max(1, hours) / 24))

        if self.provider == "openweather" and self.api_key:
            # One Call daily (v3); some fields (rad) are not provided -> set rad=0, ET0 estimated
            url = (
                "https://api.openweathermap.org/data/3.0/onecall"
                f"?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={self.api_key}"
            )
            data = await _get_json(url)
            out: List[Dict[str, Any]] = []
            for d in data.get("daily", [])[:days]:
                dt = datetime.fromtimestamp(d["dt"], tz=timezone.utc).date().isoformat()
                tmin = float(d["temp"]["min"])
                tmax = float(d["temp"]["max"])
                rain = float(d.get("rain", 0.0))
                rad = 0.0  # OpenWeather daily lacks shortwave radiation
                et0 = estimate_et0(tmin, tmax, rad)
                out.append({"date": dt, "tmin": tmin, "tmax": tmax, "rain": rain, "rad": rad, "et0": et0})
            return out

        # Open-Meteo daily (preferred): includes temp min/max, precip sum, shortwave radiation, and ET0 FAO
        url = (
            f"{self.open_meteo_base_url}"
            f"?latitude={lat}&longitude={lon}"
            "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,shortwave_radiation_sum,et0_fao_evapotranspiration"
            f"&forecast_days={days}"
        )
        data = await _get_json(url)
        daily = data.get("daily", {})
        times = daily.get("time", []) or []
        tmin = daily.get("temperature_2m_min", []) or []
        tmax = daily.get("temperature_2m_max", []) or []
        rain = daily.get("precipitation_sum", []) or []
        rad = daily.get("shortwave_radiation_sum", []) or []
        et0 = daily.get("et0_fao_evapotranspiration", []) or []

        out: List[Dict[str, Any]] = []
        for i, day in enumerate(times[:days]):
            _tmin = float(tmin[i]) if i < len(tmin) else None
            _tmax = float(tmax[i]) if i < len(tmax) else None
            _rain = float(rain[i]) if i < len(rain) else 0.0
            _rad = float(rad[i]) if i < len(rad) else 0.0
            _et0 = float(et0[i]) if i < len(et0) else estimate_et0(_tmin or 0.0, _tmax or 0.0, _rad)
            out.append({"date": day, "tmin": _tmin, "tmax": _tmax, "rain": _rain, "rad": _rad, "et0": _et0})
        return out


# ---------------
# HTTP utilities
# ---------------

async def _get_json(url: str) -> Dict[str, Any]:
    """
    GET JSON with basic retries, timeouts and headers.
    """
    last_err: Optional[Exception] = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=_DEFAULT_TIMEOUT, headers=_DEFAULT_HEADERS) as client:
                r = await client.get(url)
                r.raise_for_status()
                return r.json()
        except Exception as e:
            last_err = e
    # Surface last error with context
    raise RuntimeError(f"Weather request failed after retries: {url} :: {last_err}")


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
