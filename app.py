import streamlit as st
from style import apply_custom_theme
from streamlit_mic_recorder import mic_recorder

# Apply style
apply_custom_theme()

st.title("Fluency Coach")

# --- Sidebar ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()

# --- Main Interaction ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    st.chat_message("user").markdown(msg)

st.write("### 🎙️ Speech Input")
audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop ⏹️", key="recorder")

if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append(prompt)
    st.rerun()
