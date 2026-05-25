import streamlit as st
from streamlit_mic_recorder import mic_recorder

# --- 1. Styling & Theme ---
st.set_page_config(page_title="Fluency Coach", layout="centered")
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: url("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
        background-size: 80px;
    }
    h1, h2, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 3. UI Components ---
st.title("Fluency Coach")

# Sidebar
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.rerun()

# Chat Display
for msg in st.session_state.messages:
    with st.chat_message("user"):
        st.markdown(msg)

# Chat Input (Simplified)
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append(prompt)
    st.rerun()

# Audio Controls
c1, c2 = st.columns(2)
with c1:
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="rec")
with c2:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
