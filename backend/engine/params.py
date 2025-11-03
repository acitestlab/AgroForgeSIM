"""
AgroForgeSIM – Expanded Crop Parameter Definitions
==================================================
This module centralizes crop defaults for the simulation engine and
exposes quick business baselines used by API/CLI.

- Rich, simulation-grade defaults (CropParams/StageParams) per crop
- Crop categories for API/UI
- Business baselines (tpa/days) for quick projections

NOTE: Values are placeholders; calibrate with literature/field trials.

Used by:
- engine.sim / engine.harvest
- backend/app (e.g., /api/crops)
- backend/cli (scenario runs)

"""

from __future__ import annotations

from .models import CropParams, StageParams  # simulation-grade dataclasses

# -------------------------------------------------------------------
# Crop category mapping (used by /api/crops and front-end listing)
# -------------------------------------------------------------------
crop_categories = {
    "Cereals": ["Maize", "Rice", "Sorghum"],
    "Root and Tuber Crops": ["Cassava", "Yams"],
    "Vegetables": [
        "Spinach", "Cucumber", "Broccoli", "Tomato", "Onion",
        "Okra", "Cabbage", "Pepper", "Amaranth"
    ],
    "Fruits": [
        "Mango", "Apple", "Orange", "Banana", "Pineapple",
        "Guava", "Papaya", "Lemon", "Grapes"
    ],
    "Legumes": ["Beans", "Cowpea", "Chickpea", "Lentils", "Fava Beans", "Mung Bean"],
}

# -------------------------------------------------------------------
# Simulation-grade defaults (per crop)
# Each function returns a CropParams(...) with consistent stage structure.
# -------------------------------------------------------------------

# ------------------------ Cereals ------------------------

