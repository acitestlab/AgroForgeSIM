# backend/engine/models.py

"""
🌱 AgroForgeSIM Engine Models
-----------------------------
Core dataclasses defining crops, soils, weather, management,
field configurations, simulation outputs, and harvest planning
for the AgroForgeSIM engine.

These are consumed by:
- engine.sim / engine.harvest / engine.weather modules
- backend.app (FastAPI endpoints)
- backend.cli (command-line runner)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple, Literal, Union, Any
from datetime import date

# NEW: Pydantic request/response models for FastAPI endpoints
from pydantic import BaseModel, Field

# ============================================================
# Shared constants (mirrors fallback in app.py)
# ============================================================

CROP_CATEGORIES: Dict[str, List[str]] = {
    "Cereals": ["Maize", "Rice", "Sorghum"],
    "Root and Tuber Crops": ["Cassava", "Yams"],
    "Vegetables": [
        "Spinach",
        "Cucumber",
        "Broccoli",
        "Tomato",
        "Onion",
        "Okra",
        "Cabbage",
        "Pepper",
        "Amaranth",
    ],
    "Fruits": [
        "Mango",
        "Apple",
        "Orange",
        "Banana",
        "Pineapple",
        "Guava",
        "Papaya",
        "Lemon",
        "Grapes",
    ],
    "Legumes": [
        "Beans",
        "Cowpea",
        "Chickpea",
        "Lentils",
        "Fava Beans",
        "Mung Bean",
    ],
}

# ============================================================
# 🌾 Crop and Growth Parameters (dataclasses)
# ============================================================

@dataclass
class StageParams:
    """Growth-stage parameterization (thermal time, LAI, partitioning)."""
    name: str
    gdd_target: Optional[float] = None
    dap_target: Optional[int] = None
    kc: float = 1.0
    rue: float = 1.5
    lai_gain: float = 0.12
    partition: Dict[str, float] = field(default_factory=dict)
    nuptake_target: Dict[str, float] = field(default_factory=dict)


@dataclass
class CropParams:
    """Crop-specific physiological constants."""
    species: str
    cultivar: str
    tb: float                   # base temperature (°C)
    to: float                   # optimum temperature (°C)
    lai_max: float
    hi: float                   # harvest index
    stages: List[StageParams]
    stress_sensitivity: Dict[str, float]


# ============================================================
# 🌍 Soil and Management (dataclasses)
# ============================================================

@dataclass
class SoilLayer:
    """Single soil layer with physical properties."""
    depth_cm: int
    fc: float                    # field capacity (mm)
    wp: float                    # wilting point (mm)
    ks: float                    # saturated conductivity (mm/day)
    om_pct: float = 1.5
    ph: float = 6.5


@dataclass
class SoilProfile:
    """Soil profile composed of multiple layers."""
    layers: List[SoilLayer]
    runoff_threshold_mm: float = 20.0

    @property
    def rootzone_capacity(self) -> float:
        """Total available water capacity (mm)."""
        return sum(max(0.0, ly.fc) for ly in self.layers)


@dataclass
class Management:
    """Agronomic management configuration."""
    plant_date: str
    density_plants_m2: float
    irrigation_mm_day: float = 0.0
    fert_events: List[Tuple[str, Dict[str, float]]] = field(default_factory=list)


# ============================================================
# 🌦 Weather and Daily State (dataclasses)
# ============================================================

@dataclass
class WeatherDay:
    """Daily weather observation or forecast."""
    date: str
    tmin: float
    tmax: float
    rain: float
    rad: float
    et0: Optional[float] = None
    wind: Optional[float] = None
    rh: Optional[float] = None


@dataclass
class FieldState:
    """Instantaneous physiological state of a crop field."""
    date: str
    stage_index: int = 0
    gdd_accum: float = 0.0
    dap: int = 0
    lai: float = 0.05
    biomass_dm_kg_ha: float = 0.0
    soil_water_mm: float = 120.0
    stress_w: float = 1.0
    stress_n: float = 1.0
    n_stock_kg_ha: float = 0.0
    p_stock_kg_ha: float = 0.0
    k_stock_kg_ha: float = 0.0
    notes: Dict[str, float] = field(default_factory=dict)


# ============================================================
# 🌾 Field Configuration (dataclasses)
# ============================================================

@dataclass
class FieldConfig:
    """Configuration of a single simulated field."""
    id: str
    name: str
    area_ha: float
    soil: SoilProfile
    crop: CropParams
    management: Management


# ============================================================
# 📊 Simulation Outputs (dataclasses)
# ============================================================

@dataclass
class DayResult:
    """Daily simulation result record."""
    date: str
    stage: str
    lai: float
    biomass_dm_kg_ha: float
    soil_water_mm: float
    stress_w: float
    stress_n: float
    n_stock_kg_ha: float
    p_stock_kg_ha: float
    k_stock_kg_ha: float
    gdd_progress: Optional[float] = None
    gdd_target: Optional[float] = None
    crop: Optional[str] = None


@dataclass
class RunResult:
    """Aggregate run output per field."""
    field_id: str
    series: List[DayResult]
    yield_t_ha: Optional[float] = None
    harvest_date: Optional[str] = None
    grade: Optional[str] = None


# ============================================================
# 🧱 Agro-Infrastructure (Canvas Builder) (dataclasses)
# ============================================================

@dataclass
class NodeConfig:
    """Network node: field, irrigation source, storage, or market."""
    id: str
    type: Literal["field", "irrigation", "storage", "market"]
    label: str
    x: float
    y: float
    params: Dict[str, Union[float, str]] = field(default_factory=dict)


@dataclass
class LinkConfig:
    """Directed link connecting nodes (e.g., irrigation or transport)."""
    id: str
    from_id: str
    to_id: str
    capacity: Optional[float] = None  # e.g., mm/day or tonnes/day


@dataclass
class ScenarioConfig:
    """Overall simulation network scenario."""
    nodes: List[NodeConfig]
    links: List[LinkConfig]
    weather: List[WeatherDay]
    description: Optional[str] = None


# ============================================================
# 🌾 Field Builder and Harvest Planner (dataclasses)
# ============================================================

@dataclass
class FieldZone:
    """Polygonal field zone for drag-and-drop visualization."""
    id: str
    label: str
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0.0
    crop: Optional[str] = None
    soil_type: Optional[str] = None
    color: Optional[str] = "#66bb6a"
    moisture_status: Optional[float] = 1.0
    growth_stage: Optional[str] = "seedling"
    maturity_ratio: Optional[float] = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HarvestTask:
    """Represents a planned or completed harvest operation."""
    field_id: str
    crop: str
    planned_date: str
    expected_yield_t_ha: float
    maturity_ratio: float
    ripe_color: str = "#e53935"
    actual_yield_t_ha: Optional[float] = None
    completed: bool = False
    notes: Optional[str] = None

    @property
    def is_ready(self) -> bool:
        return self.maturity_ratio >= 0.9

    def mark_completed(self, actual_yield: float) -> None:
        self.actual_yield_t_ha = actual_yield
        self.completed = True


@dataclass
class HarvestPlanner:
    """Aggregates and manages multiple harvest tasks."""
    tasks: List[HarvestTask] = field(default_factory=list)

    def add_task(self, task: HarvestTask) -> None:
        for t in self.tasks:
            if t.field_id == task.field_id and t.crop == task.crop:
                return
        self.tasks.append(task)

    def pending_tasks(self) -> List[HarvestTask]:
        return [t for t in self.tasks if not t.completed]

    def completed_tasks(self) -> List[HarvestTask]:
        return [t for t in self.tasks if t.completed]

    def get_task(self, field_id: str) -> Optional[HarvestTask]:
        return next((t for t in self.tasks if t.field_id == field_id), None)


@dataclass
class FarmLayout:
    """Combines layout geometry with simulation outputs for visualization."""
    id: str
    name: str
    zones: List[FieldZone] = field(default_factory=list)
    harvests: HarvestPlanner = field(default_factory=HarvestPlanner)

    def update_zone_growth(self, field_id: str, maturity: float, water_stress: float) -> None:
        for z in self.zones:
            if z.id == field_id:
                z.maturity_ratio = maturity
                if maturity < 0.3:
                    base_color = "#66bb6a"
                elif maturity < 0.7:
                    base_color = "#fbc02d"
                else:
                    base_color = "#e53935"
                z.color = "#8b4513" if water_stress < 0.6 else base_color
                break


# ============================================================
# 🧭 Master Simulation Entity (dataclass)
# ============================================================

@dataclass
class AgroForgeSimulation:
    """Top-level simulation entity combining all model parts."""
    scenario: ScenarioConfig
    fields: List[FieldConfig]
    layout: FarmLayout
    planner: HarvestPlanner
    timestamp: str
    notes: Optional[str] = None


# ============================================================
# ✅ NEW: FastAPI request/response models expected by app.py
# ============================================================

class FeatureGeometry(BaseModel):
    type: Literal["Point", "LineString", "Polygon"]
    coordinates: Any


class Feature(BaseModel):
    type: Literal["Feature"] = "Feature"
    geometry: FeatureGeometry
    properties: Dict[str, Any] = Field(default_factory=dict)


class SurveyImportRequest(BaseModel):
    """Payload for /survey/import (DXF/KML→GeoJSON placeholder)."""
    name: str
    type: Literal["DXF", "KML", "GeoJSON", "Shapefile", "CSV", "Other"] = "GeoJSON"
    features: List[Feature] = Field(default_factory=list)


class ScenarioRequest(BaseModel):
    """
    Minimal scenario input for /simulate and /harvest/plan.
    Keep fields generic so engine.sim can consume by attribute access.
    """
    lat: float
    lon: float
    crop: str
    area_ha: float = 1.0
    start_date: str = Field(default_factory=lambda: date.today().isoformat())
    horizon_hours: int = 240  # 10 days by default

    # Optional agronomy knobs
    density_plants_m2: float = 4.0
    irrigation_mm_day: float = 0.0


class DayPoint(BaseModel):
    date: str
    stage: Optional[str] = None
    lai: Optional[float] = None
    biomass_dm_kg_ha: Optional[float] = None
    soil_water_mm: Optional[float] = None
    stress_w: Optional[float] = None
    stress_n: Optional[float] = None
    n_stock_kg_ha: Optional[float] = None
    p_stock_kg_ha: Optional[float] = None
    k_stock_kg_ha: Optional[float] = None
    gdd_progress: Optional[float] = None
    gdd_target: Optional[float] = None
    crop: Optional[str] = None


class SimulationResult(BaseModel):
    """
    Flexible response model that will accept either:
    - dicts returned by engine.sim (coerced by FastAPI), or
    - structured data we build directly.
    """
    field_id: Optional[str] = None
    yield_t_ha: Optional[float] = None
    harvest_date: Optional[str] = None
    grade: Optional[str] = None
    series: List[DayPoint] = Field(default_factory=list)
    summary: Dict[str, Any] = Field(default_factory=dict)
