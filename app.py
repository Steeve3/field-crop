"""FieldShift Advisor — Streamlit UI (Dev B). Only calls engine.analyze(); no model logic here."""
from __future__ import annotations

import folium
import plotly.graph_objects as go
import streamlit as st
from streamlit_folium import st_folium

from engine import analyze, config

DISCLAIMER = "This tool supports, and does not replace, your judgment and local agricultural expertise."
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
GIBS_DATE = "2024-07-15"
GIBS_URL = (
    "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/MODIS_Terra_CorrectedReflectance_TrueColor/"
    f"default/{GIBS_DATE}/GoogleMapsCompatible_Level9/{{z}}/{{y}}/{{x}}.jpg"
)
CUSTOM = "custom"
RISK_LEVEL = {"low": 1, "medium": 2, "high": 3}

st.set_page_config(page_title="FieldShift Advisor", page_icon="🌾", layout="wide")
crops = config.crops()
fields = config.fields()
crop_ids = [c for c in crops if c != "cover_crop"]


def crop_name(cid: str) -> str:
    return crops[cid]["name"]


# ---------------- Sidebar: field, current rotation, priorities ----------------
with st.sidebar:
    st.title("🌾 FieldShift Advisor")
    st.caption(DISCLAIMER)

    field_id = st.selectbox(
        "Field",
        list(fields) + [CUSTOM],
        format_func=lambda f: fields[f]["name"] if f in fields else "Custom point (click the map)",
    )
    if field_id == CUSTOM:
        lat = st.session_state.get("click_lat", 45.0)
        lon = st.session_state.get("click_lon", 10.0)
        preset = {"name": "Custom point", "lat": lat, "lon": lon,
                  "current_rotation": ["maize"] * 4, "irrigation": "rainfed"}
    else:
        preset = fields[field_id]

    st.subheader("Your current rotation (S0)")
    rotation = []
    for y in range(4):
        default = preset["current_rotation"][y]
        crop = st.selectbox(f"Year {y + 1}", crop_ids, index=crop_ids.index(default),
                            format_func=crop_name, key=f"{field_id}_y{y}")
        rotation.append({"year": y + 1, "crop": crop, "cover": False})
    irrigation_options = ["rainfed", "deficit", "full"]
    irrigation = st.selectbox("Irrigation", irrigation_options,
                              index=irrigation_options.index(preset["irrigation"]), key=f"{field_id}_irr")

    st.subheader("What matters to you?")
    priorities = {
        "water": st.slider("💧 Save water", 0, 100, 50),
        "soil": st.slider("🌱 Soil health", 0, 100, 50),
        "profit": st.slider("💶 Profit", 0, 100, 50),
        "resilience": st.slider("🌦️ Climate resilience", 0, 100, 50),
    }

field = {"id": field_id, "name": preset["name"], "lat": preset["lat"], "lon": preset["lon"]}

# ---------------- Header + map ----------------
st.info(DISCLAIMER, icon="🤝")
col_map, col_climate = st.columns([3, 2])

with col_map:
    m = folium.Map(location=[field["lat"], field["lon"]], zoom_start=12, tiles="OpenStreetMap")
    folium.TileLayer(tiles=GIBS_URL, attr="NASA GIBS / MODIS Terra", name=f"NASA MODIS true colour {GIBS_DATE}",
                     max_native_zoom=9, max_zoom=18, overlay=True, opacity=0.7).add_to(m)
    folium.Marker([field["lat"], field["lon"]], tooltip=field["name"]).add_to(m)
    folium.LayerControl().add_to(m)
    out = st_folium(m, height=380, use_container_width=True, key="map")
    if field_id == CUSTOM and out and out.get("last_clicked"):
        click = out["last_clicked"]
        if (click["lat"], click["lng"]) != (st.session_state.get("click_lat"), st.session_state.get("click_lon")):
            st.session_state["click_lat"], st.session_state["click_lon"] = click["lat"], click["lng"]
            st.rerun()

# ---------------- What-if ----------------
st.subheader("What if the climate changes?")
w1, w2 = st.columns(2)
whatif = {
    "rain_pct": w1.slider("Rainfall change (%)", -40, 20, 0, step=5),
    "temp_delta_c": w2.slider("Temperature change (°C)", 0.0, 4.0, 0.0, step=0.5),
}

try:
    with st.spinner("Reading NASA POWER data…"):
        result = analyze(field, rotation, irrigation, priorities, whatif)
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

