"""
🌱 AgroForgeSIM Engine
---------------------
Core agronomic simulation library powering AgroForgeSIM.

Provides:
- Crop growth and yield simulation
- Soil–water–nutrient balance modelling
- Weather data ingestion and conversion
- Harvest plan generation utilities

Modules exposed here form the public API used by:
- backend/app.py (FastAPI service)
- backend/cli.py (command-line runner)
- backend/tests/ (pytest integration)
"""

from __future__ import annotations

# Public re-exports
from .models import *
from .params import *
from .sim import run_field, run_multi_field
from .harvest import build_harvest_plan
from .weather import parse_weather_csv
from .utils import *

__all__ = [
    # Simulation
    "run_field",
    "run_multi_field",
    # Harvest
    "build_harvest_plan",
    # Weather
    "parse_weather_csv",
    # Core models & params
    *[name for name in globals().keys() if not name.startswith("_")],
]

__version__ = "4.0.0"
__author__ = "AgroForgeSIM Research Team"
__license__ = "MIT"

# Optional: lightweight import guard for missing dependencies
try:
    import pandas  # noqa: F401
except ImportError:
    import warnings
    warnings.warn("pandas not installed; some data utilities may be limited.", RuntimeWarning)
