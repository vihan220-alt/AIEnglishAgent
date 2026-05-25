import streamlit as st
from streamlit_mic_recorder import mic_recorder

def audio_interface():
    c1, c2 = st.columns(2)
    with c1:
        mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="rec")
    with c2:
        if st.button("Clear Chat"):
            st.session_state.messages = []
            st.rerun()
