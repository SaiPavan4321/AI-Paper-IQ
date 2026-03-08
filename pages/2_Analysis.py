import streamlit as st
import tempfile
import os

from utils.tts import speak_output

from nlp_modules.ai_summarization import ai_summarization_pipeline
from nlp_modules.insight_extraction import insight_extraction_pipeline
from nlp_modules.keyword_extraction import keyword_extraction_pipeline
from nlp_modules.text_preprocessing import text_preprocessing_pipeline


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Analysis | Paper IQ Analyzer",
    layout="wide",
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

# ---------------- PDF CHECK ----------------
if "uploaded_file" not in st.session_state:
    st.warning("⚠️ Please upload a PDF first")
    st.stop()

# ---------------- TEMP FILE ----------------
def save_temp(file):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(file.getvalue())
    tmp.close()
    return tmp.name

if "pdf_path" not in st.session_state:
    st.session_state.pdf_path = save_temp(st.session_state.uploaded_file)

pdf_path = st.session_state.pdf_path

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

# ---------------- HEADER ----------------
st.markdown("<h2 style='text-align:center;'>🧠 Analysis Modules</h2>", unsafe_allow_html=True)

# ---------------- MODULE BUTTONS ----------------
left, center, right = st.columns([1, 2, 1])

with center:
    c1, c2 = st.columns(2)
    c3, c4 = st.columns(2)

    if c1.button("🤖 AI Summarization", use_container_width=True):
        st.session_state.selected_module = "summary"

    if c2.button("🧠 Insight Extraction", use_container_width=True):
        st.session_state.selected_module = "insights"

    if c3.button("🏷️ Keyword Extraction", use_container_width=True):
        st.session_state.selected_module = "keywords"

    if c4.button("🧹 Text Preprocessing", use_container_width=True):
        st.session_state.selected_module = "preprocess"

    st.divider()

# ---------------- RUN MODULE ----------------
if "selected_module" in st.session_state:
    st.markdown("📊Output:")

    module = st.session_state.selected_module

    if st.session_state.get("last_ran") != module:
        with st.spinner("Processing... Please wait"):

            if module == "summary":
                output_text = ai_summarization_pipeline(pdf_path)
                module_name = "AI Summarization"

            elif module == "insights":
                output_text = insight_extraction_pipeline(pdf_path)
                module_name = "Insight Extraction"

            elif module == "keywords":
                keywords = keyword_extraction_pipeline(pdf_path)
                output_text = ", ".join(keywords)
                module_name = "Keyword Extraction"

            elif module == "preprocess":
                output_text = text_preprocessing_pipeline(pdf_path)
                module_name = "Text Preprocessing"

            st.session_state.output_text = output_text
            st.session_state.module_name = module_name
            st.session_state.last_ran = module

# ---------------- OUTPUT ----------------
if "output_text" in st.session_state:

    st.success(f"{st.session_state.module_name} completed")
    st.write(st.session_state.output_text)

    # ---------------- SPEAK OUTPUT ----------------
    if st.button("🔊 Speak Output"):
        speak_output(st.session_state.output_text)
