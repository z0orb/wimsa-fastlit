import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from utils.api_client import APIError, get_products, get_transactions, create_inbound, create_outbound
from utils.auth import require_auth, render_sidebar, get_token

st.set_page_config(page_title="WIMSA — Transactions", page_icon="🔄", layout="wide")

require_auth()
render_sidebar()

st.title("🔄 Transactions")

# ── Load data ─────────────────────────────────────────────────────────────────
try:
    products     = get_products(get_token())
    transactions = get_transactions(get_token())
except APIError as e:
    st.error(f"Failed to load data: {e.detail}")
    st.stop()

product_map = {p["id"]: f"{p['name']} ({p['sku']})" for p in products}

tab_in, tab_out, tab_history = st.tabs(["📥 Inbound", "📤 Outbound", "📋 History"])

# ── Inbound ───────────────────────────────────────────────────────────────────
with tab_in:
    st.subheader("Record Inbound")
    with st.form("inbound_form"):
        product_id = st.selectbox(
            "Product",
            options=list(product_map.keys()),
            format_func=lambda x: product_map[x],
        )
        quantity  = st.number_input("Quantity", min_value=1, value=1)
        reference = st.text_input("Reference (optional)")
        notes     = st.text_area("Notes (optional)")
        submitted = st.form_submit_button("Record Inbound", use_container_width=True)

    if submitted:
        try:
            create_inbound(get_token(), {
                "product_id": product_id,
                "quantity":   quantity,
                "reference":  reference or None,
                "notes":      notes or None,
            })
            st.success("Inbound transaction recorded.")
            st.rerun()
        except APIError as e:
            st.error(e.detail)

# ── Outbound ──────────────────────────────────────────────────────────────────
with tab_out:
    st.subheader("Record Outbound")
    with st.form("outbound_form"):
        product_id = st.selectbox(
            "Product",
            options=list(product_map.keys()),
            format_func=lambda x: product_map[x],
            key="out_product",
        )
        quantity  = st.number_input("Quantity", min_value=1, value=1, key="out_qty")
        reference = st.text_input("Reference (optional)", key="out_ref")
        notes     = st.text_area("Notes (optional)", key="out_notes")
        submitted = st.form_submit_button("Record Outbound", use_container_width=True)

    if submitted:
        try:
            create_outbound(get_token(), {
                "product_id": product_id,
                "quantity":   quantity,
                "reference":  reference or None,
                "notes":      notes or None,
            })
            st.success("Outbound transaction recorded.")
            st.rerun()
        except APIError as e:
            st.error(e.detail)

# ── History ───────────────────────────────────────────────────────────────────
with tab_history:
    st.subheader("Transaction History")

    if not transactions:
        st.info("No transactions yet.")
    else:
        df = pd.DataFrame(transactions)

        # Map type to emoji indicator
        df["type"] = df["type"].map(
            lambda t: "📥 inbound" if t == "inbound" else "📤 outbound"
        )

        # Map product_id to name for readability
        df["product"] = df["product_id"].map(
            lambda pid: product_map.get(pid, f"ID {pid}")
        )

        display_cols = ["id", "product", "type", "quantity",
                        "reference", "notes", "created_by", "created_at"]
        st.dataframe(df[display_cols], use_container_width=True, hide_index=True)
