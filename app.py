import streamlit as st
import json
import os
import time
import io
import base64
from groq import Groq
from gtts import gTTS

# --- File Sync Setup ---
DATA_FILE = "chat_history.json"
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

st.set_page_config(layout="wide")

# --- Custom CSS for Dark AI Background ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .stSidebar {
        background-color: #161b22;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session States
if "stop_audio" not in st.session_state:
    st.session_state.stop_audio = False

# --- Safe Data Load/Save ---
def load_data():
    default_chat = [{"id": "chat_default", "name": "Chat 1", "messages": [], "pinned": False}]
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    return default_chat
                return json.loads(content)
        except Exception:
            return default_chat
    return default_chat

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

if "chats" not in st.session_state: 
    st.session_state.chats = load_data()
if "active_idx" not in st.session_state: 
    st.session_state.active_idx = 0

# Helper function to generate auto-playing speech HTML
def generate_audio_html(text):
    if st.session_state.stop_audio:
        return ""
    try:
        tts = gTTS(text=text, lang='en', tld='co.uk')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        b64 = base64.b64encode(mp3_fp.getvalue()).decode()
        return f'<audio src="data:audio/mp3;base64,{b64}" autoplay controls></audio>'
    except Exception:
        return ""

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Coach Workspace")
    if st.button("➕ New Chat"):
        new_chat = {"id": f"chat_{time.time()}", "name": f"Chat {len(st.session_state.chats)+1}", "messages": [], "pinned": False}
        st.session_state.chats.append(new_chat)
        save_data(st.session_state.chats)
        st.session_state.active_idx = len(st.session_state.chats) - 1
        st.rerun()

    st.divider()
    
    for idx, chat in enumerate(st.session_state.chats):
        with st.expander(f"{'📌' if chat.get('pinned', False) else ''} {chat.get('name', 'Chat')}"):
            new_name = st.text_input("Rename", value=chat.get('name', 'Chat'), key=f"name_{idx}")
            if new_name != chat.get('name'):
                chat['name'] = new_name
                save_data(st.session_state.chats)
            
            c1, c2, c3 = st.columns(3)
            if c1.button("Open", key=f"open_{idx}"):
                st.session_state.active_idx = idx
                st.rerun()
            if c2.button("📌", key=f"pin_{idx}"):
                chat['pinned'] = not chat.get('pinned', False)
                save_data(st.session_state.chats)
                st.rerun()
            if c3.button("🗑️", key=f"del_{idx}"):
                if len(st.session_state.chats) > 1:
                    st.session_state.chats.pop(idx)
                    st.session_state.active_idx = 0
                    save_data(st.session_state.chats)
                    st.rerun()

# --- Main Chat Screen ---
if st.session_state.active_idx >= len(st.session_state.chats):
    st.session_state.active_idx = 0

active_chat = st.session_state.chats[st.session_state.active_idx]

# Layout for Title and Stop Button
title_col, stop_col = st.columns([4, 1])
with title_col:
    st.title(f"Fluency Coach: {active_chat.get('name', 'Chat')}")
with stop_col:
    st.write("")  # padding
    if st.button("🛑 Stop Audio"):
        st.session_state.stop_audio = True
        st.rerun()

# Render message history
if "messages" in active_chat and active_chat["messages"]:
    for msg in active_chat["messages"]:
        avatar_icon = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])
            if "audio_html" in msg and msg["audio_html"]:
                st.markdown(msg["audio_html"], unsafe_allow_html=True)
else:
    st.caption("This conversation is empty. Talk or type below!")

st.divider()

# --- Input Section ---
# 1. Speak Button (Audio Input)
audio_file = st.audio_input("Speak to your Coach 🎤")

if audio_file and not st.session_state.get("last_audio") == audio_file:
    st.session_state.last_audio = audio_file
    st.session_state.stop_audio = False  # Reset stop trigger
    
    if client:
        # Process voice transcription
        buffer = io.BytesIO(audio_file.read())
        buffer.name = "audio.wav"
        translation = client.audio.transcriptions.create(file=buffer, model="whisper-large-v3", response_format="text")
        user_text = translation.strip()
        
        # Coach thinking logic
        bot_reply = f"I heard you say: '{user_text}'. Your pronunciation is coming along nicely, let's keep practicing!"
        audio_html = generate_audio_html(bot_reply)
        
        # Save to logs
        if "messages" not in active_chat: active_chat["messages"] = []
        active_chat["messages"].append({"role": "user", "content": user_text})
        active_chat["messages"].append({"role": "assistant", "content": bot_reply, "audio_html": audio_html})
        
        save_data(st.session_state.chats)
        st.rerun()

# 2. Type Box (Text Input)
if prompt := st.chat_input("Type your message here..."):
    st.session_state.stop_audio = False
    if "messages" not in active_chat: active_chat["messages"] = []
    
    active_chat["messages"].append({"role": "user", "content": prompt})
    bot_reply = f"Awesome! I've received your text: '{prompt}'."
    active_chat["messages"].append({"role": "assistant", "content": bot_reply, "audio_html": ""})
    
    save_data(st.session_state.chats)
    st.rerun()
