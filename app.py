"""FieldShift Advisor — Streamlit UI. Layout after the Orbit Almanac prototype. No model logic here."""
from __future__ import annotations

from html import escape

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from engine import analyze, crop_ranking, sample

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
TOP_CROPS = 10
DISCLAIMER = "This tool supports, and does not replace, your judgment and local agricultural expertise."
SATELLITE = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"

CSS = """<style>
.stMainBlockContainer{max-width:920px}
.eyebrow{font:11px ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase;color:#66756a;margin:0}
.badge{font:11px ui-monospace,monospace;border:1px solid #9a4a12;color:#9a4a12;border-radius:999px;padding:2px 10px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}
.tile{background:#f8faf6;border-radius:8px;padding:10px 12px}
.tile b{display:block;font:500 22px ui-monospace,monospace}
.tile span{font-size:12px;color:#435247}
.strip{display:grid;grid-template-columns:3em repeat(12,1fr);gap:2px;font:11px ui-monospace,monospace;text-align:center}
.strip div{padding:4px 0;border-radius:3px;background:#f8faf6}
.strip .l{background:none;text-align:left;color:#66756a}
.strip .heat{background:#fbd9cb}.strip .frost{background:#d3e4f8}
.rot-head{display:grid;grid-template-columns:auto 1fr auto;gap:10px;align-items:start}
.rank{font:12px ui-monospace,monospace;width:26px;height:26px;border-radius:50%;border:1px solid #cdd7cc;display:grid;place-items:center}
.rot-head h4{margin:0;padding:0;font-size:16px}
.tag{font-size:12px;color:#66756a}
.score{font:500 28px ui-monospace,monospace;line-height:1}
.score span{font-size:12px;color:#66756a}
.meter{position:relative;height:8px;border-radius:4px;background:#f8faf6;border:1px solid #cdd7cc;margin:10px 0 2px}
.meter i{position:absolute;inset:0 auto 0 0;background:#1f5c3a;border-radius:3px 0 0 3px}
.meter u{position:absolute;top:-4px;bottom:-4px;border-left:2px solid #152018;border-right:2px solid #152018}
.small{font-size:12px;color:#66756a;margin:0}
.why{font-size:14px;color:#435247;margin:8px 0}
.cal-row{display:grid;grid-template-columns:2.2em repeat(12,minmax(0,1fr));gap:2px;margin-bottom:2px;font:10.5px ui-monospace,monospace;color:#66756a;text-align:center}
.blk{height:22px;border-radius:4px;padding:0 4px;overflow:hidden;white-space:nowrap;text-align:left;line-height:22px;font-weight:500}
.cereal{background:#eda100;color:#1b1400}.legume{background:#1baf7a;color:#04180f}
.cover{background:#6250d6;color:#fff}.other{background:#435247;color:#fff}
.bare{background:repeating-linear-gradient(135deg,transparent 0 4px,#cdd7cc 4px 6px);border:1px solid #cdd7cc}
.legend{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:12px;color:#435247}
.legend i{display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-2px;margin-right:5px}
.keys{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:10px 0}
.keys b{display:block;font:500 16px ui-monospace,monospace}
.keys span{display:block;font-size:11.5px;color:#66756a}
.bars{display:grid;grid-template-columns:auto 1fr 2em;gap:4px 10px;align-items:center;font-size:12.5px}
.bars .t{height:6px;border-radius:3px;background:#f8faf6;overflow:hidden}
.bars .t i{display:block;height:100%;background:#1f5c3a}
.bars .v{font-family:ui-monospace,monospace;text-align:right}
.flag{display:inline-block;font-size:12px;border-radius:4px;padding:2px 8px;margin:8px 6px 0 0;background:#f8faf6}
.flag.heat{background:#fbd9cb}.flag.frost{background:#d3e4f8}
</style>"""


def month_runs(flags: list[bool]) -> str:
    """[F,T,T,F,...] -> 'Feb to Mar'. Wraps around the year."""
    if all(flags):
        return "all year"
    start = flags.index(False)
    runs, m, n = [], start, 0
    for k in range(1, 13):
        i = (start + k) % 12
        if flags[i]:
            m, n = (i if n == 0 else m), n + 1
        elif n:
            runs.append(MONTHS[m] if n == 1 else f"{MONTHS[m]} to {MONTHS[(m + n - 1) % 12]}")
            n = 0
    return ", ".join(runs)


