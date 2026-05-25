import streamlit as st
from style import apply_custom_theme
from message import display_chat
from audio import audio_interface

# Set page config FIRST
st.set_page_config(page_title="Fluency Coach", layout="centered")

# Apply style
apply_custom_theme()

st.title("Fluency Coach")

# Sidebar
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()

# Run components
display_chat()
audio_interface()