def maize_defaults() -> CropParams:
    return CropParams(
        species="maize", cultivar="DMR-Early",
        tb=8.0, to=30.0, lai_max=5.0, hi=0.48,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.4, "n": 0.5},
        stages=[
            StageParams("incubation", gdd_target=80, kc=0.35, rue=0.8, lai_gain=0.10,
                        partition={"leaf": 0.6, "stem": 0.4, "root": 0.0, "storage": 0.0},
                        nuptake_target={"N": 15, "P": 5, "K": 10}),
            StageParams("vegetative", gdd_target=650, kc=1.05, rue=1.6, lai_gain=0.16,
                        partition={"leaf": 0.45, "stem": 0.40, "root": 0.15, "storage": 0.0},
                        nuptake_target={"N": 80, "P": 20, "K": 60}),
            StageParams("flowering", gdd_target=850, kc=1.20, rue=1.7, lai_gain=0.10,
                        partition={"leaf": 0.25, "stem": 0.35, "root": 0.10, "storage": 0.30},
                        nuptake_target={"N": 40, "P": 10, "K": 30}),
            StageParams("grainfill", gdd_target=1200, kc=0.95, rue=1.4, lai_gain=0.06,
                        partition={"leaf": 0.10, "stem": 0.15, "root": 0.05, "storage": 0.70},
                        nuptake_target={"N": 20, "P": 5, "K": 15}),
            StageParams("maturity", kc=0.6, rue=0.5, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def rice_defaults() -> CropParams:
    return CropParams(
        species="rice", cultivar="IR-64",
        tb=10.0, to=30.0, lai_max=6.0, hi=0.50,
        stress_sensitivity={"flower_water": 0.7, "grainfill_water": 0.5, "n": 0.45},
        stages=[
            StageParams("nursery", dap_target=20, kc=1.0, rue=1.5, lai_gain=0.10,
                        partition={"leaf": 0.5, "stem": 0.4, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 25, "P": 10, "K": 25}),
            StageParams("vegetative", dap_target=60, kc=1.1, rue=1.8, lai_gain=0.15,
                        partition={"leaf": 0.4, "stem": 0.4, "root": 0.2, "storage": 0.0},
                        nuptake_target={"N": 60, "P": 20, "K": 50}),
            StageParams("flowering", dap_target=90, kc=1.2, rue=1.9, lai_gain=0.08,
                        partition={"leaf": 0.2, "stem": 0.3, "root": 0.1, "storage": 0.4},
                        nuptake_target={"N": 30, "P": 10, "K": 30}),
            StageParams("grainfill", dap_target=120, kc=1.1, rue=1.5, lai_gain=0.06,
                        partition={"leaf": 0.1, "stem": 0.1, "root": 0.05, "storage": 0.75},
                        nuptake_target={"N": 20, "P": 6, "K": 25}),
            StageParams("maturity", kc=0.8, rue=0.9, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def sorghum_defaults() -> CropParams:
    return CropParams(
        species="sorghum", cultivar="Macia",
        tb=8.0, to=32.0, lai_max=4.5, hi=0.45,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.4, "n": 0.5},
        stages=[
            StageParams("emergence", dap_target=10, kc=0.4, rue=1.0, lai_gain=0.08,
                        partition={"leaf": 0.7, "stem": 0.2, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 15}),
            StageParams("vegetative", dap_target=45, kc=1.05, rue=1.6, lai_gain=0.15,
                        partition={"leaf": 0.45, "stem": 0.35, "root": 0.20, "storage": 0.0},
                        nuptake_target={"N": 50, "P": 15, "K": 40}),
            StageParams("flowering", dap_target=75, kc=1.2, rue=1.7, lai_gain=0.08,
                        partition={"leaf": 0.25, "stem": 0.25, "root": 0.10, "storage": 0.40},
                        nuptake_target={"N": 30, "P": 8, "K": 30}),
            StageParams("grainfill", dap_target=105, kc=1.0, rue=1.4, lai_gain=0.05,
                        partition={"leaf": 0.10, "stem": 0.10, "root": 0.05, "storage": 0.75},
                        nuptake_target={"N": 15, "P": 5, "K": 20}),
            StageParams("maturity", kc=0.85, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

# ------------------- Root & Tuber Crops -------------------

def cassava_defaults() -> CropParams:
    return CropParams(
        species="cassava", cultivar="Local-12m",
        tb=12.0, to=30.0, lai_max=4.0, hi=0.55,
        stress_sensitivity={"flower_water": 0.3, "grainfill_water": 0.3, "n": 0.4},
        stages=[
            StageParams("incubation", dap_target=15, kc=0.4, rue=0.9, lai_gain=0.09,
                        partition={"leaf": 0.6, "stem": 0.3, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 5, "K": 15}),
            StageParams("vegetative", dap_target=120, kc=1.0, rue=1.5, lai_gain=0.14,
                        partition={"leaf": 0.45, "stem": 0.35, "root": 0.20, "storage": 0.0},
                        nuptake_target={"N": 60, "P": 20, "K": 80}),
            StageParams("bulking", dap_target=300, kc=1.05, rue=1.4, lai_gain=0.08,
                        partition={"leaf": 0.20, "stem": 0.25, "root": 0.15, "storage": 0.40},
                        nuptake_target={"N": 30, "P": 10, "K": 60}),
            StageParams("maturity", dap_target=360, kc=0.9, rue=1.0, lai_gain=0.02,
                        partition={"leaf": 0.05, "stem": 0.10, "root": 0.10, "storage": 0.75},
                        nuptake_target={"N": 10, "P": 5, "K": 20})
        ]
    )

def yams_defaults() -> CropParams:
    return CropParams(
        species="yam", cultivar="White Yam",
        tb=12.0, to=30.0, lai_max=4.5, hi=0.60,
        stress_sensitivity={"flower_water": 0.4, "grainfill_water": 0.3, "n": 0.4},
        stages=[
            StageParams("sprouting", dap_target=20, kc=0.5, rue=1.0, lai_gain=0.08,
                        partition={"leaf": 0.6, "stem": 0.3, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 15, "P": 6, "K": 20}),
            StageParams("vegetative", dap_target=100, kc=1.0, rue=1.6, lai_gain=0.14,
                        partition={"leaf": 0.45, "stem": 0.35, "root": 0.20, "storage": 0.0},
                        nuptake_target={"N": 70, "P": 25, "K": 60}),
            StageParams("tuberization", dap_target=240, kc=1.05, rue=1.4, lai_gain=0.08,
                        partition={"leaf": 0.20, "stem": 0.25, "root": 0.15, "storage": 0.40},
                        nuptake_target={"N": 35, "P": 12, "K": 50}),
            StageParams("maturity", dap_target=300, kc=0.9, rue=1.0, lai_gain=0.02,
                        partition={"leaf": 0.05, "stem": 0.10, "root": 0.10, "storage": 0.75},
                        nuptake_target={"N": 10, "P": 4, "K": 15})
        ]
    )

# ------------------------- Vegetables -------------------------

def tomato_defaults() -> CropParams:
    return CropParams(
        species="tomato", cultivar="Field-Det",
        tb=10.0, to=28.0, lai_max=4.5, hi=0.65,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.5},
        stages=[
            StageParams("incubation", gdd_target=80, kc=0.5, rue=1.2, lai_gain=0.10,
                        partition={"leaf": 0.6, "stem": 0.35, "root": 0.05, "storage": 0.0},
                        nuptake_target={"N": 20, "P": 8, "K": 18}),
            StageParams("vegetative", gdd_target=400, kc=1.05, rue=1.6, lai_gain=0.16,
                        partition={"leaf": 0.45, "stem": 0.35, "root": 0.20, "storage": 0.0},
                        nuptake_target={"N": 60, "P": 20, "K": 60}),
            StageParams("flowering", gdd_target=600, kc=1.15, rue=1.7, lai_gain=0.10,
                        partition={"leaf": 0.25, "stem": 0.25, "root": 0.10, "storage": 0.40},
                        nuptake_target={"N": 30, "P": 10, "K": 40}),
            StageParams("fruitfill", gdd_target=900, kc=1.15, rue=1.5, lai_gain=0.06,
                        partition={"leaf": 0.10, "stem": 0.15, "root": 0.05, "storage": 0.70},
                        nuptake_target={"N": 20, "P": 8, "K": 50}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def pepper_defaults() -> CropParams:
    return CropParams(
        species="pepper", cultivar="Capsicum-Field",
        tb=10.0, to=28.0, lai_max=4.0, hi=0.60,
        stress_sensitivity={"flower_water": 0.55, "grainfill_water": 0.45, "n": 0.45},
        stages=[
            StageParams("incubation", gdd_target=90, kc=0.5, rue=1.1, lai_gain=0.09,
                        partition={"leaf": 0.6, "stem": 0.35, "root": 0.05, "storage": 0.0},
                        nuptake_target={"N": 18, "P": 7, "K": 16}),
            StageParams("vegetative", gdd_target=420, kc=1.0, rue=1.5, lai_gain=0.15,
                        partition={"leaf": 0.45, "stem": 0.35, "root": 0.20, "storage": 0.0},
                        nuptake_target={"N": 55, "P": 18, "K": 55}),
            StageParams("flowering", gdd_target=620, kc=1.1, rue=1.6, lai_gain=0.10,
                        partition={"leaf": 0.20, "stem": 0.25, "root": 0.10, "storage": 0.45},
                        nuptake_target={"N": 25, "P": 9, "K": 35}),
            StageParams("fruitfill", gdd_target=950, kc=1.1, rue=1.4, lai_gain=0.06,
                        partition={"leaf": 0.10, "stem": 0.15, "root": 0.05, "storage": 0.70},
                        nuptake_target={"N": 18, "P": 7, "K": 40}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def onion_defaults() -> CropParams:
    return CropParams(
        species="onion", cultivar="Bulb-IntermediateDay",
        tb=5.0, to=22.0, lai_max=3.0, hi=0.75,
        stress_sensitivity={"flower_water": 0.5, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("incubation", gdd_target=60, kc=0.45, rue=1.0, lai_gain=0.08,
                        partition={"leaf": 0.7, "stem": 0.2, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 15, "P": 6, "K": 18}),
            StageParams("leaf", gdd_target=300, kc=0.95, rue=1.4, lai_gain=0.14,
                        partition={"leaf": 0.55, "stem": 0.25, "root": 0.20, "storage": 0.0},
                        nuptake_target={"N": 50, "P": 15, "K": 50}),
            StageParams("bulbinit", gdd_target=450, kc=1.05, rue=1.4, lai_gain=0.10,
                        partition={"leaf": 0.30, "stem": 0.10, "root": 0.10, "storage": 0.50},
                        nuptake_target={"N": 25, "P": 8, "K": 35}),
            StageParams("bulbing", gdd_target=700, kc=1.05, rue=1.2, lai_gain=0.06,
                        partition={"leaf": 0.10, "stem": 0.05, "root": 0.05, "storage": 0.80},
                        nuptake_target={"N": 15, "P": 5, "K": 30}),
            StageParams("maturity", kc=0.85, rue=0.7, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def garlic_defaults() -> CropParams:
    return CropParams(
        species="garlic", cultivar="Softneck",
        tb=3.0, to=20.0, lai_max=2.8, hi=0.72,
        stress_sensitivity={"flower_water": 0.45, "grainfill_water": 0.45, "n": 0.35},
        stages=[
            StageParams("incubation", gdd_target=40, kc=0.45, rue=0.9, lai_gain=0.07,
                        partition={"leaf": 0.7, "stem": 0.2, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 12, "P": 5, "K": 15}),
            StageParams("leaf", gdd_target=250, kc=0.95, rue=1.3, lai_gain=0.12,
                        partition={"leaf": 0.55, "stem": 0.25, "root": 0.20, "storage": 0.0},
                        nuptake_target={"N": 40, "P": 12, "K": 45}),
            StageParams("bulb", gdd_target=520, kc=1.0, rue=1.1, lai_gain=0.06,
                        partition={"leaf": 0.10, "stem": 0.05, "root": 0.05, "storage": 0.80},
                        nuptake_target={"N": 18, "P": 6, "K": 28}),
            StageParams("maturity", kc=0.8, rue=0.7, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def carrot_defaults() -> CropParams:
    return CropParams(
        species="carrot", cultivar="Nantes",
        tb=4.0, to=22.0, lai_max=3.5, hi=0.80,
        stress_sensitivity={"flower_water": 0.4, "grainfill_water": 0.4, "n": 0.35},
        stages=[
            StageParams("incubation", gdd_target=50, kc=0.45, rue=1.0, lai_gain=0.08,
                        partition={"leaf": 0.7, "stem": 0.2, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 15}),
            StageParams("vegetative", gdd_target=300, kc=0.95, rue=1.4, lai_gain=0.14,
                        partition={"leaf": 0.50, "stem": 0.20, "root": 0.30, "storage": 0.0},
                        nuptake_target={"N": 40, "P": 12, "K": 50}),
            StageParams("bulking", gdd_target=650, kc=1.0, rue=1.2, lai_gain=0.07,
                        partition={"leaf": 0.10, "stem": 0.10, "root": 0.10, "storage": 0.70},
                        nuptake_target={"N": 20, "P": 6, "K": 35}),
            StageParams("maturity", kc=0.85, rue=0.7, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def spinach_defaults() -> CropParams:
    return CropParams(
        species="spinach", cultivar="AgroSpin-F1",
        tb=5.0, to=20.0, lai_max=3.0, hi=0.75,
        stress_sensitivity={"flower_water": 0.5, "grainfill_water": 0.4, "n": 0.3},
        stages=[
            StageParams("germination", dap_target=10, kc=0.5, rue=0.9, lai_gain=0.08,
                        partition={"leaf": 0.8, "stem": 0.1, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 12}),
            StageParams("vegetative", dap_target=30, kc=1.1, rue=1.2, lai_gain=0.14,
                        partition={"leaf": 0.70, "stem": 0.15, "root": 0.15, "storage": 0.0},
                        nuptake_target={"N": 25, "P": 10, "K": 30}),
            StageParams("harvest", dap_target=45, kc=0.9, rue=1.0, lai_gain=0.02,
                        partition={"leaf": 1.0, "stem": 0.0, "root": 0.0, "storage": 0.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def cucumber_defaults() -> CropParams:
    return CropParams(
        species="cucumber", cultivar="Field-Cu",
        tb=8.0, to=30.0, lai_max=4.0, hi=0.70,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("incubation", gdd_target=50, kc=0.5, rue=1.0, lai_gain=0.10,
                        partition={"leaf": 0.7, "stem": 0.2, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 15, "P": 6, "K": 15}),
            StageParams("vegetative", gdd_target=200, kc=1.0, rue=1.4, lai_gain=0.14,
                        partition={"leaf": 0.55, "stem": 0.25, "root": 0.20, "storage": 0.0},
                        nuptake_target={"N": 40, "P": 12, "K": 40}),
            StageParams("flowering", gdd_target=300, kc=1.1, rue=1.6, lai_gain=0.10,
                        partition={"leaf": 0.25, "stem": 0.25, "root": 0.10, "storage": 0.40},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("fruitfill", gdd_target=450, kc=1.1, rue=1.5, lai_gain=0.06,
                        partition={"leaf": 0.10, "stem": 0.15, "root": 0.05, "storage": 0.70},
                        nuptake_target={"N": 15, "P": 5, "K": 30}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def broccoli_defaults() -> CropParams:
    return CropParams(
        species="broccoli", cultivar="Calabrese",
        tb=7.0, to=25.0, lai_max=3.5, hi=0.65,
        stress_sensitivity={"flower_water": 0.5, "grainfill_water": 0.45, "n": 0.35},
        stages=[
            StageParams("incubation", gdd_target=60, kc=0.45, rue=1.0, lai_gain=0.08,
                        partition={"leaf": 0.7, "stem": 0.2, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 15, "P": 6, "K": 20}),
            StageParams("vegetative", gdd_target=200, kc=0.95, rue=1.3, lai_gain=0.14,
                        partition={"leaf": 0.50, "stem": 0.25, "root": 0.25, "storage": 0.0},
                        nuptake_target={"N": 40, "P": 12, "K": 40}),
            StageParams("head formation", gdd_target=300, kc=1.1, rue=1.5, lai_gain=0.10,
                        partition={"leaf": 0.25, "stem": 0.20, "root": 0.10, "storage": 0.45},
                        nuptake_target={"N": 30, "P": 8, "K": 30}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def okra_defaults() -> CropParams:
    return CropParams(
        species="okra", cultivar="Local-Okra",
        tb=10.0, to=32.0, lai_max=4.0, hi=0.65,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("incubation", dap_target=10, kc=0.5, rue=1.0, lai_gain=0.10,
                        partition={"leaf": 0.7, "stem": 0.2, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 15, "P": 5, "K": 20}),
            StageParams("vegetative", dap_target=60, kc=1.0, rue=1.4, lai_gain=0.14,
                        partition={"leaf": 0.55, "stem": 0.20, "root": 0.25, "storage": 0.0},
                        nuptake_target={"N": 35, "P": 10, "K": 35}),
            StageParams("flowering", dap_target=100, kc=1.1, rue=1.5, lai_gain=0.08,
                        partition={"leaf": 0.25, "stem": 0.25, "root": 0.10, "storage": 0.40},
                        nuptake_target={"N": 20, "P": 6, "K": 25}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def cabbage_defaults() -> CropParams:
    return CropParams(
        species="cabbage", cultivar="Hybrid",
        tb=7.0, to=25.0, lai_max=3.0, hi=0.70,
        stress_sensitivity={"flower_water": 0.5, "grainfill_water": 0.45, "n": 0.35},
        stages=[
            StageParams("incubation", gdd_target=50, kc=0.4, rue=0.9, lai_gain=0.08,
                        partition={"leaf": 0.7, "stem": 0.2, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 12, "P": 5, "K": 18}),
            StageParams("vegetative", gdd_target=180, kc=0.95, rue=1.3, lai_gain=0.14,
                        partition={"leaf": 0.55, "stem": 0.20, "root": 0.25, "storage": 0.0},
                        nuptake_target={"N": 30, "P": 10, "K": 30}),
            StageParams("heading", gdd_target=300, kc=1.0, rue=1.4, lai_gain=0.10,
                        partition={"leaf": 0.25, "stem": 0.20, "root": 0.10, "storage": 0.45},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def amaranth_defaults() -> CropParams:
    return CropParams(
        species="amaranth", cultivar="Amara",
        tb=10.0, to=28.0, lai_max=3.5, hi=0.75,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("germination", dap_target=8, kc=0.5, rue=0.9, lai_gain=0.08,
                        partition={"leaf": 0.8, "stem": 0.1, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 12}),
            StageParams("vegetative", dap_target=30, kc=1.0, rue=1.3, lai_gain=0.14,
                        partition={"leaf": 0.60, "stem": 0.15, "root": 0.25, "storage": 0.0},
                        nuptake_target={"N": 25, "P": 8, "K": 30}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

# --------------------------- Fruits ---------------------------

def mango_defaults() -> CropParams:
    return CropParams(
        species="mango", cultivar="Alphonso",
        tb=12.0, to=30.0, lai_max=5.0, hi=0.50,
        stress_sensitivity={"flower_water": 0.7, "grainfill_water": 0.6, "n": 0.4},
        stages=[
            StageParams("budbreak", dap_target=20, kc=0.7, rue=1.2, lai_gain=0.03,
                        partition={"leaf": 0.5, "stem": 0.4, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 20, "P": 6, "K": 25}),
            StageParams("flowering", dap_target=50, kc=0.8, rue=1.3, lai_gain=0.04,
                        partition={"leaf": 0.3, "stem": 0.2, "root": 0.1, "storage": 0.4},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("fruitset", dap_target=120, kc=0.95, rue=1.4, lai_gain=0.05,
                        partition={"leaf": 0.2, "stem": 0.15, "root": 0.05, "storage": 0.60},
                        nuptake_target={"N": 30, "P": 10, "K": 40}),
            StageParams("enlargement", dap_target=240, kc=1.05, rue=1.3, lai_gain=0.05,
                        partition={"leaf": 0.10, "stem": 0.10, "root": 0.05, "storage": 0.75},
                        nuptake_target={"N": 25, "P": 8, "K": 45}),
            StageParams("maturation", dap_target=300, kc=0.95, rue=1.0, lai_gain=0.02,
                        partition={"leaf": 0.05, "stem": 0.05, "root": 0.05, "storage": 0.85},
                        nuptake_target={"N": 10, "P": 4, "K": 20})
        ]
    )

def apple_defaults() -> CropParams:
    return CropParams(
        species="apple", cultivar="Gala",
        tb=6.0, to=26.0, lai_max=4.5, hi=0.60,
        stress_sensitivity={"flower_water": 0.75, "grainfill_water": 0.55, "n": 0.4},
        stages=[
            StageParams("budbreak", dap_target=20, kc=0.7, rue=1.2, lai_gain=0.03,
                        partition={"leaf": 0.5, "stem": 0.4, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 22, "P": 6, "K": 22}),
            StageParams("flowering", dap_target=45, kc=0.8, rue=1.25, lai_gain=0.04,
                        partition={"leaf": 0.3, "stem": 0.2, "root": 0.1, "storage": 0.4},
                        nuptake_target={"N": 18, "P": 6, "K": 20}),
            StageParams("fruitset", dap_target=110, kc=0.95, rue=1.35, lai_gain=0.05,
                        partition={"leaf": 0.2, "stem": 0.15, "root": 0.05, "storage": 0.60},
                        nuptake_target={"N": 28, "P": 9, "K": 35}),
            StageParams("enlargement", dap_target=220, kc=1.0, rue=1.25, lai_gain=0.05,
                        partition={"leaf": 0.10, "stem": 0.10, "root": 0.05, "storage": 0.75},
                        nuptake_target={"N": 22, "P": 7, "K": 38}),
            StageParams("maturation", dap_target=280, kc=0.9, rue=1.0, lai_gain=0.02,
                        partition={"leaf": 0.05, "stem": 0.05, "root": 0.05, "storage": 0.85},
                        nuptake_target={"N": 8, "P": 3, "K": 15})
        ]
    )

def orange_defaults() -> CropParams:
    return CropParams(
        species="orange", cultivar="Valencia",
        tb=8.0, to=28.0, lai_max=5.0, hi=0.55,
        stress_sensitivity={"flower_water": 0.7, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("budbreak", dap_target=20, kc=0.7, rue=1.2, lai_gain=0.03,
                        partition={"leaf": 0.5, "stem": 0.4, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 20, "P": 6, "K": 25}),
            StageParams("flowering", dap_target=50, kc=0.8, rue=1.3, lai_gain=0.04,
                        partition={"leaf": 0.3, "stem": 0.2, "root": 0.1, "storage": 0.4},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("fruitset", dap_target=120, kc=0.95, rue=1.4, lai_gain=0.05,
                        partition={"leaf": 0.2, "stem": 0.15, "root": 0.05, "storage": 0.60},
                        nuptake_target={"N": 30, "P": 10, "K": 40}),
            StageParams("enlargement", dap_target=240, kc=1.05, rue=1.3, lai_gain=0.05,
                        partition={"leaf": 0.10, "stem": 0.10, "root": 0.05, "storage": 0.75},
                        nuptake_target={"N": 25, "P": 8, "K": 45}),
            StageParams("maturation", dap_target=300, kc=0.95, rue=1.0, lai_gain=0.02,
                        partition={"leaf": 0.05, "stem": 0.05, "root": 0.05, "storage": 0.85},
                        nuptake_target={"N": 10, "P": 4, "K": 20})
        ]
    )

def banana_defaults() -> CropParams:
    return CropParams(
        species="banana", cultivar="Cavendish",
        tb=12.0, to=30.0, lai_max=6.0, hi=0.50,
        stress_sensitivity={"flower_water": 0.7, "grainfill_water": 0.6, "n": 0.4},
        stages=[
            StageParams("vegetative", dap_target=120, kc=1.0, rue=1.5, lai_gain=0.05,
                        partition={"leaf": 0.6, "stem": 0.3, "root": 0.1, "storage": 0.0},
                        nuptake_target={"N": 30, "P": 10, "K": 35}),
            StageParams("fruiting", dap_target=240, kc=1.1, rue=1.4, lai_gain=0.03,
                        partition={"leaf": 0.2, "stem": 0.1, "root": 0.05, "storage": 0.65},
                        nuptake_target={"N": 25, "P": 8, "K": 30}),
            StageParams("maturity", kc=0.9, rue=0.9, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def pineapple_defaults() -> CropParams:
    return CropParams(
        species="pineapple", cultivar="Smooth Cayenne",
        tb=10.0, to=28.0, lai_max=4.0, hi=0.55,
        stress_sensitivity={"flower_water": 0.65, "grainfill_water": 0.50, "n": 0.35},
        stages=[
            StageParams("veg_growth", dap_target=200, kc=0.9, rue=1.3, lai_gain=0.04,
                        partition={"leaf": 0.5, "stem": 0.3, "root": 0.2, "storage": 0.0},
                        nuptake_target={"N": 20, "P": 6, "K": 25}),
            StageParams("fruit_growth", dap_target=300, kc=1.0, rue=1.2, lai_gain=0.03,
                        partition={"leaf": 0.2, "stem": 0.15, "root": 0.05, "storage": 0.75},
                        nuptake_target={"N": 15, "P": 5, "K": 20}),
            StageParams("maturity", kc=0.85, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def guava_defaults() -> CropParams:
    return CropParams(
        species="guava", cultivar="Tropical",
        tb=10.0, to=28.0, lai_max=4.5, hi=0.60,
        stress_sensitivity={"flower_water": 0.7, "grainfill_water": 0.55, "n": 0.4},
        stages=[
            StageParams("flowering", dap_target=30, kc=0.8, rue=1.3, lai_gain=0.05,
                        partition={"leaf": 0.4, "stem": 0.3, "root": 0.1, "storage": 0.2},
                        nuptake_target={"N": 15, "P": 5, "K": 20}),
            StageParams("fruit_growth", dap_target=90, kc=0.9, rue=1.4, lai_gain=0.04,
                        partition={"leaf": 0.2, "stem": 0.15, "root": 0.05, "storage": 0.60},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("maturity", kc=0.9, rue=0.9, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def papaya_defaults() -> CropParams:
    return CropParams(
        species="papaya", cultivar="Solo",
        tb=8.0, to=28.0, lai_max=4.5, hi=0.65,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("vegetative", dap_target=100, kc=0.9, rue=1.3, lai_gain=0.04,
                        partition={"leaf": 0.5, "stem": 0.3, "root": 0.2, "storage": 0.0},
                        nuptake_target={"N": 20, "P": 6, "K": 25}),
            StageParams("fruiting", dap_target=200, kc=1.0, rue=1.2, lai_gain=0.03,
                        partition={"leaf": 0.2, "stem": 0.15, "root": 0.05, "storage": 0.75},
                        nuptake_target={"N": 15, "P": 5, "K": 20}),
            StageParams("maturity", kc=0.85, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def lemon_defaults() -> CropParams:
    return CropParams(
        species="lemon", cultivar="Eureka",
        tb=10.0, to=28.0, lai_max=4.0, hi=0.60,
        stress_sensitivity={"flower_water": 0.7, "grainfill_water": 0.55, "n": 0.4},
        stages=[
            StageParams("flowering", dap_target=30, kc=0.8, rue=1.3, lai_gain=0.05,
                        partition={"leaf": 0.3, "stem": 0.2, "root": 0.1, "storage": 0.4},
                        nuptake_target={"N": 15, "P": 5, "K": 20}),
            StageParams("fruit_growth", dap_target=90, kc=0.9, rue=1.4, lai_gain=0.04,
                        partition={"leaf": 0.2, "stem": 0.15, "root": 0.05, "storage": 0.60},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("maturity", kc=0.9, rue=0.9, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def grapes_defaults() -> CropParams:
    return CropParams(
        species="grapes", cultivar="Vitis",
        tb=8.0, to=28.0, lai_max=5.0, hi=0.60,
        stress_sensitivity={"flower_water": 0.7, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("budburst", dap_target=20, kc=0.7, rue=1.2, lai_gain=0.03,
                        partition={"leaf": 0.4, "stem": 0.4, "root": 0.1, "storage": 0.1},
                        nuptake_target={"N": 20, "P": 6, "K": 25}),
            StageParams("flowering", dap_target=50, kc=0.8, rue=1.3, lai_gain=0.04,
                        partition={"leaf": 0.3, "stem": 0.2, "root": 0.1, "storage": 0.4},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("veraison", dap_target=100, kc=0.95, rue=1.4, lai_gain=0.05,
                        partition={"leaf": 0.2, "stem": 0.15, "root": 0.05, "storage": 0.60},
                        nuptake_target={"N": 30, "P": 10, "K": 40}),
            StageParams("ripening", dap_target=150, kc=0.9, rue=1.0, lai_gain=0.02,
                        partition={"leaf": 0.1, "stem": 0.05, "root": 0.05, "storage": 0.80},
                        nuptake_target={"N": 10, "P": 4, "K": 20}),
            StageParams("maturity", kc=0.85, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

# ---------------------------- Legumes ----------------------------

def beans_defaults() -> CropParams:
    return CropParams(
        species="beans", cultivar="Common Bean",
        tb=10.0, to=28.0, lai_max=3.5, hi=0.60,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("germination", dap_target=7, kc=0.5, rue=1.0, lai_gain=0.10,
                        partition={"leaf": 0.6, "stem": 0.2, "root": 0.2, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 12}),
            StageParams("vegetative", dap_target=30, kc=1.0, rue=1.4, lai_gain=0.14,
                        partition={"leaf": 0.50, "stem": 0.20, "root": 0.30, "storage": 0.0},
                        nuptake_target={"N": 25, "P": 8, "K": 30}),
            StageParams("flowering", dap_target=45, kc=1.1, rue=1.5, lai_gain=0.10,
                        partition={"leaf": 0.25, "stem": 0.20, "root": 0.10, "storage": 0.45},
                        nuptake_target={"N": 20, "P": 6, "K": 25}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def cowpea_defaults() -> CropParams:
    return CropParams(
        species="cowpea", cultivar="Local Cowpea",
        tb=10.0, to=28.0, lai_max=3.0, hi=0.65,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.45},
        stages=[
            StageParams("germination", dap_target=7, kc=0.5, rue=1.0, lai_gain=0.09,
                        partition={"leaf": 0.6, "stem": 0.2, "root": 0.2, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 12}),
            StageParams("vegetative", dap_target=25, kc=1.0, rue=1.3, lai_gain=0.13,
                        partition={"leaf": 0.50, "stem": 0.20, "root": 0.30, "storage": 0.0},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("flowering", dap_target=40, kc=1.1, rue=1.4, lai_gain=0.08,
                        partition={"leaf": 0.25, "stem": 0.20, "root": 0.10, "storage": 0.45},
                        nuptake_target={"N": 15, "P": 6, "K": 20}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def chickpea_defaults() -> CropParams:
    return CropParams(
        species="chickpea", cultivar="Kabuli",
        tb=8.0, to=28.0, lai_max=3.5, hi=0.65,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.45},
        stages=[
            StageParams("germination", dap_target=8, kc=0.5, rue=1.0, lai_gain=0.09,
                        partition={"leaf": 0.6, "stem": 0.2, "root": 0.2, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 12}),
            StageParams("vegetative", dap_target=30, kc=1.0, rue=1.3, lai_gain=0.13,
                        partition={"leaf": 0.50, "stem": 0.20, "root": 0.30, "storage": 0.0},
                        nuptake_target={"N": 25, "P": 8, "K": 25}),
            StageParams("flowering", dap_target=45, kc=1.1, rue=1.4, lai_gain=0.08,
                        partition={"leaf": 0.25, "stem": 0.20, "root": 0.10, "storage": 0.45},
                        nuptake_target={"N": 15, "P": 6, "K": 20}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def lentils_defaults() -> CropParams:
    return CropParams(
        species="lentils", cultivar="Local Lentil",
        tb=6.0, to=24.0, lai_max=3.0, hi=0.70,
        stress_sensitivity={"flower_water": 0.5, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("germination", dap_target=7, kc=0.5, rue=1.0, lai_gain=0.08,
                        partition={"leaf": 0.6, "stem": 0.2, "root": 0.2, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 12}),
            StageParams("vegetative", dap_target=25, kc=1.0, rue=1.3, lai_gain=0.13,
                        partition={"leaf": 0.50, "stem": 0.20, "root": 0.30, "storage": 0.0},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("flowering", dap_target=35, kc=1.1, rue=1.4, lai_gain=0.08,
                        partition={"leaf": 0.25, "stem": 0.20, "root": 0.10, "storage": 0.45},
                        nuptake_target={"N": 15, "P": 6, "K": 20}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def fava_beans_defaults() -> CropParams:
    return CropParams(
        species="fava beans", cultivar="Broad Bean",
        tb=8.0, to=25.0, lai_max=3.5, hi=0.65,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.45},
        stages=[
            StageParams("germination", dap_target=8, kc=0.5, rue=1.0, lai_gain=0.09,
                        partition={"leaf": 0.6, "stem": 0.2, "root": 0.2, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 12}),
            StageParams("vegetative", dap_target=30, kc=1.0, rue=1.3, lai_gain=0.13,
                        partition={"leaf": 0.50, "stem": 0.20, "root": 0.30, "storage": 0.0},
                        nuptake_target={"N": 25, "P": 8, "K": 25}),
            StageParams("flowering", dap_target=45, kc=1.1, rue=1.4, lai_gain=0.08,
                        partition={"leaf": 0.25, "stem": 0.20, "root": 0.10, "storage": 0.45},
                        nuptake_target={"N": 15, "P": 6, "K": 20}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

def mung_bean_defaults() -> CropParams:
    return CropParams(
        species="mung bean", cultivar="Vermic",
        tb=10.0, to=30.0, lai_max=3.0, hi=0.70,
        stress_sensitivity={"flower_water": 0.6, "grainfill_water": 0.5, "n": 0.4},
        stages=[
            StageParams("germination", dap_target=7, kc=0.5, rue=1.0, lai_gain=0.10,
                        partition={"leaf": 0.6, "stem": 0.2, "root": 0.2, "storage": 0.0},
                        nuptake_target={"N": 10, "P": 4, "K": 12}),
            StageParams("vegetative", dap_target=25, kc=1.0, rue=1.3, lai_gain=0.14,
                        partition={"leaf": 0.50, "stem": 0.20, "root": 0.30, "storage": 0.0},
                        nuptake_target={"N": 20, "P": 7, "K": 25}),
            StageParams("flowering", dap_target=35, kc=1.1, rue=1.4, lai_gain=0.08,
                        partition={"leaf": 0.25, "stem": 0.20, "root": 0.10, "storage": 0.45},
                        nuptake_target={"N": 15, "P": 6, "K": 20}),
            StageParams("maturity", kc=0.9, rue=0.8, lai_gain=0.00,
                        partition={"leaf": 0.0, "stem": 0.0, "root": 0.0, "storage": 1.0},
                        nuptake_target={"N": 0, "P": 0, "K": 0})
        ]
    )

# -------------------------------------------------------------------
# Crop selector
# -------------------------------------------------------------------

def get_crop_defaults(name: str) -> CropParams:
    name = name.lower().strip()
    crop_map = {
        # Cereals
        "maize": maize_defaults,
        "rice": rice_defaults,
        "sorghum": sorghum_defaults,
        # Root & Tuber
        "cassava": cassava_defaults,
        "yams": yams_defaults,
        # Vegetables
        "tomato": tomato_defaults,
        "pepper": pepper_defaults,
        "onion": onion_defaults,
        "garlic": garlic_defaults,
        "carrot": carrot_defaults,
        "spinach": spinach_defaults,
        "cucumber": cucumber_defaults,
        "broccoli": broccoli_defaults,
        "okra": okra_defaults,
        "cabbage": cabbage_defaults,
        "amaranth": amaranth_defaults,
        # Fruits
        "mango": mango_defaults,
        "apple": apple_defaults,
        "orange": orange_defaults,
        "banana": banana_defaults,
        "pineapple": pineapple_defaults,
        "guava": guava_defaults,
        "papaya": papaya_defaults,
        "lemon": lemon_defaults,
        "grapes": grapes_defaults,
        # Legumes
        "beans": beans_defaults,
        "cowpea": cowpea_defaults,
        "chickpea": chickpea_defaults,
        "lentils": lentils_defaults,
        "fava beans": fava_beans_defaults,
        "mung bean": mung_bean_defaults,
    }
    if name not in crop_map:
        valid = sorted(crop_map.keys())
        raise ValueError(f"Unsupported crop '{name}'. Supported: {valid}")
    return crop_map[name]()  # noqa: RET504
# (Built from the attached engine parameters.) :contentReference[oaicite:2]{index=2}

# -------------------------------------------------------------------
# Business baselines (from your pasted table)
# tpa = tonnes per acre; days = typical cycle duration (placeholder)
# -------------------------------------------------------------------
CROP_BASELINES = {
    "Maize": {"tpa": 3.5, "days": 110},
    "Rice": {"tpa": 2.8, "days": 120},
    "Sorghum": {"tpa": 2.2, "days": 100},
    "Cassava": {"tpa": 10.0, "days": 300},
    "Yams": {"tpa": 7.0, "days": 270},
    "Spinach": {"tpa": 8.0, "days": 45},
    "Cucumber": {"tpa": 6.0, "days": 55},
    "Broccoli": {"tpa": 4.0, "days": 70},
    "Tomato": {"tpa": 5.5, "days": 85},
    "Onion": {"tpa": 4.5, "days": 90},
    "Okra": {"tpa": 3.0, "days": 65},
    "Cabbage": {"tpa": 5.0, "days": 80},
    "Pepper": {"tpa": 3.8, "days": 90},
    "Amaranth": {"tpa": 7.0, "days": 40},
    "Mango": {"tpa": 4.0, "days": 365},
    "Apple": {"tpa": 3.5, "days": 365},
    "Orange": {"tpa": 4.2, "days": 365},
    "Banana": {"tpa": 12.0, "days": 365},
    "Pineapple": {"tpa": 10.0, "days": 450},
    "Guava": {"tpa": 6.0, "days": 365},
    "Papaya": {"tpa": 8.0, "days": 300},
    "Lemon": {"tpa": 4.0, "days": 365},
    "Grapes": {"tpa": 5.0, "days": 180},
    "Beans": {"tpa": 2.0, "days": 80},
    "Cowpea": {"tpa": 1.8, "days": 75},
    "Chickpea": {"tpa": 1.6, "days": 100},
    "Lentils": {"tpa": 1.5, "days": 100},
    "Fava Beans": {"tpa": 2.2, "days": 110},
    "Mung Bean": {"tpa": 1.5, "days": 70},
}

def list_supported_crops() -> list[str]:
    """Flattened crop name list for UI/API."""
    return [c for group in crop_categories.values() for c in group]

def get_baseline(crop: str) -> dict:
    """Return baseline tpa/days for a given crop (case-insensitive)."""
    key_map = {k.lower(): k for k in CROP_BASELINES.keys()}
    name = key_map.get(crop.lower())
    if not name:
        raise ValueError(f"Unsupported crop '{crop}'. Supported: {sorted(CROP_BASELINES.keys())}")
    return CROP_BASELINES[name]

# Public API of this module
__all__ = [
    "crop_categories",
    "get_crop_defaults",
    "CROP_BASELINES",
    "list_supported_crops",
    "get_baseline",
]