def delta(v: float, base: float, unit: str) -> str:
    d = v - base
    return "same as current" if abs(d) < 0.05 else f"{d:+.0f} {unit} vs current" if abs(d) >= 1 else f"{d:+.1f} {unit} vs current"


def calendar_html(o: dict) -> str:
    rows = ['<div class="cal-row"><span></span>' + "".join(f"<span>{m[0]}</span>" for m in MONTHS) + "</div>"]
    for y in range(o["years"]):
        cells, blocks, m = o["cal"][y * 12:(y + 1) * 12], [], 0
        while m < 12:
            seg = cells[m]["seg"] if cells[m] else None
            n = 1
            while m + n < 12 and (cells[m + n]["seg"] if cells[m + n] else None) == seg:
                n += 1
            crop = cells[m]["crop"] if cells[m] else None
            cls, text = (crop["role"], escape(crop["short"])) if crop else ("bare", "")
            blocks.append(f'<div class="blk {cls}" style="grid-column:span {n}">{text}</div>')
            m += n
        rows.append(f'<div class="cal-row"><span>Y{y + 1}</span>{"".join(blocks)}</div>')
    return "".join(rows)


def card_html(o: dict, cur: dict, pos: int) -> str:
    tag = "Current rotation" if o["current"] else f"{o['years']}-year cycle"
    d = (lambda v, b, u: "") if o["current"] else (lambda v, b, u: f"<span>{delta(v, b, u)}</span>")
    bars = "".join(
        f'<span>{label}</span><span class="t"><i style="width:{o["scores"][k]:.0f}%"></i></span><span class="v">{o["scores"][k]:.0f}</span>'
        for k, label in [(c[0], c[2]) for c in sample.CRITERIA] + [("climate", "Weather fit")])
    flags = "".join(
        f'<span class="flag {f["type"]}">{f["type"].title()}: {escape(f["crop"])}, {", ".join(MONTHS[m] for m in f["months"])}</span>'
        for f in o["flags"]) or '<span class="flag">No frost or heat flags</span>'
    return f"""
<div class="rot-head"><div class="rank">{pos}</div>
  <div><h4>{escape(o["name"])}</h4><div class="tag">{tag}</div></div>
  <div class="score">{o["score"]:.0f}<span>/100</span></div></div>
<div class="meter"><i style="width:{o["score"]:.0f}%"></i><u style="left:{o["lo"]:.0f}%;width:{max(o["hi"] - o["lo"], 1):.0f}%"></u></div>
<p class="small">Dry to wet year: {o["lo"]:.0f} to {o["hi"]:.0f}</p>
{calendar_html(o)}
<div class="keys">
  <div><b>{o["water_gap_mm"]:.0f} mm</b><span>water gap per year</span>{d(o["water_gap_mm"], cur["water_gap_mm"], "mm")}</div>
  <div><b>{o["bare_months"]:.1f}</b><span>bare months per year</span>{d(o["bare_months"], cur["bare_months"], "mo")}</div>
  <div><b>{o["syn_n_kg"]:.0f} kg</b><span>fertiliser N per ha</span>{d(o["syn_n_kg"], cur["syn_n_kg"], "kg")}</div>
</div>
<div class="bars">{bars}</div>
<div>{flags}</div>"""


st.set_page_config(page_title="FieldShift Advisor", page_icon="🌾", layout="centered")
st.html(CSS)
st.html('<p class="eyebrow">NASA Space Apps 2026 · crop rotation · <span class="badge">SAMPLE DATA</span></p>')
st.title("FieldShift Advisor")
st.caption(DISCLAIMER)

# ---------------- Who are you ----------------
for col, f in zip(st.columns(len(sample.FARMERS)), sample.FARMERS):
    chosen = st.session_state.get("farmer") == f["id"]
    if col.button(f"**{f['name']}** · {f['area']}", key=f"farmer_{f['id']}",
                  type="primary" if chosen else "secondary", use_container_width=True):
        st.session_state["farmer"] = f["id"]
        st.rerun()
