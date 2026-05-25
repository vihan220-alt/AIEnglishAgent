import streamlit as st
from style import apply_custom_theme
from streamlit_mic_recorder import mic_recorder

# 1. Apply styles
apply_custom_theme()

st.title("Fluency Coach")

# 2. Simple Chat Input
if "messages" not in st.session_state:
    st.session_state.messages = []

# 3. Display
for msg in st.session_state.messages:
    st.write(msg)

# 4. Input
if prompt := st.chat_input("Say something..."):
    st.session_state.messages.append(prompt)
    st.rerun()

# 5. Simple mic trigger
audio = mic_recorder(start_prompt="Speak", stop_prompt="Stop")
if audio:
    st.write("Audio detected!")
