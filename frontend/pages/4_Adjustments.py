import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from utils.api_client import APIError, get_products, get_adjustments, create_adjustment
from utils.auth import require_auth, require_supervisor, render_sidebar, get_token

st.set_page_config(page_title="WIMSA — Adjustments", page_icon="⚙️", layout="wide")

require_auth()
require_supervisor()
render_sidebar()

st.title("⚙️ Stock Adjustments")

# ── Load data ─────────────────────────────────────────────────────────────────
try:
    products    = get_products(get_token())
    adjustments = get_adjustments(get_token())
except APIError as e:
    st.error(f"Failed to load data: {e.detail}")
    st.stop()

product_map = {p["id"]: f"{p['name']} ({p['sku']})" for p in products}

tab_new, tab_history = st.tabs(["➕ New Adjustment", "📋 History"])

# ── New Adjustment ────────────────────────────────────────────────────────────
with tab_new:
    st.subheader("Submit Stock Adjustment")
    st.caption("Use this to correct stock quantities when the system differs from physical count.")

    with st.form("adjustment_form"):
        product_id   = st.selectbox(
            "Product",
            options=list(product_map.keys()),
            format_func=lambda x: product_map[x],
        )
        new_quantity = st.number_input("New Quantity", min_value=0, value=0)
        reason       = st.text_input("Reason", placeholder="e.g. damaged goods, count correction")
        notes        = st.text_area("Notes (optional)")
        submitted    = st.form_submit_button("Submit Adjustment", use_container_width=True)

    if submitted:
        if not reason.strip():
            st.error("Reason is required.")
        else:
            try:
                create_adjustment(get_token(), {
                    "product_id":   product_id,
                    "new_quantity": new_quantity,
                    "reason":       reason,
                    "notes":        notes or None,
                })
                st.success("Stock adjustment recorded.")
                st.rerun()
            except APIError as e:
                st.error(e.detail)

# ── History ───────────────────────────────────────────────────────────────────
with tab_history:
    st.subheader("Adjustment History")

    if not adjustments:
        st.info("No adjustments recorded yet.")
    else:
        df = pd.DataFrame(adjustments)

        # Add a diff column showing the change
        df["change"] = df.apply(
            lambda r: f"+{r['new_quantity'] - r['previous_quantity']}"
            if r["new_quantity"] >= r["previous_quantity"]
            else str(r["new_quantity"] - r["previous_quantity"]),
            axis=1,
        )

        # Map product_id to name
        df["product"] = df["product_id"].map(
            lambda pid: product_map.get(pid, f"ID {pid}")
        )

        display_cols = ["id", "product", "previous_quantity",
                        "new_quantity", "change", "reason", "notes",
                        "created_by", "created_at"]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
