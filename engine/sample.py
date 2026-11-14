"""SAMPLE data. No dataset is read yet: everything the app shows is computed from this block.

!!! Hand-entered, approximate values taken from the Orbit Almanac prototype. Not a NASA download,
not validated. Replace each block with real data (NASA POWER, the terrain notebook, local prices)
and delete this file when nothing uses it any more.
"""
from __future__ import annotations

SOURCE = "SAMPLE — hand-entered values, not a dataset"

# Monthly climate normals, Po Valley. T = mean, Tx = mean daily high, Tn = mean night low (°C), P = rain (mm).
CLIMATE = {
    "lat": 45.35,
    "T": [3.0, 4.9, 9.2, 13.3, 18.3, 22.2, 24.4, 23.9, 19.4, 14.2, 8.5, 3.8],
    "Tx": [6.7, 9.5, 14.3, 18.5, 23.7, 27.6, 30.0, 29.7, 25.0, 19.0, 12.2, 7.3],
    "Tn": [-0.6, 0.4, 4.2, 8.2, 13.0, 16.8, 18.9, 18.4, 14.3, 9.6, 4.9, 0.3],
    "P": [55, 50, 60, 75, 85, 85, 70, 75, 80, 90, 90, 60],
}

# kc = crop coefficients [initial, mid-season, end] (FAO-56 style). n_need / n_credit in kg N/ha.
# res = residue returned (t dry matter/ha). frost_t = lowest monthly mean night low tolerated (°C).
# heat = monthly mean daily high above which mid/late growth is stressed (°C).
# income = relative revenue index 0-5 (placeholder). forage 0-1.
CROPS = {
    "maize":   {"name": "Grain maize",       "short": "Maize",   "role": "cereal", "group": "warm-season grass",
                "kc": [0.3, 1.2, 0.5],    "n_need": 200, "n_credit": 0,   "res": 8,   "frost_t": 5,   "heat": 32, "forage": 0.2, "income": 4},
    "wheat":   {"name": "Winter wheat",      "short": "Wheat",   "role": "cereal", "group": "small grain",
                "kc": [0.5, 1.15, 0.3],   "n_need": 140, "n_credit": 0,   "res": 5,   "frost_t": -12, "heat": 30, "forage": 0.1, "income": 3},
    "barley":  {"name": "Winter barley",     "short": "Barley",  "role": "cereal", "group": "small grain",
                "kc": [0.4, 1.15, 0.25],  "n_need": 100, "n_credit": 0,   "res": 4,   "frost_t": -10, "heat": 30, "forage": 0.2, "income": 2.5},
    "sorghum": {"name": "Grain sorghum",     "short": "Sorghum", "role": "cereal", "group": "warm-season grass",
                "kc": [0.3, 1.05, 0.55],  "n_need": 110, "n_credit": 0,   "res": 6.5, "frost_t": 6,   "heat": 37, "forage": 0.3, "income": 3},
    "soy":     {"name": "Soybean",           "short": "Soy",     "role": "legume", "group": "legume",
                "kc": [0.4, 1.15, 0.5],   "n_need": 0,   "n_credit": 40,  "res": 3,   "frost_t": 5,   "heat": 34, "forage": 0.2, "income": 3.5},
    "alfalfa": {"name": "Alfalfa",           "short": "Alfalfa", "role": "cover",  "group": "perennial legume",
                "kc": [0.95, 0.95, 0.95], "n_need": 0,   "n_credit": 120, "res": 6,   "frost_t": -15, "heat": 36, "forage": 1,   "income": 3.5, "perennial": True},
    "cover":   {"name": "Rye + vetch cover", "short": "Cover",   "role": "cover",  "group": "mixed cover",
                "kc": [0.5, 0.85, 0.85],  "n_need": 0,   "n_credit": 50,  "res": 3,   "frost_t": -10, "heat": 99, "forage": 0.2, "income": 0,   "is_cover": True},
}

# Field inputs. awc = water the soil can hold for crops (mm). infil = share of rain that enters the soil.
# erode = erosion multiplier. scale = water gap (mm/yr) at which the water score reaches 0.
SOILS = {"sandy": {"label": "Sandy", "awc": 80}, "loam": {"label": "Loam", "awc": 150}, "clay": {"label": "Clay", "awc": 170}}
SLOPES = {"flat": {"label": "Flat", "infil": 0.9, "erode": 0.6}, "gentle": {"label": "Gentle", "infil": 0.85, "erode": 1.0},
          "steep": {"label": "Steep", "infil": 0.7, "erode": 1.5}}
