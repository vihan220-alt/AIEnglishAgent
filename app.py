import streamlit as st
import json
import os
from groq import Groq
from gtts import gTTS
import io
import base64

# --- Setup ---
DATA_FILE = "chat_history.json"
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

if "chats" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: st.session_state.chats = json.load(f)
    else:
        st.session_state.chats = [{"id": "main", "messages": []}]
        
active_chat = st.session_state.chats[0]

# --- Sidebar ---
with st.sidebar:
    st.header("Coach Workspace")
    if st.button("New Chat"):
        st.session_state.chats = [{"id": str(time.time()), "messages": []}]
        st.rerun()

# --- Main Interface ---
st.title("Fluency Coach")

# Render existing messages
for msg in active_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 1. Audio Input Block ---
audio_file = st.audio_input("Speak to your Coach 🎤")
if audio_file:
    # Transcribe and append logic here...
    st.info("Processing voice...")
    # (Use your Groq transcribe block here)

# --- 2. Text Input Block ---
if prompt := st.chat_input("Type your message..."):
    # Append text message to chat
    active_chat["messages"].append({"role": "user", "content": prompt})
    # Add response
    active_chat["messages"].append({"role": "assistant", "content": "I received your text."})
    # Save and Refresh
    with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
    st.rerun()