if "farmer" not in st.session_state:
    st.caption("Choose a farmer to open their field.")
    st.stop()
farmer = sample.FARMER[st.session_state["farmer"]]

# ---------------- The field ----------------
st.subheader(f"The field of {farmer['name']}, {farmer['area']}")
lon0, lat0, lon1, lat1 = farmer["bbox"]
fmap = folium.Map(tiles=SATELLITE, attr="Esri World Imagery", scrollWheelZoom=False)  # page scroll must not zoom
folium.Rectangle([[lat0, lon0], [lat1, lon1]], color="#ffffff", weight=3, fill=True, fill_color="#eda100",
                 fill_opacity=0.25).add_to(fmap)
fmap.fit_bounds([[lat0, lon0], [lat1, lon1]])
st_folium(fmap, height=360, use_container_width=True, key=f"map_{farmer['id']}", returned_objects=[])

cols = st.columns(3)
settings = {}
for col, (key, label, opts) in zip(cols, [("soil", "Soil texture", sample.SOILS), ("slope", "Slope", sample.SLOPES),
                                          ("access", "Water access", sample.ACCESS)]):
    default = farmer["defaults"][key]
    settings[key] = col.segmented_control(label, list(opts), default=default, key=f"{key}_{farmer['id']}",
                                          format_func=lambda k, o=opts: o[k]["label"]) or default

# ---------------- Best crops for this region ----------------
st.subheader("Best crops for this area")
ranking = crop_ranking(farmer["id"])
crop_rows = pd.DataFrame([{"#": c["rank"], "Crop": c["name"], "Final score": c["score_pct"], "Notes": c["note"]}
                          for c in ranking["crops"][:TOP_CROPS]])
st.dataframe(crop_rows, hide_index=True, width="stretch", column_config={
    "#": st.column_config.NumberColumn(width="small"),
    "Final score": st.column_config.ProgressColumn(format="%.1f%%", min_value=0, width="medium",
                                                   max_value=100),
    "Notes": st.column_config.TextColumn(width="large")})
st.caption(f"Source: {ranking['source']}.")

climate_box = st.container()

# ---------------- What matters to you ----------------
st.subheader("What matters to you")
preset = st.segmented_control("Priorities", list(sample.PRESETS), default="balanced", label_visibility="collapsed",
                              format_func=lambda k: sample.PRESETS[k]["label"]) or "balanced"
with st.expander("Fine-tune each priority"):
    wcols = st.columns(3)
    weights = {cid: wcols[i % 3].slider(label, 0, 5, sample.PRESETS[preset]["w"][cid], key=f"w_{preset}_{cid}")
               for i, (cid, label, _) in enumerate(sample.CRITERIA)}
s1, s2 = st.columns(2)
rain_pct = s1.slider("What if rainfall changes (%)", -40, 20, 0, step=5)
temp_delta = s2.slider("What if it gets warmer (°C)", 0.0, 4.0, 0.0, step=0.5)

result = analyze(farmer["id"], settings["soil"], settings["slope"], settings["access"], weights, rain_pct, temp_delta)
clim, options = result["climate"], result["options"]
current = next(o for o in options if o["current"])

