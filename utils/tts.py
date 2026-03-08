import os
import streamlit as st

def speak_output(text: str):
    """
    Speak text locally using pyttsx3.
    On Streamlit Cloud, safely disable TTS.
    """
    if os.environ.get("STREAMLIT_CLOUD") == "1":
        st.warning("🔇 Voice output is disabled on Streamlit Cloud.")
        return

    try:
        import pyttsx3
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
    except Exception:
        st.error("Text-to-Speech is not supported in this environment.")
