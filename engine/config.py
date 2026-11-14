"""Load the YAML files in data/ once."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load(name: str):
    return yaml.safe_load((DATA_DIR / name).read_text(encoding="utf-8"))


@lru_cache
def crops() -> dict[str, dict]:
    """Crop id -> parameters. The top-level non-crop keys (e.g. irrigation cost) are removed."""
    return {k: v for k, v in _load("crops.yaml").items() if isinstance(v, dict)}


@lru_cache
def irrigation_cost_eur_per_mm() -> float:
    return float(_load("crops.yaml")["irrigation_cost_eur_per_mm"])


@lru_cache
def rotations() -> list[dict]:
    return _load("rotations.yaml")


@lru_cache
def fields() -> dict[str, dict]:
    return _load("fields.yaml")