ACCESS = {"rainfed": {"label": "Rain only", "scale": 250}, "limited": {"label": "Limited", "scale": 500},
          "full": {"label": "Full", "scale": 1500}}
DEFAULTS = {"soil": "loam", "slope": "flat", "access": "limited"}

# (id, label, short label)
CRITERIA = [
    ("water", "Save water", "Water"),
    ("soil", "Keep soil covered", "Soil cover"),
    ("fert", "Build fertility", "Fertility"),
    ("pest", "Break pest cycles", "Pest break"),
    ("income", "Revenue", "Revenue"),
    ("forage", "Forage", "Forage"),
]
PRESETS = {
    "balanced": {"label": "Balanced",     "w": {"water": 3, "soil": 3, "fert": 3, "pest": 3, "income": 3, "forage": 1}},
    "water":    {"label": "Water first",  "w": {"water": 5, "soil": 2, "fert": 2, "pest": 2, "income": 2, "forage": 0}},
    "soil":     {"label": "Soil builder", "w": {"water": 2, "soil": 5, "fert": 5, "pest": 3, "income": 1, "forage": 1}},
    "income":   {"label": "Revenue",      "w": {"water": 2, "soil": 1, "fert": 1, "pest": 2, "income": 5, "forage": 1}},
    "stock":    {"label": "Livestock",    "w": {"water": 2, "soil": 3, "fert": 3, "pest": 2, "income": 2, "forage": 5}},
}

# segs = [crop id, start month (0 = January of year 1), length in months].
ROTATIONS = [
    {"id": "r0", "name": "Continuous grain maize", "current": True, "years": 1, "segs": [["maize", 3, 6]],
     "why": "The rotation the field runs today. Every other option is measured against it.",
     "benefits": ["Simple to manage with existing machinery and contracts.", "High residue return from stalks."],
     "gaps": ["Actual yields and irrigation volumes for this field are not in the model."],
     "risks": ["Maize after maize builds up rootworm and stalk-borer pressure."]},
    {"id": "r1", "name": "Maize, soybean, winter wheat", "years": 3, "segs": [["maize", 3, 6], ["soy", 16, 5], ["wheat", 21, 9]],
     "why": "Two of the three crops need less summer water than maize, and wheat grows through the wet months.",
     "benefits": ["Soybean leaves nitrogen for the wheat.", "Three crop families break maize pest cycles.", "Wheat covers the soil from October to June."],
     "gaps": ["The gap after wheat harvest is still bare.", "Soybean and wheat prices are not modelled."],
     "risks": ["Harvest and sowing dates depend on local contractor availability."]},
    {"id": "r2", "name": "Three crops with winter cover", "years": 3,
     "segs": [["maize", 3, 6], ["cover", 9, 7], ["soy", 16, 5], ["wheat", 21, 9], ["cover", 31, 8]],
     "why": "Autumn and winter rain exceeds crop demand, so a cover crop can grow on water that would otherwise be lost.",
     "benefits": ["Soil is covered in almost every month.", "Vetch in the cover mix fixes nitrogen.", "Roots and residue add organic matter."],
     "gaps": ["Cover-crop growth is assumed, not measured.", "Seed and termination costs are not included."],
     "risks": ["A cover crop terminated late can dry the seedbed in a dry spring."]},
    {"id": "r3", "name": "Sorghum, barley, second-crop soybean", "years": 2,
     "segs": [["sorghum", 4, 5], ["barley", 9, 9], ["soy", 18, 4], ["cover", 22, 6]],
     "why": "For dry summers: sorghum tolerates heat and water shortage better than maize, and barley finishes before July.",
     "benefits": ["Lowest summer water demand.", "Three harvests in two years.", "Sorghum stays productive in heat that hurts maize."],
     "gaps": ["Second-crop soybean depends on July rain or irrigation.", "Local sorghum buyers are assumed to exist."],
     "risks": ["Sorghum markets are thinner than maize markets. Confirm a buyer first."]},
    {"id": "r4", "name": "Alfalfa ley, then maize and wheat", "years": 5,
     "segs": [["alfalfa", 2, 37], ["maize", 39, 6], ["wheat", 45, 9], ["cover", 55, 7]],
     "why": "For fields near livestock: three years of alfalfa rebuild soil structure and supply nitrogen to the maize.",
     "benefits": ["Soil undisturbed and covered for three years.", "Deep roots open compacted layers.", "Large nitrogen credit for the next maize."],
     "gaps": ["Alfalfa summer water shortfall is counted as lost yield, which may overstate it.", "Hay price is not modelled."],
     "risks": ["Needs a forage outlet.", "Needs mowing and baling equipment."]},
]
