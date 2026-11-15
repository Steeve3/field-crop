# AGENTS.md — rules for every coding agent (Claude Code, Copilot, others)

FieldShift Advisor: a Streamlit app for NASA Space Apps 2026, challenge
"Field Shift: Adapting Farms with NASA Data". 2 people, < 12 hours. Keep it simple.

## What we build
One page, layout after the Orbit Almanac prototype. It opens with three farmer buttons
(`sample.FARMERS`: name, area, bbox, crop file, sample climate). After a click the page shows
that farmer's field on the map, the best crops for the area (from the farmer's file in `data/`),
the climate record, priorities and what-if sliders, and the current rotation against alternatives.
Climate and rotations are SAMPLE data in `engine/sample.py`.

## Ownership (do not edit the other person's files)
| Area | Owner | Files |
|---|---|---|
| Engine | Dev A | `engine/`, `data/`, `tests/` |
| App & demo | Dev B | `app.py`, `ui/` (if created), `.streamlit/` |
| Shared contract | both, agree out loud first | `engine/schema.py` |

The app only calls `engine.analyze(...)` and reads the dict shape in
`engine/schema.py`. Never put model logic in `app.py`.

## Hard rules
1. **No invented numbers.** Every number shown to the user comes from the engine
   (computed from data) or from a CSV in `data/`. The only exception is
   `engine/sample.py`, which is clearly labelled SAMPLE and is replaced by real data later.
2. **Every number has a source.** Use the `Metric` shape (`value`, `unit`, `source`, `note`).
3. **Every default is tagged** with `# SOURCE: ...` or `# ASSUMPTION: ...`.
4. **Never crash on stage.** Read local files only during the demo; show `data_status` in the UI.
5. **Supportive tool.** The UI always shows: "This tool supports, and does not
   replace, your judgment and local agricultural expertise." Use hedged language
   ("may", "could", "under these assumptions"). No legal, subsidy, water-rights or
   chemical advice.
6. **Small commits, main always runs.** `streamlit run app.py` and `pytest` must pass.
7. **No secrets in the repo.** Use `.env` (git-ignored); see `.env.example`.
8. **New ideas** go into `ideas.md`, not into code, until all P0 tasks work.

## Commands
```bash
pip install -r requirements.txt
streamlit run app.py
pytest -q
```

## Adding a CSV
Copy the pattern of `engine/crop_scores.py`: put the file in `data/`, write one cached loader
in `engine/` that returns plain dicts with English names and units, export it in
`engine/__init__.py`, describe its shape in `engine/schema.py`, render it in `app.py`, add a test.

## Conventions
- Python 3.11+, type hints, plain functions, no classes unless needed.
- Units in names: `rain_mm`, `et0_mm`, `margin_eur_ha`, `yield_t_ha`.
- Months are 1–12 (calendar). Per-month arrays have 12 values, index 0 = January.
- English in code and UI.
