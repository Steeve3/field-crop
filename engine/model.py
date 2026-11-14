"""Monthly rotation model, ported from the Orbit Almanac prototype. Pure functions, no I/O.

1. Reference water demand per month: ET0 = 0.0135 (T + 17.8) Rs / 2.45 (Hargreaves radiation form),
   Rs estimated from the day-night temperature range (Hargreaves-Samani). SOURCE: FAO-56.
2. Each rotation is laid out month by month; crop demand = Kc(stage) x ET0.
3. A soil-water store fills with rain and empties with crop use; unmet demand is the water gap.
4. The same calendar gives bare months, rain on exposed soil, nitrogen, residue, crop families, heat/frost months.
5. Each indicator becomes a 0-100 score; scores are averaged with the farmer's priority weights.
"""
from __future__ import annotations

import math

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAYS = [31, 28.25, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
MID_DOY = [15, 46, 75, 106, 136, 167, 197, 228, 259, 289, 320, 350]

# ASSUMPTION: scales and thresholds below come from the Orbit Almanac prototype. Not validated.
BARE_EVAP_SHARE = 0.25            # bare soil evaporates this share of ET0
DORMANCY_T_C, DORMANCY_KC = 4, 0.4  # below this mean temperature Kc is capped (winter dormancy)
HIGH_RESIDUE_T_HA = 5             # residue above this protects bare soil
EXPOSURE = {"bare": 1.0, "bare_residue": 0.55, "sowing": 0.5, "crop": 0.1, "dense": 0.05}  # share of rain hitting soil
EXPOSED_SCALE = 0.6               # exposed-rain share at which the soil score reaches 0 (gentle slope)
N_SCALE_KG, RESIDUE_SCALE_T = 300, 10
REVENUE_SCALE, FORAGE_SCALE = 10, 0.5
HEAT_STAGE_FROM = 0.4             # heat only counts from this share of the crop cycle
HEAT_PENALTY, FROST_PENALTY = 18, 25
CLIMATE_WEIGHT = 2                # weather fit always counts with this weight
DRY_YEAR, WET_YEAR = 0.75, 1.20   # rain multipliers for the score range


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


def kc_at(crop: dict, j: int, length: int, t_mean: float) -> float:
    a, b, c = crop["kc"]
    f = (j + 0.5) / length
    if f < 0.2:
        k = a
    elif f < 0.45:
        k = a + (b - a) * (f - 0.2) / 0.25
    elif f < 0.8:
        k = b
    else:
        k = b + (c - b) * (f - 0.8) / 0.2
    return min(k, DORMANCY_KC) if t_mean < DORMANCY_T_C else k


def layout(rot: dict, crops: dict) -> list[dict | None]:
    """One cell per month of the rotation: None = bare, else the crop growing."""
    n = rot["years"] * 12
    cal: list[dict | None] = [None] * n
    for si, (cid, start, length) in enumerate(rot["segs"]):
        for j in range(length):
            cal[(start + j) % n] = {"id": cid, "crop": crops[cid], "j": j, "len": length, "seg": si}
    return cal


def _clamp(v: float) -> float:
    return max(0.0, min(100.0, v))


def evaluate(clim: dict, rot: dict, crops: dict, soil: dict, slope: dict, access: dict,
             rain_pct: float = 0.0, d_temp: float = 0.0) -> dict:
    c = climate_for(clim, rain_pct, d_temp)
    cal = layout(rot, crops)
    n, years, awc = len(cal), rot["years"], soil["awc"]

    # water store, three passes so it reaches a steady cycle
    store, gap = awc * 0.5, [0.0] * n
    for _ in range(3):
        for i, cell in enumerate(cal):
            m = i % 12
            store += c["P"][m] * slope["infil"]
            gap[i] = 0.0
            if cell:
                store -= kc_at(cell["crop"], cell["j"], cell["len"], c["T"][m]) * c["ET0"][m]
                if store < 0:
                    gap[i], store = -store, 0.0
            else:
                store -= min(store, BARE_EVAP_SHARE * c["ET0"][m])
            store = min(store, awc)
    water_gap = sum(gap) / years

    # soil cover
    rain = sum(c["P"])
    prev_res = next((cell["crop"]["res"] for cell in reversed(cal) if cell), 0)
    bare, exposed, bare_by_month = 0, 0.0, [0.0] * 12
    for i, cell in enumerate(cal):
        m = i % 12
        if not cell:
            bare += 1
            bare_by_month[m] += 1 / years
            x = EXPOSURE["bare_residue"] if prev_res >= HIGH_RESIDUE_T_HA else EXPOSURE["bare"]
        else:
            crop = cell["crop"]
            prev_res = crop["res"]
            dense = crop.get("perennial") or crop.get("is_cover")
            x = EXPOSURE["sowing"] if cell["j"] == 0 else EXPOSURE["dense"] if dense else EXPOSURE["crop"]
        exposed += x * c["P"][m]
    exposed_frac = exposed / years / rain if rain > 0 else 0.0

    # nitrogen, residue, forage, revenue
    need = credit = res = forage_m = income = 0.0
    for cid, _, length in rot["segs"]:
        crop = crops[cid]
        share = length / 12 if crop.get("perennial") else 1
        need += crop["n_need"]
        credit += crop["n_credit"]
        res += crop["res"] * share
        income += crop["income"] * share
        forage_m += crop["forage"] * length
    syn_n = max(0.0, need - credit) / years

    # pest break
    main = sorted((s for s in rot["segs"] if not crops[s[0]].get("is_cover")), key=lambda s: s[1])
    groups = [crops[s[0]]["group"] for s in main]
    repeats = sum(g == groups[(i + 1) % len(groups)] for i, g in enumerate(groups))
    counts: dict[str, int] = {}
    for s in main:
        counts[s[0]] = counts.get(s[0], 0) + 1
    min_return = min(years / k for k in counts.values())
    families = len({crops[s[0]]["group"] for s in rot["segs"]})
    pest = 100 * (0.4 * (1 - repeats / len(groups)) + 0.3 * min(1, (min_return - 1) / 2) + 0.3 * min(1, (families - 1) / 3))

    # weather fit
    flags = []
    for cid, start, length in rot["segs"]:
        crop, frost, heat = crops[cid], [], []
        for j in range(length):
            m = (start + j) % 12
            if c["Tn"][m] < crop["frost_t"]:
                frost.append(m)
            if (j + 0.5) / length >= HEAT_STAGE_FROM and c["Tx"][m] > crop["heat"]:
                heat.append(m)
        if frost:
            flags.append({"type": "frost", "crop": crop["name"], "months": frost})
        if heat:
            flags.append({"type": "heat", "crop": crop["name"], "months": heat})
    frost_n = sum(len(f["months"]) for f in flags if f["type"] == "frost") / years
    heat_n = sum(len(f["months"]) for f in flags if f["type"] == "heat") / years

    scores = {
        "water": _clamp(100 * (1 - water_gap / access["scale"])),
        "soil": _clamp(100 * (1 - exposed_frac * slope["erode"] / EXPOSED_SCALE)),
        "fert": (_clamp(100 * (1 - syn_n / N_SCALE_KG)) + _clamp(100 * res / years / RESIDUE_SCALE_T)) / 2,
        "pest": _clamp(pest),
        "income": _clamp(100 * income / years / REVENUE_SCALE),
        "forage": _clamp(100 * forage_m / n / FORAGE_SCALE),
        "climate": _clamp(100 - HEAT_PENALTY * heat_n - FROST_PENALTY * frost_n),
    }
    return {"cal": cal, "water_gap_mm": water_gap, "bare_months": bare / years, "bare_by_month": bare_by_month,
            "exposed_frac": exposed_frac, "syn_n_kg": syn_n, "residue_t": res / years,
            "heat_frost_months": heat_n + frost_n, "flags": flags, "scores": scores}


def total(scores: dict, weights: dict) -> float:
    num, den = CLIMATE_WEIGHT * scores["climate"], CLIMATE_WEIGHT
    for k, w in weights.items():
        num += w * scores[k]
        den += w
    return num / den


def rank(clim: dict, rotations: list[dict], crops: dict, soil: dict, slope: dict, access: dict,
         weights: dict, rain_pct: float = 0.0, d_temp: float = 0.0) -> list[dict]:
    """Score every rotation, plus a dry and a wet year for the range. Best first."""
    out = []
    for rot in rotations:
        run = lambda factor: evaluate(clim, rot, crops, soil, slope, access, (1 + rain_pct / 100) * factor * 100 - 100, d_temp)  # noqa: E731
        base, dry, wet = run(1.0), run(DRY_YEAR), run(WET_YEAR)
        lo, hi = sorted((total(dry["scores"], weights), total(wet["scores"], weights)))
        out.append({**{k: rot[k] for k in ("id", "name", "years", "why", "benefits", "gaps", "risks")},
                    "current": rot.get("current", False), **base,
                    "score": total(base["scores"], weights), "lo": lo, "hi": hi, "gap_dry_mm": dry["water_gap_mm"]})
    return sorted(out, key=lambda o: -o["score"])
