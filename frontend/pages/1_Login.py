import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from utils.api_client import APIError, login, get_me
from utils.auth import is_authenticated, set_session

st.set_page_config(page_title="WIMSA — Login", page_icon="📦", layout="centered")

# Already logged in → skip to products
if is_authenticated():
    st.switch_page("pages/2_Products.py")
    st.stop()

# ── Page UI ──────────────────────────────────────────────────────────────────

st.markdown("## 📦 WIMSA")
st.markdown("#### Warehouse Inventory Management System")
st.divider()

st.subheader("Sign In")

with st.form("login_form"):
    username  = st.text_input("Username")
    password  = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login", use_container_width=True)

if submitted:
    if not username or not password:
        st.error("Please enter both username and password.")
    else:
        try:
            token_data = login(username, password)
            user_info  = get_me(token_data["access_token"])
            set_session(
                token    = token_data["access_token"],
                role     = user_info["role"],
                username = user_info["username"],
            )
            st.success(f"Welcome, {user_info['username']}!")
            st.switch_page("pages/2_Products.py")
        except APIError as e:
            if e.status_code == 401:
                st.error("Invalid username or password.")
            elif e.status_code == 0:
                st.error("Cannot connect to backend. Make sure the server is running.")
            else:
                st.error(e.detail)
