"""NASA POWER daily point data: fetch, cache to disk, fall back to cache.

Docs: https://power.larc.nasa.gov/docs/services/api/temporal/daily/
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
PARAMETERS = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN", "RH2M", "WS2M"]
START_YEAR = 2005
END_YEAR = 2024
CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "cache"
TIMEOUT_S = 60
FILL_VALUE = -999.0
SOURCE = f"NASA POWER daily (AG community), {START_YEAR}-{END_YEAR}"

# Readable column names used by the rest of the engine.
COLUMNS = {
    "T2M": "tmean_c",
    "T2M_MAX": "tmax_c",
    "T2M_MIN": "tmin_c",
    "PRECTOTCORR": "rain_mm",
    "ALLSKY_SFC_SW_DWN": "rad_mj_m2",   # MJ/m2/day for the AG community
    "RH2M": "rh_pct",
    "WS2M": "wind_m_s",
}


def _cache_path(lat: float, lon: float) -> Path:
    return CACHE_DIR / f"power_{lat:.2f}_{lon:.2f}_{START_YEAR}_{END_YEAR}.json"


def _download(lat: float, lon: float) -> dict:
    params = {
        "parameters": ",".join(PARAMETERS),
        "community": "AG",
        "latitude": round(lat, 4),
        "longitude": round(lon, 4),
        "start": f"{START_YEAR}0101",
        "end": f"{END_YEAR}1231",
        "format": "JSON",
    }
    resp = requests.get(API_URL, params=params, timeout=TIMEOUT_S)
    resp.raise_for_status()
    return resp.json()


def parse(raw: dict) -> pd.DataFrame:
    """POWER JSON -> daily DataFrame indexed by date, readable column names, NaN for gaps."""
    param = raw["properties"]["parameter"]
    df = pd.DataFrame({COLUMNS.get(k, k): v for k, v in param.items()})
    df.index = pd.to_datetime(df.index, format="%Y%m%d")
    df.index.name = "date"
    return df.replace(FILL_VALUE, float("nan")).sort_index()


def get_daily(lat: float, lon: float, *, use_cache: bool = True) -> tuple[pd.DataFrame, str]:
    """Return (daily weather, status) where status is "cached" or "live".

    Order: disk cache -> live download (then saved to cache).
    Raises RuntimeError with a readable message if both fail.
    """
    path = _cache_path(lat, lon)
    if use_cache and path.exists():
        return parse(json.loads(path.read_text(encoding="utf-8"))), "cached"
    try:
        raw = _download(lat, lon)
    except requests.RequestException as exc:
        if path.exists():
            return parse(json.loads(path.read_text(encoding="utf-8"))), "cached"
        raise RuntimeError(f"NASA POWER is not reachable and there is no cached data for this point: {exc}") from exc
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(raw), encoding="utf-8")
    return parse(raw), "live"


def climate_summary(daily: pd.DataFrame) -> dict[str, dict]:
    """Simple yearly climate facts straight from POWER (no model). Returns Metric dicts."""
    years = daily.index.year.nunique()
    yearly_rain = daily["rain_mm"].groupby(daily.index.year).sum()
    monthly_rain = daily["rain_mm"].groupby([daily.index.year, daily.index.month]).sum()
    dry_months = (monthly_rain < 10).groupby(level=0).sum()  # months with < 10 mm rain

    def m(value: float, unit: str, note: str) -> dict:
        return {"value": round(float(value), 1), "unit": unit, "source": SOURCE, "note": note}

    return {
        "rain_mm": m(yearly_rain.mean(), "mm/yr", "Average yearly rainfall"),
        "rain_driest_year_mm": m(yearly_rain.min(), "mm/yr", f"Driest year: {int(yearly_rain.idxmin())}"),
        "tmean_c": m(daily["tmean_c"].mean(), "°C", "Average air temperature"),
        "heat_days": m((daily["tmax_c"] > 32).sum() / years, "days/yr", "Days with maximum above 32 °C"),
        "frost_days": m((daily["tmin_c"] < 0).sum() / years, "days/yr", "Days with minimum below 0 °C"),
        "dry_months": m(dry_months.mean(), "months/yr", "Months with less than 10 mm of rain"),
    }
