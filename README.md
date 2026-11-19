# FieldShift Advisor

NASA Space Apps Challenge 2026 — *Field Shift: Adapting Farms with NASA Data*.

The farmer draws a field, sets soil, slope, water access and priorities, and compares
the current crop rotation with four optimised strategies (balanced, water saving, economic return, soil health). A table shows the best crops for a region.

> This tool supports, and does not replace, your judgment and local agricultural expertise.

## Run
```bash
pip install -r requirements.txt
streamlit run app.py
pytest -q
```

## Layout
```
app.py                the page (Streamlit); calls only engine.analyze() and engine.crop_ranking()
engine/
  api.py              analyze(): static rotation results; the farmer's preference selects the matching strategy
  results.py          STATIC optimisation results: 4 strategies + current rotation (water, revenue, soil)
  model.py            climate helper (ET0) for the climate record
  sample.py           SAMPLE farmers, climate, field labels, priority presets
  crop_scores.py      crop_ranking(): reads data/score_colture.csv
  schema.py           data shapes returned to the page
data/
  score_colture.csv   crop suitability for a fixed region (terrain notebook output)
  toscana_*.csv       per-cell Tuscany data, not used yet
tests/
```

Rules for people and agents: [AGENTS.md](AGENTS.md). Tasks: [TODO.md](TODO.md). Ideas: [ideas.md](ideas.md).
