import streamlit as st
import json
import os
import time
from groq import Groq
from gtts import gTTS
import io
import base64

# --- Setup ---
DATA_FILE = "chat_history.json"
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

st.set_page_config(layout="wide")

# Dark Theme with Robot style
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- State ---
if "chats" not in st.session_state:
    st.session_state.chats = [{"id": "main", "messages": []}]
active_chat = st.session_state.chats[0]

# --- Sidebar ---
with st.sidebar:
    st.header("Coach Workspace")
    if st.button("New Chat"):
        st.session_state.chats = [{"id": str(time.time()), "messages": []}]
        st.rerun()

# --- Main Logic ---
st.title("Fluency Coach")

# Render chat with specific avatars
for msg in active_chat["messages"]:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if "audio_html" in msg:
            st.markdown(msg["audio_html"], unsafe_allow_html=True)

# Use a container for input to prevent loop errors
input_container = st.container()

with input_container:
    # 1. Audio Input
    audio_file = st.audio_input("Speak to your Coach 🎤")
    
    # 2. Text Input
    if prompt := st.chat_input("Type your message..."):
        active_chat["messages"].append({"role": "user", "content": prompt})
        active_chat["messages"].append({"role": "assistant", "content": "I received your message."})
        st.rerun()

# Handle Audio only if file is new
if audio_file and not st.session_state.get("last_audio") == audio_file:
    st.session_state.last_audio = audio_file
    # (Your existing Groq transcription logic here)
    # ... after response ...
    st.rerun()
