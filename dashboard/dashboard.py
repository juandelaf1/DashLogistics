import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parents[1]))
from src.database import get_engine, read_sql_query

load_dotenv()

st.set_page_config(page_title="DashLogistics", layout="wide", initial_sidebar_state="collapsed")

ST_CENTER = {
    "AL":(32.8,-86.9),"AK":(61.4,-152.5),"AZ":(34.0,-111.7),"AR":(34.8,-92.4),"CA":(36.1,-119.7),
    "CO":(39.0,-105.5),"CT":(41.6,-72.7),"DE":(39.0,-75.5),"FL":(27.8,-81.4),"GA":(32.6,-83.4),
    "HI":(19.7,-155.5),"ID":(44.4,-114.7),"IL":(40.0,-89.4),"IN":(39.8,-86.1),"IA":(42.0,-93.4),
    "KS":(38.5,-98.4),"KY":(37.5,-84.7),"LA":(30.9,-91.7),"ME":(45.3,-69.4),"MD":(39.0,-76.7),
    "MA":(42.4,-72.7),"MI":(44.3,-85.6),"MN":(46.1,-94.3),"MS":(32.8,-89.8),"MO":(38.5,-92.5),
    "MT":(47.0,-109.7),"NE":(41.5,-99.6),"NV":(38.5,-117.1),"NH":(43.6,-71.6),"NJ":(40.3,-74.5),
    "NM":(34.4,-106.1),"NY":(42.8,-75.0),"NC":(35.6,-79.4),"ND":(47.4,-100.4),"OH":(40.3,-82.8),
    "OK":(35.6,-97.1),"OR":(43.8,-120.6),"PA":(41.0,-77.7),"RI":(41.6,-71.5),"SC":(33.9,-80.9),
    "SD":(44.3,-100.2),"TN":(35.9,-86.5),"TX":(31.5,-99.4),"UT":(39.3,-111.7),"VT":(44.1,-72.7),
    "VA":(37.6,-78.4),"WA":(47.3,-120.4),"WV":(38.6,-80.6),"WI":(44.6,-89.9),"WY":(42.9,-107.5),"DC":(38.9,-77.0),
}

st.markdown("""
<style>
    .stApp { background: #0e1117; }
    .main .block-container { padding: 1.5rem 2rem; }
    h1, h2, h3, h4 { color: #f0f2f6 !important; font-weight: 600 !important; }
    div[data-testid="stMetric"] { background: #1a1d23; border: 1px solid #2d3139; border-radius: 12px; padding: 1rem; }
    div[data-testid="stMetric"] label { color: #8b8fa3 !important; font-size: 0.75rem !important; text-transform: uppercase; }
    div[data-testid="stMetric"] div { color: #f0f2f6 !important; }
    div[data-testid="stDataFrame"] { background: #1a1d23; border-radius: 8px; }
    .stTabs [data-baseweb="tab-list"] { gap: 0; background: #1a1d23; border-radius: 8px; padding: 0.25rem; }
    .stTabs [data-baseweb="tab"] { border-radius: 6px; color: #8b8fa3; }
    .stTabs [aria-selected="true"] { background: #2d3139; color: #f0f2f6; }
    hr { border-color: #2d3139; }
</style>
""", unsafe_allow_html=True)


def _table_exists(engine, name):
    try:
        from sqlalchemy import inspect
        return name in inspect(engine).get_table_names()
    except: return False

@st.cache_data(ttl=300)
def load():
    engine = get_engine()
    tables = {}
    targets = ["freight_by_state","freight_lanes","freight_mode_split","freight_commodities",
               "freight_yearly","freight_trade_balance","truck_rates",
               "fuel_prices","shipping_stats","eia_fuel_prices",
               "freight_lanes_truck","freight_lanes_rail",
               "route_costs","route_congestion","lane_efficiency"]
    for t in targets:
        try: tables[t] = read_sql_query(f"SELECT * FROM {t}", engine) if _table_exists(engine, t) else pd.DataFrame()
        except: tables[t] = pd.DataFrame()
    return tables

t = load()

# Data freshness
_db_path = Path(__file__).resolve().parents[1] / "data" / "dashlogistics.db"
LAST_UPDATED = "Unknown"
if _db_path.exists():
    _mt = datetime.fromtimestamp(_db_path.stat().st_mtime)
    LAST_UPDATED = _mt.strftime("%b %d, %Y at %I:%M %p")

