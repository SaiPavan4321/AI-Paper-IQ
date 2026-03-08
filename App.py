import streamlit as st
from pathlib import Path
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Paper IQ Analyzer | Login",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("Login")

# ---------------- LOAD CSS ----------------
with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------- ENSURE DATA DIRECTORY ----------------
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

users_file = data_dir / "users.log"
if not users_file.exists():
    users_file.touch()

# ---------------- SAVE USERNAME ----------------
def save_username(username):
    with open(users_file, "a", encoding="utf-8") as f:
        f.write(f"{username},{datetime.now().isoformat()}\n")

# ---------------- SESSION ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "username" not in st.session_state:
    st.session_state.username = ""

# ---------------- VISITS FILE ----------------
visits_file = Path("assets/visits.txt")
if not visits_file.exists():
    visits_file.write_text("0")

visits = int(visits_file.read_text())

# ---------------- REDIRECT IF LOGGED IN ----------------
if st.session_state.logged_in:
    st.switch_page("pages/1_Home.py")

# ---------------- SIMPLE LOGIN UI ----------------
st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="login-box">
        <h1>📄 Paper IQ Analyzer</h1>
        <p>Enter your username to continue</p>
    </div>
    """,
    unsafe_allow_html=True
)

username = st.text_input(
    "Username",
    placeholder="e.g. SaiPavan",
    label_visibility="collapsed"
)

if st.button("Login", use_container_width=True):
    if username.strip() == "":
        st.error("Username is required")
    else:
        # 🔢 Increment visits
        visits += 1
        visits_file.write_text(str(visits))

        # 💾 Save username permanently
        save_username(username.strip())

        # 🔐 Session login
        st.session_state.username = username.strip()
        st.session_state.logged_in = True

        st.switch_page("pages/1_Home.py")

# ---------------- VISITS DISPLAY ----------------
st.markdown(
    f"<div class='login-visits'>Total Visits: {visits}</div>",
    unsafe_allow_html=True
)
