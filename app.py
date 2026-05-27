import streamlit as st
import json
import os
import time  # Fixes the NameError
from groq import Groq
from gtts import gTTS
import io
import base64

# --- Setup ---
DATA_FILE = "chat_history.json"
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

# Custom CSS for Background and UI
st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a2e;
        color: white;
    }
    .stChatInput { background-color: #16213e; }
    </style>
""", unsafe_allow_html=True)

# --- Initialization ---
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
        with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
        st.rerun()

# --- Main Logic ---
st.title("Fluency Coach")

# Display messages
for msg in active_chat["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "audio_html" in msg:
            st.markdown(msg["audio_html"], unsafe_allow_html=True)

# --- 1. Audio Input Block ---
audio_file = st.audio_input("Speak to your Coach 🎤")
if audio_file:
    # Transcribe
    buffer = io.BytesIO(audio_file.read())
    buffer.name = "audio.wav"
    translation = client.audio.transcriptions.create(file=buffer, model="whisper-large-v3", response_format="text")
    text = translation.strip()
    
    # Generate Response
    response = f"I heard you say: {text}. That's a great start!"
    
    # Generate Audio
    tts = gTTS(text=response, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    b64 = base64.b64encode(fp.getvalue()).decode()
    audio_html = f'<audio autoplay controls src="data:audio/mp3;base64,{b64}"></audio>'
    
    active_chat["messages"].append({"role": "user", "content": text})
    active_chat["messages"].append({"role": "assistant", "content": response, "audio_html": audio_html})
    st.rerun()

# --- 2. Text Input Block ---
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    # Text only response (No audio_html added here)
    active_chat["messages"].append({"role": "assistant", "content": "I received your message."})
    st.rerun()