df_state = t["freight_by_state"]
df_lanes = t["freight_lanes"]
df_modes = t["freight_mode_split"]
df_comm = t["freight_commodities"]
df_yearly = t["freight_yearly"]
df_balance = t["freight_trade_balance"]
df_rates = t["truck_rates"]
df_fuel = t["fuel_prices"]
df_ship = t["shipping_stats"]
df_eia = t["eia_fuel_prices"]
df_costs = t["route_costs"]
df_cong = t["route_congestion"]
df_lane_eff = t["lane_efficiency"]

if df_state.empty and df_ship.empty:
    st.error("Run `python main.py` first"); st.stop()

# ─── Prep ───
if not df_ship.empty:
    df_ship["pop_m"] = df_ship["population"] / 1_000_000

fuel_lookup = {}
if not df_fuel.empty:
    try:
        fuel_lookup = df_fuel.sort_values("scraped_at").groupby("state").last()[["regular","diesel"]].to_dict("index")
    except: pass

if not df_state.empty:
    df_state["regular"] = df_state["state"].map(lambda s: fuel_lookup.get(s,{}).get("regular", 0))
    df_state["diesel"] = df_state["state"].map(lambda s: fuel_lookup.get(s,{}).get("diesel", 0))
    df_state["lat"] = df_state["state"].map(lambda s: ST_CENTER.get(s, (0,0))[0])
    df_state["lon"] = df_state["state"].map(lambda s: ST_CENTER.get(s, (0,0))[1])

def fmt(v, d=0):
    try: return f"{v:,.{d}f}"
    except: return str(v)

# ─── Select state ───
all_states = sorted(df_state["state"].tolist() if not df_state.empty else df_ship["state"].tolist())
if "sel" not in st.session_state or st.session_state.sel not in all_states:
    st.session_state.sel = all_states[0] if all_states else "AL"
sel = st.session_state.sel

# ─── Header ───
st.markdown(f"# DashLogistics  &nbsp;·&nbsp; US Freight Intelligence  &nbsp;·&nbsp; <span style='font-size:0.75rem;color:#8b8fa3;font-weight:400;'>Updated {LAST_UPDATED}</span>", unsafe_allow_html=True)

# ─── Top metrics ───
tons_24 = df_yearly[df_yearly["year"]==2024]["tons_m"].values[0] if not df_yearly.empty and 2024 in df_yearly["year"].values else 0
val_24 = df_yearly[df_yearly["year"]==2024]["value_b"].values[0] if not df_yearly.empty and 2024 in df_yearly["year"].values else 0
avg_rate = df_rates["rate_per_mile"].mean() if not df_rates.empty else 0
avg_cost = df_costs["cost_per_mi"].mean() if not df_costs.empty else 0
high_cong = len(df_cong[df_cong["congestion_tier"]=="High"]) if not df_cong.empty else 0

# YoY deltas
_tons_d = _val_d = None
if not df_yearly.empty:
    _y24 = df_yearly[df_yearly["year"]==2024]
    _y23 = df_yearly[df_yearly["year"]==2023]
    if not _y24.empty and not _y23.empty:
        _tons_d = ((_y24["tons_m"].values[0] - _y23["tons_m"].values[0]) / _y23["tons_m"].values[0]) * 100
        _val_d = ((_y24["value_b"].values[0] - _y23["value_b"].values[0]) / _y23["value_b"].values[0]) * 100

col_k = st.columns(5)
col_k[0].metric("Freight Volume", f"{fmt(tons_24)}M tons", f"{_tons_d:+.1f}% YoY" if _tons_d is not None else None)
col_k[1].metric("Freight Value", f"${fmt(val_24)}B", f"{_val_d:+.1f}% YoY" if _val_d is not None else None)
col_k[2].metric("Avg Truck Rate", f"${avg_rate:.2f}/mi")
col_k[3].metric("Avg Op Cost", f"${avg_cost:.2f}/mi")
col_k[4].metric("High Congestion Routes", str(high_cong))

# ─── HERO: Map + Detail ───
st.markdown("## ")
map_col, info_col = st.columns([2.5, 1])

