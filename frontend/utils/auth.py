import streamlit as st
from streamlit_tailwind import st_tw

# Session state keys
SESSION_TOKEN    = "token"
SESSION_ROLE     = "role"
SESSION_USERNAME = "username"


def set_session(token: str, role: str, username: str) -> None:
    """Store auth info in session state after successful login."""
    st.session_state[SESSION_TOKEN]    = token
    st.session_state[SESSION_ROLE]     = role
    st.session_state[SESSION_USERNAME] = username


def clear_session() -> None:
    """Remove all auth keys from session state (logout)."""
    for key in [SESSION_TOKEN, SESSION_ROLE, SESSION_USERNAME]:
        st.session_state.pop(key, None)


def is_authenticated() -> bool:
    """Return True if a token is present in session state."""
    return bool(st.session_state.get(SESSION_TOKEN))


def is_supervisor() -> bool:
    """Return True if the current user has the supervisor role."""
    return st.session_state.get(SESSION_ROLE) == "supervisor"


def get_token() -> str:
    """Return the current JWT token."""
    return st.session_state.get(SESSION_TOKEN, "")


def get_role() -> str:
    """Return the current user role."""
    return st.session_state.get(SESSION_ROLE, "")


def get_username() -> str:
    """Return the current username."""
    return st.session_state.get(SESSION_USERNAME, "")


def require_auth() -> None:
    """
    Guard: redirect to login and stop if the user is not authenticated.
    Call as the first statement of every protected page.
    """
    if not is_authenticated():
        st.switch_page("pages/1_Login.py")
        st.stop()


def require_supervisor() -> None:
    """
    Guard: redirect to products and stop if the user is not a supervisor.
    Call after require_auth() on supervisor-only pages.
    """
    if not is_supervisor():
        st.error("Access denied. This page is for supervisors only.")
        st.switch_page("pages/2_Products.py")
        st.stop()


def render_sidebar() -> None:
    """
    Render the shared sidebar with app branding, role badge,
    username, and logout button.
    """
    with st.sidebar:
        st.markdown("## 📦 WIMSA")
        st.markdown("Warehouse Inventory System")
        st.divider()

        # Role badge via st_tw
        username = get_username()
        role     = get_role()

        if role == "supervisor":
            badge_html = (
                f'<div class="mb-1 text-sm text-gray-600">Logged in as</div>'
                f'<div class="font-semibold text-gray-800 mb-2">{username}</div>'
                f'<span class="inline-block px-2 py-1 rounded-full text-xs font-bold '
                f'bg-yellow-100 text-yellow-800">Supervisor</span>'
            )
        else:
            badge_html = (
                f'<div class="mb-1 text-sm text-gray-600">Logged in as</div>'
                f'<div class="font-semibold text-gray-800 mb-2">{username}</div>'
                f'<span class="inline-block px-2 py-1 rounded-full text-xs font-bold '
                f'bg-blue-100 text-blue-800">Ground Staff</span>'
            )

        st_tw(badge_html, height=80)
        st.divider()

        # Nav links
        st.page_link("pages/2_Products.py",     label="📦 Products")
        st.page_link("pages/3_Transactions.py", label="🔄 Transactions")
        if is_supervisor():
            st.page_link("pages/4_Adjustments.py", label="⚙️ Adjustments")
            st.page_link("pages/5_Analytics.py",   label="📊 Analytics")

        st.divider()

        if st.button("Logout", use_container_width=True):
            clear_session()
            st.switch_page("pages/1_Login.py")
