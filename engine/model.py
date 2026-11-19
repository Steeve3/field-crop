"""Climate helper for the climate record on the page: reference water demand (ET0) per month.

ET0 = 0.0135 (T + 17.8) Rs / 2.45 (Hargreaves radiation form), with Rs estimated from the
day-night temperature range (Hargreaves-Samani). SOURCE: FAO-56. The rotation results are not
computed here: they are static, see engine/results.py.
"""
from __future__ import annotations

import math

DAYS = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MID_DOY = [15, 46, 75, 106, 136, 167, 197, 228, 259, 289, 320, 350]


def extra_rad(lat_deg: float, doy: int) -> float:
    """Extraterrestrial radiation, MJ/m2/day. SOURCE: FAO-56 eq. 21."""
    phi = math.radians(lat_deg)
    dr = 1 + 0.033 * math.cos(2 * math.pi * doy / 365)
    d = 0.409 * math.sin(2 * math.pi * doy / 365 - 1.39)
    ws = math.acos(max(-1, min(1, -math.tan(phi) * math.tan(d))))
    return (24 * 60 / math.pi) * 0.0820 * dr * (ws * math.sin(phi) * math.sin(d) + math.cos(phi) * math.cos(d) * math.sin(ws))


def climate_for(clim: dict, rain_pct: float = 0.0, d_temp: float = 0.0) -> dict:
    """Apply the what-if scenario and add ET0 (mm/month)."""
    t = [v + d_temp for v in clim["T"]]
    tx = [v + d_temp for v in clim["Tx"]]
    tn = [v + d_temp for v in clim["Tn"]]
    p = [v * (1 + rain_pct / 100) for v in clim["P"]]
    et0 = []
    for m in range(12):
        rs = 0.16 * math.sqrt(max(tx[m] - tn[m], 1)) * extra_rad(clim["lat"], MID_DOY[m])
        et0.append(max(0.0, 0.0135 * (t[m] + 17.8) * rs / 2.45) * DAYS[m])
    return {"T": t, "Tx": tx, "Tn": tn, "P": p, "ET0": et0}