with map_col:
    # Build flow lines for selected state
    flow = pd.DataFrame()
    if not df_lanes.empty and sel in df_lanes["origin"].values:
        top_f = df_lanes[df_lanes["origin"]==sel].head(8).copy()
        if not top_f.empty:
            top_f["ol"] = top_f["origin"].map(lambda s: ST_CENTER.get(s,(0,0))[1])
            top_f["olat"] = top_f["origin"].map(lambda s: ST_CENTER.get(s,(0,0))[0])
            top_f["dl"] = top_f["destination"].map(lambda s: ST_CENTER.get(s,(0,0))[1])
            top_f["dlat"] = top_f["destination"].map(lambda s: ST_CENTER.get(s,(0,0))[0])
            flow = top_f

    hover = {"state":False}
    if "tons" in df_state.columns: hover["tons"] = ":,.0f"
    if "diesel" in df_state.columns: hover["diesel"] = ":.2f"

    fmap = px.choropleth(df_state, locations="state", locationmode="USA-states",
        color="tons" if "tons" in df_state.columns else "regular", scope="usa",
        color_continuous_scale="Viridis", hover_name="state", hover_data=hover, title="")

    for _, r in flow.iterrows():
        w = max(0.5, min(8, r["tons_m"]/15))
        fmap.add_trace(go.Scattergeo(lon=[r["ol"],r["dl"]], lat=[r["olat"],r["dlat"]],
            mode="lines", line=dict(width=w, color="rgba(79,139,249,0.5)"), showlegend=False,
            hoverinfo="text", text=f"{r['origin']} -> {r['destination']}: {fmt(r['tons_m'],1)}M tons"))
    if sel in ST_CENTER:
        fmap.add_trace(go.Scattergeo(lon=[ST_CENTER[sel][1]], lat=[ST_CENTER[sel][0]],
            mode="markers", marker=dict(size=14,color="#f9a84f",symbol="star",line=dict(width=2,color="white")),
            name=sel, hoverinfo="skip"))

    fmap.update_geos(showsubunits=True, resolution=50, bgcolor="#0e1117",
        scope="usa", center=dict(lat=39.8, lon=-98.6), projection_scale=1.5)
    fmap.update_layout(margin=dict(l=0,r=0,t=20,b=0), height=520, dragmode=False,
        paper_bgcolor="#0e1117", geo_bgcolor="#0e1117", font_color="#f0f2f6", clickmode="event+select",
        coloraxis_colorbar=dict(title="Tons"))

    ev = st.plotly_chart(fmap, width='stretch', key=f"map_{sel}", on_select="rerun")
    if ev and "selection" in ev and ev["selection"] and "points" in ev["selection"]:
        pts = ev["selection"]["points"]
        if pts and "location" in pts[0]:
            clicked = pts[0]["location"]
            if clicked != sel:
                st.session_state.sel = clicked
                st.rerun()

with info_col:
    sel_idx = all_states.index(sel) if sel in all_states else 0
    st.selectbox("State", all_states, index=sel_idx, key="picker",
        on_change=lambda: setattr(st.session_state,"sel",st.session_state.picker), label_visibility="collapsed")
    rs = df_state[df_state["state"]==sel]
    if not rs.empty:
        r = rs.iloc[0]
        st.subheader(sel)
        st.write(f"Freight: **{fmt(r.get('tons',0))} tons**")
        st.write(f"Value: **${fmt(r.get('value',0))}**")
        st.write(f"Diesel: **${r.get('diesel',0):.2f}**")
        if not df_balance.empty:
            b = df_balance[df_balance["state"]==sel]
            if not b.empty:
                bn = b.iloc[0]["net_tons_m"]
                clr = "#4fc94f" if bn>0 else "#f94f6f"
                st.markdown(f"Trade: <span style='color:{clr}'>**{'Surplus' if bn>0 else 'Deficit'} {fmt(abs(bn),1)}M t**</span>", unsafe_allow_html=True)
        if not df_costs.empty:
            cs = df_costs[df_costs["origin"]==sel]
            if not cs.empty:
                st.write(f"Cost/mi: **${cs['cost_per_mi'].mean():.2f}**")
                st.write(f"Fuel %: **{cs['fuel_pct'].mean():.0f}%**")
        if not flow.empty:
            st.write("**Top routes**")
            for _, fr in flow.iterrows():
                st.write(f"→ {fr['destination']}: {fmt(fr['tons_m'],1)}M t")
        if not df_cong.empty:
            cg = df_cong[df_cong["origin"]==sel]
            if not cg.empty:
                cr = cg["congestion_ratio"].mean()
                st.write(f"Congestion: **{cr:.2f}** (1.0 = free)")

# ─── TABS ───
t1, t2, t3, t4 = st.tabs(["Volumes", "Costs & Congestion", "Routes by Mode", f"Deep: {sel}"])

