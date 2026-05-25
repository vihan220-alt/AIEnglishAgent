import streamlit as st
from style import apply_custom_theme
from message import display_chat
from audio import audio_interface

st.set_page_config(page_title="Fluency Coach", layout="centered")
apply_custom_theme()

# Sidebar
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()

# Main UI
st.title("Fluency Coach")
display_chat()
audio_interface()