# ---------------- What the climate record says ----------------
with climate_box:
    st.subheader("What the climate record says")
    tiles = [(f"{clim['rain_mm']:.0f} mm", "rain per year"), (f"{clim['et0_mm']:.0f} mm", "reference water demand per year"),
             (f"{sum(clim['short'])} of 12", "months when demand exceeds rain"),
             (f"{sum(clim['frost'])}", "months with frost-prone nights")]
    st.html('<div class="tiles">' + "".join(f'<div class="tile"><b>{v}</b><span>{t}</span></div>' for v, t in tiles) + "</div>")

    bare = [v >= 0.5 for v in current["bare_by_month"]]
    fig = go.Figure()
    fig.add_bar(x=MONTHS, y=clim["P"], name="Rain, mm", marker_color="#2a78d6")
    fig.add_scatter(x=MONTHS, y=clim["ET0"], name="Water demand, mm", line=dict(color="#eb6834", width=3))
    for m, is_bare in enumerate(bare):
        if is_bare:
            fig.add_vrect(x0=m - 0.5, x1=m + 0.5, fillcolor="#66756a", opacity=0.12, line_width=0)
    fig.update_layout(height=240, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", y=1.2),
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(gridcolor="#cdd7cc"))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    strip = '<div class="l"></div>' + "".join(f'<div class="l" style="text-align:center">{m[0]}</div>' for m in MONTHS)
    strip += '<div class="l">High</div>' + "".join(f'<div class="{"heat" if h else ""}">{t:.0f}</div>' for t, h in zip(clim["Tx"], clim["heat"]))
    strip += '<div class="l">Low</div>' + "".join(f'<div class="{"frost" if f else ""}">{t:.0f}</div>' for t, f in zip(clim["Tn"], clim["frost"]))
    st.html(f'<div class="strip">{strip}</div>')
    st.caption("°C. Shaded: high above 32 °C, night low below 1 °C. Grey bands in the chart: field bare in the current rotation.")

    finds = [f"**Water:** demand exceeds rain {month_runs(clim['short'])}, by {clim['deficit_mm']:.0f} mm in total."
             if any(clim["short"]) else "**Water:** rain exceeds demand in every month."]
    if any(bare):
        wet = sum(p for p, b in zip(clim["P"], bare) if b)
        finds.append(f"**Bare field:** no crop {month_runs(bare)}. {wet:.0f} mm of rain "
                     f"({100 * wet / clim['rain_mm']:.0f}% of the year) falls then.")
    st.markdown("\n".join(f"- {f}" for f in finds))

# ---------------- Rotation options ----------------
st.subheader("Rotation options, ranked for this field")
best, pos = options[0], options.index(current) + 1
st.caption(f"Your current rotation ranks {pos} of {len(options)}. "
           + (f"The top alternative scores {best['score'] - current['score']:.0f} points higher." if best is not current
              else "No alternative scores higher."))
st.html('<div class="legend"><span><i style="background:#eda100"></i>Cereal</span>'
        '<span><i style="background:#1baf7a"></i>Legume</span><span><i style="background:#6250d6"></i>Cover or forage</span>'
        '<span><i class="bare"></i>Bare soil</span></div>')
rcols = st.columns(2)
for i, o in enumerate(options):
    with rcols[i % 2].container(border=True):
        st.html(card_html(o, current, i + 1))

# ---------------- Side by side ----------------
st.subheader("Side by side")
st.dataframe(pd.DataFrame([{
    "Rotation": o["name"] + (" (current)" if o["current"] else ""),
    "Score": round(o["score"]),
    "Water gap, mm": round(o["water_gap_mm"]),
    "Gap in a dry year, mm": round(o["gap_dry_mm"]),
    "Bare months": round(o["bare_months"], 1),
    "Rain on exposed soil, %": round(100 * o["exposed_frac"]),
    "Fertiliser N, kg/ha": round(o["syn_n_kg"]),
    "Residue, t/ha": round(o["residue_t"], 1),
    "Heat or frost months": round(o["heat_frost_months"], 1),
} for o in options]), hide_index=True, width="stretch")
st.caption("Water gap: crop demand that rain and stored soil water do not cover. Revenue is a placeholder index.")

# ---------------- How it works ----------------
st.subheader("How it works")
with st.expander("What is real and what is sample"):
    st.markdown(
        "- **Sample:** the farmers, their climate and the rotations are hand-entered values, not a dataset.\n"
        "- **From data:** the best-crops table is read from the file of each area.\n"
        "- **Computed:** monthly water balance, soil cover, nitrogen, pest break and weather fit, weighted by your priorities.\n"
        "- **Not validated:** nothing here was checked against field records or by an agronomist.")
with st.expander("Terms"):
    st.markdown(
        "- **Reference water demand:** water a well-watered grass surface would use (evapotranspiration).\n"
        "- **Water gap:** crop demand left unmet by rain and soil water.\n"
        "- **Cover crop:** grown to protect and feed the soil between cash crops, not for harvest.\n"
        "- **Nitrogen fixing:** legumes turn nitrogen from air into a form plants use.")
st.caption(DISCLAIMER)