# ═══════════════ TAB 1: VOLUMES ═══════════════
with t1:
    col_a, col_b = st.columns([1.5,1])
    with col_a:
        if not df_yearly.empty:
            fy = go.Figure()
            fy.add_trace(go.Scatter(x=df_yearly["year"], y=df_yearly["tons_m"], mode="lines+markers",
                name="Tons (M)", line=dict(color="#4f8bf9",width=3),
                fill="tozeroy", fillcolor="rgba(79,139,249,0.08)"))
            fy.add_trace(go.Scatter(x=df_yearly["year"], y=df_yearly["value_b"], mode="lines+markers",
                name="Value ($B)", line=dict(color="#4fc94f",width=3), yaxis="y2",
                fill="tozeroy", fillcolor="rgba(79,201,79,0.08)"))
            fy.update_layout(title="National Freight 2018-2024", height=380,
                paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", font_color="#f0f2f6", hovermode="x unified",
                yaxis=dict(title="M tons"), yaxis2=dict(title="$B", overlaying="y", side="right"))
            st.plotly_chart(fy, width='stretch')
    with col_b:
        if not df_comm.empty:
            _vcol = [c for c in df_comm.columns if c not in ["commodity","pct"] and df_comm[c].dtype in ["int64","float64"]][0]
            t10 = df_comm.head(10).copy()
            t10["pct"] = (t10[_vcol] / t10[_vcol].sum() * 100).round(1)
            fc = px.bar(t10, x="commodity", y=_vcol, title="Top Commodities",
                labels={"commodity":"", _vcol:"Tons"}, color="commodity", text="pct")
            fc.update_traces(texttemplate="%{text}%", textposition="outside")
            fc.update_layout(showlegend=False, height=380, paper_bgcolor="#0e1117",
                plot_bgcolor="#0e1117", font_color="#f0f2f6", xaxis_tickangle=-45)
            st.plotly_chart(fc, width='stretch')

    col_c, col_d = st.columns([1,1.5])
    with col_c:
        if not df_modes.empty:
            fm = px.pie(df_modes, values="tons_2024", names="mode", title="Mode Split 2024",
                color_discrete_sequence=px.colors.sequential.Viridis_r, hole=0.4)
            fm.update_traces(texttemplate="%{label}<br>%{value}M tons", textfont_size=13)
            fm.update_layout(height=330, paper_bgcolor="#0e1117", font_color="#f0f2f6")
            st.plotly_chart(fm, width='stretch')
    with col_d:
        if not df_balance.empty:
            fb = px.choropleth(df_balance, locations="state", locationmode="USA-states",
                color="net_tons_m", scope="usa", color_continuous_scale="RdYlGn",
                title="Trade Balance (net M tons)",
                hover_name="state", hover_data={"net_tons_m":":,.1f","outbound":":,.0f","inbound":":,.0f"})
            fb.update_geos(showsubunits=True, bgcolor="#0e1117")
            fb.update_layout(height=330, paper_bgcolor="#0e1117", geo_bgcolor="#0e1117",
                font_color="#f0f2f6", coloraxis_colorbar=dict(title="Net M t"))
            st.plotly_chart(fb, width='stretch')

    if not df_lanes.empty:
        st.markdown("### Top 20 National Lanes")
        top20 = df_lanes.head(20)[["origin","destination","commodity","tons_m"]].copy()
        top20.index = range(1,len(top20)+1)
        st.dataframe(top20, width='stretch', hide_index=False)

