"""SAMPLE data for the farmers: names, field areas, starting field settings and monthly climate.

!!! Hand-entered, approximate values. Not a NASA download, not validated. The rotation results
are separate: engine/results.py. Replace the climate with real data when it is available.
"""
from __future__ import annotations

SOURCE = "SAMPLE — hand-entered values, not a dataset"

# Three demo farmers (fictional names), one field area each. bbox = lon_min, lat_min, lon_max, lat_max.
# crops_csv = crop ranking for that area in data/ (output of the terrain notebook).
# defaults = starting soil / slope / water access. ASSUMPTION, to be confirmed by the farmer.
# climate = SAMPLE monthly normals, hand-entered and approximate: T = mean, Tx = mean daily high,
# Tn = mean night low (°C), P = rain (mm).
FARMERS = [
    {"id": "asciano", "name": "Giulia Bianchi", "area": "Asciano", "bbox": (11.564102, 43.215159, 11.571898, 43.220841),
     "crops_csv": "risultato_asciano.csv", "defaults": {"soil": "clay", "slope": "gentle", "access": "rainfed"},
     "climate": {"lat": 43.21,
                 "T": [5.6, 6.4, 9.3, 12.5, 17.0, 21.2, 24.3, 24.2, 20.0, 15.3, 10.0, 6.4],
                 "Tx": [9.8, 11.2, 14.8, 18.3, 23.3, 27.9, 31.4, 31.3, 26.2, 20.5, 14.3, 10.4],
                 "Tn": [1.6, 1.9, 4.2, 6.9, 10.9, 14.6, 17.2, 17.3, 14.1, 10.5, 6.0, 2.7],
                 "P": [55, 55, 55, 65, 60, 50, 30, 45, 70, 90, 100, 70]}},
    {"id": "mugello", "name": "Marco Rossi", "area": "Mugello", "bbox": (11.381053, 43.965159, 11.388947, 43.970841),
     "crops_csv": "risultato_mugello.csv", "defaults": {"soil": "loam", "slope": "gentle", "access": "limited"},
     "climate": {"lat": 43.99,
                 "T": [4.0, 5.2, 8.5, 11.8, 16.3, 20.3, 23.2, 23.0, 18.9, 14.2, 8.8, 4.8],
                 "Tx": [8.5, 10.4, 14.5, 18.2, 23.2, 27.5, 31.0, 30.9, 25.8, 19.8, 13.2, 9.0],
                 "Tn": [-0.3, 0.3, 2.8, 5.6, 9.6, 13.2, 15.5, 15.4, 12.3, 8.8, 4.6, 0.8],
                 "P": [90, 85, 85, 95, 80, 60, 40, 55, 90, 125, 140, 105]}},
    {"id": "val_di_chiana", "name": "Elena Conti", "area": "Val di Chiana", "bbox": (11.801100, 43.247159, 11.808900, 43.252841),
     "crops_csv": "risultato_chiana.csv", "defaults": {"soil": "loam", "slope": "flat", "access": "limited"},
     "climate": {"lat": 43.27,
                 "T": [5.2, 6.3, 9.5, 12.8, 17.4, 21.6, 24.6, 24.4, 20.1, 15.2, 9.8, 5.9],
                 "Tx": [9.6, 11.5, 15.4, 19.0, 24.2, 28.8, 32.4, 32.2, 26.8, 20.6, 14.2, 10.0],
                 "Tn": [1.0, 1.4, 3.8, 6.7, 10.8, 14.5, 16.9, 16.8, 13.6, 10.0, 5.6, 2.0],
                 "P": [50, 50, 50, 60, 60, 50, 30, 40, 65, 85, 90, 65]}},
]
FARMER = {f["id"]: f for f in FARMERS}

# Field inputs shown on the page. They do not change the rotation results yet (those are static).
SOILS = {"sandy": {"label": "Sandy"}, "loam": {"label": "Loam"}, "clay": {"label": "Clay"}}
SLOPES = {"flat": {"label": "Flat"}, "gentle": {"label": "Gentle"}, "steep": {"label": "Steep"}}
ACCESS = {"rainfed": {"label": "Rain only"}, "limited": {"label": "Limited"}, "full": {"label": "Full"}}

# The three objectives of the optimisation model. (id, label on the card bars)
CRITERIA = [
    ("water", "Water"),
    ("revenue", "Revenue"),
    ("soil", "Soil health"),
]
# What matters to you: each preference shows the matching optimised strategy (ids in engine/results.py).
PRESETS = {
    "balanced": {"label": "Balanced",      "strategy": "balanced"},
    "water":    {"label": "Water first",   "strategy": "water_saving"},
    "revenue":  {"label": "Revenue first", "strategy": "economic_return"},
    "soil":     {"label": "Soil first",    "strategy": "soil_health"},
}
