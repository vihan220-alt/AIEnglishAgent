import streamlit as st
from streamlit_mic_recorder import mic_recorder
from style import apply_custom_theme  # This matches the file name style.py

# 1. Apply the style
apply_custom_theme()

# 2. Chat logic
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. UI
st.title("Fluency Coach")

with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()

for msg in st.session_state.messages:
    with st.chat_message("user"):
        st.markdown(msg)

# 4. Input and Controls
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append(prompt)
    st.rerun()

c1, c2 = st.columns(2)
with c1:
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="rec")
with c2:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
