import streamlit as st
import pytz
from datetime import datetime

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Home | Paper IQ Analyzer",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------- LOGOUT ----------------
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("login.py")

if st.query_params.get("logout") == ["true"]:
    logout()

# ---------------- AUTH GUARD ----------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first")
    st.stop()

# ---------------- LOAD CSS ----------------
with open("assets/styles.css", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ---------------- SESSION STATE INIT ----------------
st.session_state.setdefault("uploaded_file", None)
st.session_state.setdefault("pdf_history", [])
st.session_state.setdefault("result_history", [])

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 👤 Profile")
    st.write("**Username:**", st.session_state.username)
    st.write("**Project:** Paper IQ Analyzer")
    st.divider()

    st.markdown("## 📄 Upload History")
    if st.session_state.pdf_history:
        for pdf in st.session_state.pdf_history[-5:]:
            st.write("•", pdf)
    else:
        st.caption("No uploads yet")
    st.divider()

# ---------------- TOP RIGHT USER + LOGOUT ----------------
top_left, top_center, top_right = st.columns([6, 3, 1])

with top_right:
  st.markdown(
    f"""
    <div class="top-user-box">
        <div class="top-username">{st.session_state.username}</div>
        <a href="?logout=true" class="top-logout">Logout</a>
    </div>
    """,
    unsafe_allow_html=True
)


# ---------------- GREETING ----------------
IST = pytz.timezone("Asia/Kolkata")
hour = datetime.now(IST).hour

if hour < 12:
    greeting = "Good Morning"
elif hour < 17:
    greeting = "Good Afternoon"
elif hour < 21:
    greeting = "Good Evening"
else:
    greeting = "Good Night"

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-title">{greeting}, {st.session_state.username} 👋</div>
        <div class="hero-sub">
            Upload a text PDF to start analysis
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------------- UPLOAD CARD ----------------
st.markdown(
    """
    <div class="upload-card">
        <div class="upload-title">📄 Upload your PDF document</div>
    """,
    unsafe_allow_html=True
)

uploaded_file = st.file_uploader("", type=["pdf"])

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- HANDLE NEW PDF ----------------
if uploaded_file is not None:

    # Detect new file
    if (
        st.session_state.uploaded_file is None
        or uploaded_file.name != st.session_state.uploaded_file.name
    ):
        # Save file
        st.session_state.uploaded_file = uploaded_file

        # Add to history (avoid duplicates)
        if uploaded_file.name not in st.session_state.pdf_history:
            st.session_state.pdf_history.append(uploaded_file.name)

        # 🔥 RESET ANALYSIS STATE (CRITICAL FIX)
        for key in [
            "pdf_path",
            "output_text",
            "last_ran",
            "selected_module",
            "module_name",
        ]:
            st.session_state.pop(key, None)

        st.success("✅ PDF uploaded successfully")
        st.info("📄 New PDF detected. Analysis will run on the new document.")

        st.switch_page("pages/2_Analysis.py")
