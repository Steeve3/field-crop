# To-do

P0 = demo needs it · P1 = nice · P2 = only if ahead.
If behind, cut in this order: P2 → P1 → map click (keep presets only).
Never cut: S0 + alternatives, Evidence Cards, calendars, sliders, disclaimer.

## Together, first 45 min
- [x] P0 Repo, folders, AGENTS.md, requirements.txt
- [x] P0 3 Italian demo fields (see `data/fields.yaml`) — check the points and rotations
- [x] P0 Data shape the engine returns (see `engine/schema.py`) — read it together, change now if needed

## Dev A — engine
- [x] P0 `power.py`: fetch + cache + fallback; cache for the 3 demo fields
- [ ] P0 Review `crops.yaml` + `rotations.yaml` values (seeded, tagged SOURCE/ASSUMPTION)
- [ ] P0 `model.py`: water, yield, soil, profit, resilience + tests (more water never lowers yield, sane ranges)
- [ ] P0 `strategies.py`: S0 + 3 alternatives from priorities
- [ ] P0 `calendars.py`: bare-field months, vulnerability matrix
- [ ] P0 `explain.py`: Evidence Card (why, 3 evidence items with source, benefits, risks, gaps, needs local review, confidence)
- [ ] P0 `api.py`: wire everything in `analyze()`; then delete `sample.py`
- [ ] P1 Optional LLM rewrite of Evidence Card text
- [ ] P2 SoilGrids, MODIS NDVI, future climate scenarios

## Dev B — app + demo
- [x] P0 App skeleton running on SAMPLE data (map, presets, rotation input, sliders, cards, calendars)
- [ ] P0 Polish map: GIBS layer date, click a point → custom field
- [ ] P0 "What NASA data says" box (real POWER numbers already wired)
- [ ] P0 Strategy cards: chips, radar, changes vs S0, Evidence Card layout
- [ ] P0 Bare-field strip + vulnerability heatmap styling
- [ ] P0 What-if sliders + "ranking changed" message (needs engine)
- [ ] P0 Disclaimer banner (done in skeleton — keep it)
- [ ] P0 Deploy (Streamlit Community Cloud or Cloud Run)
- [ ] P1 "Learn" expander: ET, water balance, frost risk, cover crops, N-fixing crops
- [ ] P1 Data & methods expander
- [ ] P2 Italian translation, draw polygon

## Last 2 hours, together
- [ ] P0 Feature freeze; test the 3 fields with network off (cache works)
- [ ] P0 3-minute demo script, 2 rehearsals, backup video, submission text