# ═══════════════ TAB 2: COSTS & CONGESTION ═══════════════
with t2:
    col_e, col_f = st.columns([1.5,1])
    with col_e:
        if not df_costs.empty:
            c_avg = df_costs.groupby("origin")[["fuel_cost","driver_cost","maint_cost"]].mean().reset_index()
            cm = c_avg.melt(id_vars="origin", var_name="type", value_name="$")
            fig_cb = px.bar(cm, x="origin", y="$", color="type", title="Avg Cost per Route by Origin State",
                color_discrete_map={"fuel_cost":"#f94f6f","driver_cost":"#4f8bf9","maint_cost":"#4fc94f"})
            fig_cb.update_layout(height=400, paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
                font_color="#f0f2f6", legend=dict(orientation="h",y=1.1))
            st.plotly_chart(fig_cb, width='stretch')
    with col_f:
        if not df_cong.empty:
            cs = df_cong.groupby("origin")["congestion_ratio"].mean().reset_index()
            cs["ratio"] = cs["congestion_ratio"].round(2)
            fig_cg = px.choropleth(cs, locations="origin", locationmode="USA-states",
                color="ratio", scope="usa", color_continuous_scale="RdYlGn_r",
                title="Congestion by Origin (ratio)",
                hover_name="origin", hover_data={"ratio":":.2f"})
            fig_cg.update_geos(showsubunits=True, bgcolor="#0e1117")
            fig_cg.update_layout(height=400, paper_bgcolor="#0e1117", geo_bgcolor="#0e1117",
                font_color="#f0f2f6", coloraxis_colorbar=dict(title="Congestion Ratio (1.0 = free)"))
            st.plotly_chart(fig_cg, width='stretch')

    if not df_costs.empty:
        st.markdown("### Detailed Route Costs")
        route_show = df_costs[df_costs["origin"]==sel].head(20) if sel in df_costs["origin"].values else df_costs.head(20)
        rc = route_show[["origin","destination","driving_mi","driving_hr","total_cost","cost_per_mi","fuel_pct"]].copy()
        rc.index = range(1,len(rc)+1)
        st.dataframe(rc, width='stretch', hide_index=False)

    if not df_lane_eff.empty:
        st.markdown("### Most Efficient Lanes (tons per $)")
        eff = df_lane_eff[df_lane_eff["total_cost"]>0].head(10)
        if not eff.empty:
            eff_s = eff[["origin","destination","tons_m","total_cost","tons_per_dollar"]].copy()
            eff_s.index = range(1,len(eff_s)+1)
            st.dataframe(eff_s, width='stretch', hide_index=False)

# ═══════════════ TAB 3: ROUTES BY MODE ═══════════════
with t3:
    mtabs = st.tabs(["Truck","Rail","Water"])
    mode_sets = [t.get(k, pd.DataFrame()) for k in ["freight_lanes_truck","freight_lanes_rail","freight_lanes_water"]]
    mode_names = ["Truck","Rail","Water"]
    mode_colors = {"Truck":"#4f8bf9","Rail":"#f9a84f","Water":"#4fc94f"}

    for mi, (mdf, mname) in enumerate(zip(mode_sets, mode_names)):
        with mtabs[mi]:
            if not mdf.empty:
                col_m1, col_m2 = st.columns([1.5,1])
                with col_m1:
                    mv = mdf.head(15).copy()
                    mv["ol"] = mv["origin"].map(lambda s: ST_CENTER.get(s,(0,0))[1])
                    mv["olat"] = mv["origin"].map(lambda s: ST_CENTER.get(s,(0,0))[0])
                    mv["dl"] = mv["destination"].map(lambda s: ST_CENTER.get(s,(0,0))[1])
                    mv["dlat"] = mv["destination"].map(lambda s: ST_CENTER.get(s,(0,0))[0])

                    fmo = go.Figure()
                    fmo.add_trace(go.Choropleth(locations=df_state["state"], locationmode="USA-states",
                        z=[0]*len(df_state), colorscale=[[0,"rgba(14,17,23,0)"],[1,"rgba(14,17,23,0)"]],
                        showscale=False, hoverinfo="skip"))
                    c = mode_colors[mname]
                    for _, r in mv.iterrows():
                        w = max(0.5, min(6, r["tons_m"]/20))
                        fmo.add_trace(go.Scattergeo(lon=[r["ol"],r["dl"]], lat=[r["olat"],r["dlat"]],
                            mode="lines", line=dict(width=w, color=c), showlegend=False,
                            hoverinfo="text", text=f"{r['origin']} -> {r['destination']}: {fmt(r['tons_m'],1)}M tons"))
                    fmo.update_geos(showsubunits=True, resolution=50, bgcolor="#0e1117")
                    fmo.update_layout(margin=dict(l=0,r=0,t=0,b=0), height=450,
                        paper_bgcolor="#0e1117", geo_bgcolor="#0e1117", font_color="#f0f2f6")
                    st.plotly_chart(fmo, width='stretch')
                with col_m2:
                    tb = mdf[["origin","destination","tons_m"]].head(15).copy()
                    tb.index = range(1,len(tb)+1)
                    st.dataframe(tb, width='stretch', hide_index=False)
                    st.write(f"Total: **{fmt(mdf['tons_m'].sum(),1)}M tons** over **{len(mdf)}** lanes")
            else:
                st.info(f"No {mname} lane data")

