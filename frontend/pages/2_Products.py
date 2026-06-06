import streamlit as st
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from utils.api_client import APIError, get_products, create_product, update_product, delete_product
from utils.auth import require_auth, render_sidebar, get_token, is_supervisor

st.set_page_config(page_title="WIMSA — Products", page_icon="📦", layout="wide")

require_auth()
render_sidebar()

st.title("📦 Products")

# ── Load products ─────────────────────────────────────────────────────────────
try:
    products = get_products(get_token())
except APIError as e:
    st.error(f"Failed to load products: {e.detail}")
    st.stop()

if not products:
    st.info("No products found.")
else:
    df = pd.DataFrame(products)

    # Add a stock status column
    def stock_status(row):
        if row["stock_quantity"] <= 0:
            return "🔴 Out of Stock"
        elif row["stock_quantity"] < row["min_stock_level"]:
            return "🟡 Low Stock"
        return "🟢 OK"

    df["status"] = df.apply(stock_status, axis=1)

    display_cols = ["id", "sku", "name", "category", "location",
                    "stock_quantity", "min_stock_level", "max_capacity", "status"]
    st.dataframe(df[display_cols], use_container_width=True, hide_index=True)

# ── Supervisor CRUD ───────────────────────────────────────────────────────────
if is_supervisor():
    st.divider()
    st.subheader("Manage Products")

    tab_add, tab_edit, tab_delete = st.tabs(["➕ Add Product", "✏️ Edit Product", "🗑️ Delete Product"])

    # ── Add ──────────────────────────────────────────────────────────────────
    with tab_add:
        with st.form("add_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                name     = st.text_input("Name")
                sku      = st.text_input("SKU")
                category = st.text_input("Category")
                location = st.text_input("Location")
            with col2:
                stock_quantity = st.number_input("Initial Stock",  min_value=0, value=0)
                min_stock      = st.number_input("Min Stock Level", min_value=0, value=10)
                max_capacity   = st.number_input("Max Capacity",    min_value=1, value=100)
            submitted = st.form_submit_button("Create Product", use_container_width=True)

        if submitted:
            if not name or not sku or not category or not location:
                st.error("Name, SKU, Category, and Location are all required.")
            elif max_capacity < min_stock:
                st.error("Max capacity must be greater than or equal to min stock level.")
            else:
                try:
                    create_product(get_token(), {
                        "name": name, "sku": sku, "category": category,
                        "location": location, "stock_quantity": stock_quantity,
                        "min_stock_level": min_stock, "max_capacity": max_capacity,
                    })
                    st.success("Product created successfully.")
                    st.rerun()
                except APIError as e:
                    st.error(e.detail)

    # ── Edit ─────────────────────────────────────────────────────────────────
    with tab_edit:
        if not products:
            st.info("No products to edit.")
        else:
            product_map = {p["id"]: f"{p['name']} ({p['sku']})" for p in products}
            selected_id = st.selectbox(
                "Select product to edit",
                options=list(product_map.keys()),
                format_func=lambda x: product_map[x],
                key="edit_select",
            )
            selected = next(p for p in products if p["id"] == selected_id)

            with st.form("edit_product_form"):
                col1, col2 = st.columns(2)
                with col1:
                    name     = st.text_input("Name",     value=selected["name"])
                    sku      = st.text_input("SKU",      value=selected["sku"])
                    category = st.text_input("Category", value=selected["category"])
                    location = st.text_input("Location", value=selected["location"])
                with col2:
                    min_stock    = st.number_input("Min Stock Level", min_value=0,
                                                   value=selected["min_stock_level"])
                    max_capacity = st.number_input("Max Capacity",    min_value=1,
                                                   value=selected["max_capacity"])
                submitted = st.form_submit_button("Update Product", use_container_width=True)

            if submitted:
                try:
                    update_product(get_token(), selected_id, {
                        "name": name, "sku": sku, "category": category,
                        "location": location, "min_stock_level": min_stock,
                        "max_capacity": max_capacity,
                    })
                    st.success("Product updated successfully.")
                    st.rerun()
                except APIError as e:
                    st.error(e.detail)

    # ── Delete ────────────────────────────────────────────────────────────────
    with tab_delete:
        if not products:
            st.info("No products to delete.")
        else:
            product_map = {p["id"]: f"{p['name']} ({p['sku']})" for p in products}
            selected_id = st.selectbox(
                "Select product to delete",
                options=list(product_map.keys()),
                format_func=lambda x: product_map[x],
                key="delete_select",
            )
            st.warning(f"This will permanently delete **{product_map[selected_id]}**.")
            if st.button("Delete Product", type="primary", use_container_width=True):
                try:
                    delete_product(get_token(), selected_id)
                    st.success("Product deleted.")
                    st.rerun()
                except APIError as e:
                    st.error(e.detail)
