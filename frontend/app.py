import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="WIMSA",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Redirect to login if not authenticated, otherwise go to products
if not st.session_state.get("token"):
    st.switch_page("pages/1_Login.py")
else:
    st.switch_page("pages/2_Products.py")
