"""
🧠 AgroForgeSIM Utility Functions
---------------------------------
Reusable helpers for health/status, filesystem safety, numeric operations,
time-series convenience, and UI color mapping for growth & stress.

Used by:
- backend/app.py (health endpoint, logs)
- engine modules (sim/harvest/weather)
- CLI and potential preprocessing scripts
"""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Any


__all__ = [
    "health_status",
    "clamp",
    "safe_float",
    "ensure_dir",
    "color_from_growth",
    "timestamp",
    "lerp",
]


# -----------------------------
# Health / Time helpers
# -----------------------------
def health_status() -> dict[str, Any]:
    """
    Return a lightweight health payload used by /api/health and Docker healthchecks.
    Includes both human timestamp and epoch for machine checks.
    """
    now = time.time()
    return {
        "status": "ok",
        "time_epoch": int(now),
        "time_iso": datetime.utcfromtimestamp(now).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def timestamp() -> str:
    """Filesystem-friendly timestamp string, e.g. '2025-10-10_08-45-12'."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# -----------------------------
# Filesystem helpers
# -----------------------------
def ensure_dir(path: str) -> None:
    """Ensure a directory exists (no-op if it already does)."""
    os.makedirs(path, exist_ok=True)


# -----------------------------
# Numeric / parsing helpers
# -----------------------------
def clamp(v: float, lo: float, hi: float) -> float:
    """Clamp value v to the inclusive range [lo, hi]."""
    return max(lo, min(v, hi))


def lerp(a: float, b: float, t: float) -> float:
    """
    Linear interpolation between a and b given t in [0, 1].
    Values of t outside [0, 1] are clamped.
    """
    t_c = clamp(t, 0.0, 1.0)
    return a + (b - a) * t_c


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert to float safely, returning default on failure."""
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


# -----------------------------
# UI color helpers
# -----------------------------
def color_from_growth(maturity: float, stress: float = 1.0) -> str:
    """
    Generate a hex color representing crop health & maturity for the canvas.

    - If water/nutrient stress is low (stress < 0.6): brown
    - Else choose by maturity:
        < 0.3  -> green
        < 0.7  -> yellow
        >= 0.7 -> red
    """
    m = clamp(maturity, 0.0, 1.0)
    s = clamp(stress, 0.0, 1.0)

    if s < 0.6:
        return "#8b4513"  # brown (stressed)
    if m < 0.3:
        return "#4caf50"  # green
    if m < 0.7:
        return "#fbc02d"  # yellow
    return "#e53935"      # red