if result["data_status"] == "sample":
    st.warning("SAMPLE DATA — strategy scores are placeholders until the engine is finished.", icon="🚧")
for note in result["notes"]:
    st.caption(note)

# ---------------- What NASA data says ----------------
with col_climate:
    st.subheader("What NASA data says about this field")
    for key, metric in result["climate"].items():
        st.metric(metric["note"], f"{metric['value']:g} {metric['unit']}")
    first = next(iter(result["climate"].values()))
    st.caption(f"Source: {first['source']}")

# ---------------- Strategy cards ----------------
st.subheader("Your rotation vs. alternatives")
strategies = result["strategies"]
cols = st.columns(len(strategies))
for col, s in zip(cols, strategies):
    with col:
        st.markdown(f"### {s['id']} · {s['label']}")
        st.write(" → ".join(crop_name(cy["crop"]) + (" +cover" if cy["cover"] else "") for cy in s["rotation"]))
        st.caption(f"Irrigation: {s['irrigation']}")
        axes = ["water", "soil", "profit", "resilience"]
        radar = go.Figure(go.Scatterpolar(r=[s["scores"][a] for a in axes] + [s["scores"][axes[0]]],
                                          theta=axes + [axes[0]], fill="toself"))
        radar.update_layout(height=220, margin=dict(l=30, r=30, t=10, b=10), showlegend=False,
                            polar=dict(radialaxis=dict(range=[0, 100], showticklabels=False)))
        st.plotly_chart(radar, width="stretch", key=f"radar_{s['id']}")
        for key, metric in s["metrics"].items():
            delta = s["delta_vs_s0"].get(key)
            st.metric(key.replace("_", " "), f"{metric['value']:g} {metric['unit']}",
                      delta=None if s["id"] == "S0" or not delta else f"{delta:+g} vs S0")
        card = s["evidence_card"]
        with st.expander("Evidence card"):
            st.markdown(f"**Why:** {card['why']}")
            st.markdown("**Evidence**")
            for e in card["evidence"]:
                st.markdown(f"- {e['claim']}  \n  _{e['source']} · confidence {e['confidence']}_")
            st.markdown("**Benefits**\n" + "\n".join(f"- ✅ {b}" for b in card["benefits"]))
            st.markdown("**Risks**\n" + "\n".join(f"- ⚠️ {r}" for r in card["risks"]))
            st.markdown("**Information gaps**\n" + "\n".join(f"- {g}" for g in card["information_gaps"]))
            st.markdown("**Needs local review**\n" + "\n".join(f"- 🔎 {n}" for n in card["needs_local_review"]))
            st.caption(f"Confidence: {card['confidence']}")

# ---------------- Calendars ----------------
st.subheader("When is the field bare?")
bare = go.Figure(go.Heatmap(
    z=[s["calendars"]["bare_months"] for s in strategies],
    x=MONTHS, y=[f"{s['id']} {s['label']}" for s in strategies],
    zmin=0, zmax=1, colorscale="YlOrBr", colorbar=dict(title="share of years bare"),
))
bare.update_layout(height=60 + 40 * len(strategies), margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(bare, width="stretch")

st.subheader("When are the crops vulnerable?")
pick = st.selectbox("Strategy", [s["id"] for s in strategies],
                    format_func=lambda sid: next(f"{s['id']} {s['label']}" for s in strategies if s["id"] == sid))
vuln = next(s for s in strategies if s["id"] == pick)["calendars"]["vulnerability"]
vfig = go.Figure(go.Heatmap(
    z=[[RISK_LEVEL.get(r) for r in levels] for levels in vuln.values()],
    x=MONTHS, y=[crop_name(c) for c in vuln], zmin=1, zmax=3,
    colorscale=[[0, "#d9f0d3"], [0.5, "#fdd49e"], [1, "#d7301f"]],
    colorbar=dict(tickvals=[1, 2, 3], ticktext=["low", "medium", "high"]),
))
vfig.update_layout(height=60 + 40 * len(vuln), margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(vfig, width="stretch")

# ---------------- Learn + methods ----------------
with st.expander("📚 Learn: the terms used here"):
    st.markdown("TODO (Dev B): evapotranspiration, water balance, frost risk, cover crops, nitrogen-fixing crops.")
with st.expander("🔬 Data & methods"):
    st.markdown("TODO (Dev B): datasets, formulas, limitations. See README.md → Data.")
