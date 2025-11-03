"""
🌾 AgroForgeSIM – Harvest Planning
---------------------------------
Converts simulation outputs into yield/grade/harvest dates and
builds a cross-field harvest schedule that can drive the UI.

Public API:
- estimate_yield(field, series) -> (yield_t_ha, harvest_date, grade)
- HarvestManager: planner that registers field results and syncs layout
- build_harvest_plan(results, layout=None, storage_capacity_t=100.0) -> dict
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Tuple, Optional

from .models import (
    FieldConfig,
    DayResult,
    HarvestPlanner,
    HarvestTask,
    FarmLayout,
)

__all__ = [
    "estimate_yield",
    "HarvestManager",
    "build_harvest_plan",
]


# ============================================================
# 🌾 CROP YIELD ESTIMATOR
# ============================================================

def estimate_yield(field: FieldConfig, series: List[DayResult]) -> Tuple[float, str, str]:
    """
    Estimate final yield (t/ha), harvest date (ISO), and grade (A/B/C).
    Penalizes harvest index using water stress during flowering & grain fill.
    """
    crop = field.crop
    stages = [d.stage for d in series]

    def _stage_min(stage_name: str, attr: str = "stress_w") -> float:
        vals = [getattr(d, attr) for d in series if d.stage == stage_name] or [1.0]
        return min(vals)

    flower_min = _stage_min("flowering") if "flowering" in stages else 1.0
    grain_min = _stage_min("grainfill") if "grainfill" in stages else 1.0

    final = series[-1]
    biomass = final.biomass_dm_kg_ha  # dry matter kg/ha

    # Harvest index penalty from stress sensitivities
    hi_penalty = 1.0 \
        - crop.stress_sensitivity.get("flower_water", 0.0) * (1 - flower_min) \
        - crop.stress_sensitivity.get("grainfill_water", 0.0) * (1 - grain_min)

    hi_eff = max(0.3, min(1.0, crop.hi * hi_penalty))
    yield_t_ha = (biomass * hi_eff) / 1000.0  # t/ha

    # Harvest date = first maturity/grainfill day if reached, else last simulated day
    maturity_idx = next(
        (i for i, d in enumerate(series)
         if d.stage in ("maturity", "grainfill") and i > 0),
        len(series) - 1,
    )
    harvest_date = series[maturity_idx].date

    # Grade
    avg_stress = (flower_min + grain_min) / 2
    if avg_stress > 0.8:
        grade = "A"
    elif avg_stress > 0.6:
        grade = "B"
    else:
        grade = "C"

    return float(yield_t_ha), harvest_date, grade


# ============================================================
# 🧮 HARVEST PLANNER CORE ENGINE
# ============================================================

class HarvestManager:
    """
    Harvest scheduling system that registers simulated field results,
    updates the canvas layout, and produces a serialized plan.
    """

    def __init__(self, planner: Optional[HarvestPlanner] = None, layout: Optional[FarmLayout] = None):
        self.planner = planner or HarvestPlanner()
        self.layout = layout or FarmLayout(id="Default", name="AutoFarm")

    def register_field_result(
        self,
        field_id: str,
        crop: str,
        series: List[DayResult],
        yield_t_ha: float,
        harvest_date: str,
        maturity: float,
    ) -> None:
        """Register a simulated field into the planner and update UI color."""
        self.planner.add_task(
            HarvestTask(
                field_id=field_id,
                crop=crop,
                planned_date=harvest_date,
                expected_yield_t_ha=yield_t_ha,
                maturity_ratio=maturity,
            )
        )
        # Sync layout color with ripeness & stress
        self.layout.update_zone_growth(field_id, maturity, series[-1].stress_w)

    def summarize_plan(self) -> Dict:
        """Overview metrics for dashboards."""
        total = len(self.planner.tasks)
        avg_maturity = round(
            sum(t.maturity_ratio for t in self.planner.tasks) / max(1, total), 2
        )
        return {
            "total_fields": total,
            "pending": len(self.planner.pending_tasks()),
            "completed": len(self.planner.completed_tasks()),
            "average_maturity": avg_maturity,
        }

    def mark_completed(self, field_id: str, actual_yield: float) -> None:
        """Mark a task done and set a harvested color."""
        task = self.planner.get_task(field_id)
        if task:
            task.mark_completed(actual_yield)
            zone = next((z for z in self.layout.zones if z.id == field_id), None)
            if zone:
                zone.color = "#8d6e63"  # harvested/bare field

    def plan_schedule(self, storage_capacity_t: float = 100.0) -> List[Dict]:
        """
        Build a capacity-aware plan across fields (simple FIFO by planned_date).
        """
        plan: List[Dict] = []
        capacity = storage_capacity_t
        for t in sorted(self.planner.tasks, key=lambda x: x.planned_date):
            ripeness_color = "#66bb6a" if t.maturity_ratio < 0.3 else "#fbc02d" if t.maturity_ratio < 0.7 else "#e53935"
            plan.append({
                "field_id": t.field_id,
                "crop": t.crop,
                "planned_date": t.planned_date,
                "expected_yield_t": round(t.expected_yield_t_ha, 2),
                "grade": "A" if t.is_ready else "B",
                "maturity_ratio": t.maturity_ratio,
                "ripe_color": ripeness_color,
            })
            capacity -= t.expected_yield_t_ha
            if capacity <= 0:
                break
        return plan


# ============================================================
# 📊 API/CLI UTILITY
# ============================================================

def build_harvest_plan(
    results: Dict[str, object],
    layout: Optional[FarmLayout] = None,
    storage_capacity_t: float = 100.0,
) -> Dict:
    """
    Generate a JSON-serializable harvest plan from simulated field results.

    Parameters
    ----------
    results: dict[str, RunResult]
        Mapping of field_id -> RunResult (from engine.sim.run_field).
    layout: Optional[FarmLayout]
        Canvas layout; if None, a default layout object is used.
    storage_capacity_t: float
        Simple capacity gate to stop planning once storage is full.

    Returns
    -------
    dict
        {
          "summary": {...},
          "plan": [...],
          "fields": [... HarvestTask as dict ...],
          "timestamp": "ISO8601"
        }
    """
    planner = HarvestPlanner()
    manager = HarvestManager(planner=planner, layout=layout)

    for fid, res in results.items():
        last = res.series[-1]
        maturity = min(1.0, (last.gdd_progress or 0.0) / (last.gdd_target or 1.0))
        yld = float(res.yield_t_ha or 0.0)
        manager.register_field_result(
            field_id=fid,
            crop=last.crop or "unknown",
            series=res.series,
            yield_t_ha=yld,
            harvest_date=res.harvest_date,
            maturity=maturity,
        )

    summary = manager.summarize_plan()
    plan = manager.plan_schedule(storage_capacity_t)

    return {
        "summary": summary,
        "plan": plan,
        "fields": [t.__dict__ for t in manager.planner.tasks],
        "timestamp": datetime.now().isoformat(timespec="seconds"),
    }
