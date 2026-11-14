# FieldShift Advisor

NASA Space Apps Challenge 2026 — *Field Shift: Adapting Farms with NASA Data*.

A farmer picks a field, enters the current crop rotation, sets priorities (water,
soil, profit, climate resilience) and gets the current rotation compared with
3 alternatives, each explained with NASA POWER evidence, a bare-field calendar,
a vulnerability calendar and rainfall/temperature what-if sliders.

> This tool supports, and does not replace, your judgment and local agricultural expertise.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Test
```bash
pytest -q
```

## Layout
```
app.py              Streamlit UI (Dev B)
engine/             all logic (Dev A); the app only calls engine.analyze()
  schema.py         the shared data shape (agree before changing)
  sample.py         SAMPLE climate, crops, rotations — the only data used for now
  model.py          monthly water balance, soil cover, nitrogen, pest break, weather fit, scores
  api.py            analyze(): the one function the app calls
  power.py          NASA POWER fetch + disk cache (not used yet)
data/               crops.yaml, rotations.yaml, fields.yaml, cache/
scripts/            prefetch_demo.py
tests/
```

Rules for people and agents: [AGENTS.md](AGENTS.md). Task list: [TODO.md](TODO.md).
Ideas for later: [ideas.md](ideas.md).

## Data
- **NASA POWER** daily point data (community AG), 2005–2024: T2M, T2M_MAX, T2M_MIN,
  PRECTOTCORR, ALLSKY_SFC_SW_DWN, RH2M, WS2M. https://power.larc.nasa.gov
- **NASA GIBS** MODIS true-colour tiles on the map (visual only).
- Crop parameters: FAO-56 (crop coefficients) and FAO-33 (yield response); prices
  and costs are placeholders marked ASSUMPTION in `data/crops.yaml`.
