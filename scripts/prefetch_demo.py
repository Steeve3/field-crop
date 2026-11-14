"""Download and cache NASA POWER data for every demo field. Run before the demo."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine import config, power  # noqa: E402

if __name__ == "__main__":
    for fid, f in config.fields().items():
        daily, status = power.get_daily(f["lat"], f["lon"], use_cache=False)
        print(f"{fid}: {len(daily)} days ({status})")
