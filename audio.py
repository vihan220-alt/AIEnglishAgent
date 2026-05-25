import streamlit as st
from streamlit_mic_recorder import mic_recorder

def audio_interface():
    st.write("### 🎙️ Voice Controls")
    c1, c2 = st.columns(2)
    with c1:
        # Wrapped in a try/except to prevent total app failure
        try:
            mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="rec")
        except Exception as e:
            st.error("Audio failed to load.")
    with c2:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
