import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_tailwind import st_tw
from dotenv import load_dotenv

load_dotenv()

from utils.api_client import APIError, get_reorder_points, get_movement_trends, get_warehouse_capacity
from utils.auth import require_auth, require_supervisor, render_sidebar, get_token

st.set_page_config(page_title="WIMSA — Analytics", page_icon="📊", layout="wide")

require_auth()
require_supervisor()
render_sidebar()

st.title("📊 Analytics Dashboard")

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading analytics..."):
    try:
        reorder_data = get_reorder_points(get_token())
        trends_data  = get_movement_trends(get_token())
        capacity     = get_warehouse_capacity(get_token())
    except APIError as e:
        st.error(f"Failed to load analytics: {e.detail}")
        st.stop()

# ── Section 1: Warehouse Capacity ─────────────────────────────────────────────
st.subheader("🏭 Warehouse Capacity")

pct = capacity["utilization_pct"]

# Determine color based on utilization
if pct >= 85:
    color = "red"
    bg    = "bg-red-50"
    text  = "text-red-700"
elif pct >= 60:
    color = "yellow"
    bg    = "bg-yellow-50"
    text  = "text-yellow-700"
else:
    color = "green"
    bg    = "bg-green-50"
    text  = "text-green-700"

# Stat cards via st_tw
col1, col2, col3 = st.columns(3)
with col1:
    st_tw(
        f'<div class="bg-blue-50 rounded-xl p-4 text-center border border-blue-100">'
        f'<p class="text-3xl font-bold text-blue-700">{capacity["total_capacity"]}</p>'
        f'<p class="text-sm text-gray-500 mt-1">Total Capacity (units)</p>'
        f'</div>',
        height=100,
    )
with col2:
    st_tw(
        f'<div class="bg-indigo-50 rounded-xl p-4 text-center border border-indigo-100">'
        f'<p class="text-3xl font-bold text-indigo-700">{capacity["used_capacity"]}</p>'
        f'<p class="text-sm text-gray-500 mt-1">Used Capacity (units)</p>'
        f'</div>',
        height=100,
    )
with col3:
    st_tw(
        f'<div class="{bg} rounded-xl p-4 text-center border">'
        f'<p class="text-3xl font-bold {text}">{pct:.1f}%</p>'
        f'<p class="text-sm text-gray-500 mt-1">Utilization</p>'
        f'</div>',
        height=100,
    )

# Plotly gauge
gauge_fig = go.Figure(go.Indicator(
    mode  = "gauge+number",
    value = pct,
    title = {"text": "Warehouse Utilization (%)"},
    gauge = {
        "axis":  {"range": [0, 100]},
        "bar":   {"color": "#4f46e5"},
        "steps": [
            {"range": [0,  60], "color": "#bbf7d0"},
            {"range": [60, 85], "color": "#fef08a"},
            {"range": [85, 100], "color": "#fecaca"},
        ],
        "threshold": {
            "line":  {"color": "red", "width": 4},
            "value": 85,
        },
    },
))
gauge_fig.update_layout(height=300, margin={"t": 40, "b": 0, "l": 20, "r": 20})
st.plotly_chart(gauge_fig, use_container_width=True)

st.divider()

# ── Section 2: Reorder Alerts ─────────────────────────────────────────────────
st.subheader("⚠️ Reorder Alerts")
st.caption("Products with stock below their minimum stock level.")

if not reorder_data:
    st.success("All products are above minimum stock levels. No reorders needed.")
else:
    df_reorder = pd.DataFrame(reorder_data)

    reorder_fig = px.bar(
        df_reorder,
        x     = "product_name",
        y     = "deficit",
        color = "deficit",
        color_continuous_scale = "Reds",
        title  = "Stock Deficit by Product (units below minimum)",
        labels = {"deficit": "Units Below Min", "product_name": "Product"},
    )
    reorder_fig.update_layout(
        xaxis_tickangle = -30,
        coloraxis_showscale = False,
        height = 400,
    )
    st.plotly_chart(reorder_fig, use_container_width=True)

    display_cols = ["product_name", "sku", "stock_quantity", "min_stock_level", "deficit"]
    st.dataframe(df_reorder[display_cols], use_container_width=True, hide_index=True)

st.divider()

# ── Section 3: Movement Trends ────────────────────────────────────────────────
st.subheader("📈 Product Movement Trends")
st.caption("Total inbound vs outbound units per product.")

if not trends_data:
    st.info("No transaction data available yet.")
else:
    df_trends = pd.DataFrame(trends_data)

    trends_fig = px.bar(
        df_trends,
        x       = "product_name",
        y       = ["total_inbound", "total_outbound"],
        barmode = "group",
        title   = "Inbound vs Outbound by Product",
        labels  = {"value": "Units", "product_name": "Product", "variable": "Type"},
        color_discrete_map = {
            "total_inbound":  "#22c55e",
            "total_outbound": "#f97316",
        },
    )
    trends_fig.update_layout(xaxis_tickangle=-30, height=420)
    st.plotly_chart(trends_fig, use_container_width=True)

    display_cols = ["product_name", "sku", "total_inbound", "total_outbound", "net_movement"]
    st.dataframe(df_trends[display_cols], use_container_width=True, hide_index=True)
