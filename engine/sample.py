"""SAMPLE data. No dataset is read yet: everything the app shows is computed from this block.

!!! Hand-entered, approximate values taken from the Orbit Almanac prototype. Not a NASA download,
not validated. Replace each block with real data (NASA POWER, the terrain notebook, local prices)
and delete this file when nothing uses it any more.
"""
from __future__ import annotations

SOURCE = "SAMPLE — hand-entered values, not a dataset"

# Three demo farmers (fictional names), one field area each. bbox = lon_min, lat_min, lon_max, lat_max.
# crops_csv = crop ranking for that area in data/ (output of the terrain notebook).
# defaults = starting soil / slope / water access. ASSUMPTION, to be confirmed by the farmer.
# terrain = SAMPLE share of the area (0-1) at risk of erosion, waterlogging and summer drought.
#   The terrain notebook measures these from NASADEM + HLS; here they are assumed, and only
#   scripts/build_crop_tables.py uses them to build the placeholder crop tables.
# climate = SAMPLE monthly normals, hand-entered and approximate: T = mean, Tx = mean daily high,
# Tn = mean night low (°C), P = rain (mm).
FARMERS = [
    {"id": "asciano", "name": "Giulia Bianchi", "area": "Asciano", "bbox": (11.564102, 43.215159, 11.571898, 43.220841),
     "crops_csv": "score_asciano.csv", "defaults": {"soil": "clay", "slope": "gentle", "access": "rainfed"},
     "terrain": {"erosion": 0.45, "waterlogging": 0.05, "drought": 0.35},   # clay hills
     "climate": {"lat": 43.21,
                 "T": [5.6, 6.4, 9.3, 12.5, 17.0, 21.2, 24.3, 24.2, 20.0, 15.3, 10.0, 6.4],
                 "Tx": [9.8, 11.2, 14.8, 18.3, 23.3, 27.9, 31.4, 31.3, 26.2, 20.5, 14.3, 10.4],
                 "Tn": [1.6, 1.9, 4.2, 6.9, 10.9, 14.6, 17.2, 17.3, 14.1, 10.5, 6.0, 2.7],
                 "P": [55, 55, 55, 65, 60, 50, 30, 45, 70, 90, 100, 70]}},
    {"id": "mugello", "name": "Marco Rossi", "area": "Mugello", "bbox": (11.381053, 43.965159, 11.388947, 43.970841),
     "crops_csv": "score_mugello.csv", "defaults": {"soil": "loam", "slope": "gentle", "access": "limited"},
     "terrain": {"erosion": 0.35, "waterlogging": 0.20, "drought": 0.10},   # wet mountain valley
     "climate": {"lat": 43.99,
                 "T": [4.0, 5.2, 8.5, 11.8, 16.3, 20.3, 23.2, 23.0, 18.9, 14.2, 8.8, 4.8],
                 "Tx": [8.5, 10.4, 14.5, 18.2, 23.2, 27.5, 31.0, 30.9, 25.8, 19.8, 13.2, 9.0],
                 "Tn": [-0.3, 0.3, 2.8, 5.6, 9.6, 13.2, 15.5, 15.4, 12.3, 8.8, 4.6, 0.8],
                 "P": [90, 85, 85, 95, 80, 60, 40, 55, 90, 125, 140, 105]}},
    {"id": "val_di_chiana", "name": "Elena Conti", "area": "Val di Chiana", "bbox": (11.801100, 43.247159, 11.808900, 43.252841),
     "crops_csv": "score_val_di_chiana.csv", "defaults": {"soil": "loam", "slope": "flat", "access": "limited"},
     "terrain": {"erosion": 0.05, "waterlogging": 0.30, "drought": 0.25},   # flat reclaimed plain
     "climate": {"lat": 43.27,
                 "T": [5.2, 6.3, 9.5, 12.8, 17.4, 21.6, 24.6, 24.4, 20.1, 15.2, 9.8, 5.9],
                 "Tx": [9.6, 11.5, 15.4, 19.0, 24.2, 28.8, 32.4, 32.2, 26.8, 20.6, 14.2, 10.0],
                 "Tn": [1.0, 1.4, 3.8, 6.7, 10.8, 14.5, 16.9, 16.8, 13.6, 10.0, 5.6, 2.0],
                 "P": [50, 50, 50, 60, 60, 50, 30, 40, 65, 85, 90, 65]}},
]
FARMER = {f["id"]: f for f in FARMERS}

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