# ═══════════════ TAB 4: DEEP DIVE ═══════════════
with t4:
    rs = df_state[df_state["state"]==sel]
    if not rs.empty:
        r = rs.iloc[0]
        ck = st.columns(4)
        ck[0].metric("Volume", fmt(r.get("tons",0)))
        ck[1].metric("Value", f"${fmt(r.get('value',0))}")
        ck[2].metric("Diesel", f"${r.get('diesel',0):.2f}")
        ck[3].metric("Regular", f"${r.get('regular',0):.2f}")

    _cm = df_state[["state"]].copy()
    _cm["hl"] = _cm["state"].apply(lambda s: 1 if s == sel else 0)
    _fmm = px.choropleth(_cm, locations="state", locationmode="USA-states",
        color="hl", scope="usa", color_continuous_scale=[[0,"#1a1d23"],[1,"#4f8bf9"]],
        title="", hover_name="state")
    _fmm.update_geos(showsubunits=True, bgcolor="#0e1117")
    _fmm.update_layout(height=160, margin=dict(l=0,r=0,t=0,b=0),
        paper_bgcolor="#0e1117", geo_bgcolor="#0e1117", coloraxis_showscale=False)
    st.plotly_chart(_fmm, width='stretch')

    if not df_balance.empty:
        b = df_balance[df_balance["state"]==sel]
        if not b.empty:
            bi = b.iloc[0]
            st.write(f"Outbound: **{fmt(bi['outbound'])}t** → Inbound: **{fmt(bi['inbound'])}t** → "
                    f"**{'Net Exporter' if bi['net_tons']>0 else 'Net Importer'}** ({fmt(abs(bi['net_tons_m']),1)}M tons)")

    if not df_lanes.empty:
        out = df_lanes[df_lanes["origin"]==sel].head(12)
        inn = df_lanes[df_lanes["destination"]==sel].head(12)
        co, ci = st.columns(2)
        with co:
            st.markdown(f"**Outbound**")
            if not out.empty:
                o = out[["destination","commodity","tons_m"]].copy(); o.index = range(1,len(o)+1)
                st.dataframe(o, width='stretch', hide_index=False)
        with ci:
            st.markdown(f"**Inbound**")
            if not inn.empty:
                i = inn[["origin","commodity","tons_m"]].copy(); i.index = range(1,len(i)+1)
                st.dataframe(i, width='stretch', hide_index=False)

    if not df_costs.empty:
        cs = df_costs[df_costs["origin"]==sel]
        if not cs.empty:
            st.markdown("**Cost Summary**")
            ck2 = st.columns(4)
            ck2[0].metric("Avg Cost/mi", f"${cs['cost_per_mi'].mean():.2f}")
            ck2[1].metric("Fuel %", f"{cs['fuel_pct'].mean():.0f}%")
            ck2[2].metric("Avg Distance", f"{cs['driving_mi'].mean():.0f} mi")
            ck2[3].metric("Avg Transit", f"{cs['driving_hr'].mean():.1f} hrs")
            rt = cs[["destination","driving_mi","driving_hr","total_cost","cost_per_mi","fuel_pct"]].head(15).copy()
            rt.index = range(1,len(rt)+1)
            st.dataframe(rt, width='stretch', hide_index=False)

    if not df_cong.empty:
        cg = df_cong[df_cong["origin"]==sel]
        if not cg.empty:
            st.markdown(f"**Congestion** — avg ratio: **{cg['congestion_ratio'].mean():.2f}**")
            hi = cg[cg["congestion_tier"]=="High"]
            if not hi.empty:
                st.write(f"High congestion routes: {', '.join(hi['destination'].tolist())}")

    if not df_rates.empty:
        rs2 = df_rates[df_rates["origin_state"]==sel]
        if not rs2.empty:
            st.markdown("**USDA Truck Rates**")
            rt2 = rs2[["destination","quarter","rate_per_mile","rate_per_truckload"]].copy()
            rt2.index = range(1,len(rt2)+1)
            st.dataframe(rt2, width='stretch', hide_index=False)

# ─── Footer ───
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#6b7280;font-size:0.7rem;padding:1rem 0;line-height:1.6;'>"
    "Data: BTS Freight Analysis Framework (FAF 5.7.1) · USDA Ag Transport · AAA Fuel Gauge · EIA · OSRM | "
    "Routes by top 25 states (FAF + OSRM cached) | Dashboard updated " + LAST_UPDATED +
    "</div>",
    unsafe_allow_html=True
)
