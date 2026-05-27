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

# Custom CSS for Background and UI
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- Initialization ---
if "chats" not in st.session_state:
    st.session_state.chats = [{"id": "Chat 1", "messages": []}]

if "active_chat_idx" not in st.session_state:
    st.session_state.active_chat_idx = 0

active_chat = st.session_state.chats[st.session_state.active_chat_idx]

# --- Sidebar (Chat List) ---
with st.sidebar:
    st.header("Coach Workspace")
    if st.button("New Chat"):
        new_chat = {"id": f"Chat {len(st.session_state.chats) + 1}", "messages": []}
        st.session_state.chats.append(new_chat)
        st.session_state.active_chat_idx = len(st.session_state.chats) - 1
        st.rerun()
    
    st.divider()
    for idx, chat in enumerate(st.session_state.chats):
        if st.button(chat["id"], key=f"btn_{idx}"):
            st.session_state.active_chat_idx = idx
            st.rerun()

# --- Main Logic ---
st.title("Fluency Coach")

# Render chat with explicit robot avatar
for msg in active_chat["messages"]:
    avatar = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if "audio_html" in msg:
            st.markdown(msg["audio_html"], unsafe_allow_html=True)

# --- Input Handling ---
# Text Input
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    active_chat["messages"].append({"role": "assistant", "content": "I received your message."})
    st.rerun()

# Audio Input
audio_file = st.audio_input("Speak to your Coach 🎤")
if audio_file and not st.session_state.get("last_audio") == audio_file:
    st.session_state.last_audio = audio_file
    # Add your Groq transcription logic here
    st.rerun()
