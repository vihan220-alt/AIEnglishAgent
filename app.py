import streamlit as st
import json
import os
import time
import io
from groq import Groq
from gtts import gTTS

# --- File Sync Setup ---
DATA_FILE = "chat_history.json"
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

st.set_page_config(layout="wide")

# --- Custom CSS for Solid Dark AI Background ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117 !important;
        color: #ffffff;
    }
    .stSidebar {
        background-color: #161b22 !important;
    }
    div[data-testid="stExpander"] {
        background-color: #1f242c !important;
        border: 1px solid #30363d !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session States Safely
if "stop_audio" not in st.session_state:
    st.session_state.stop_audio = False
if "active_audio_bytes" not in st.session_state:
    st.session_state.active_audio_bytes = None

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

# Helper function to generate clean audio binary data
def get_audio_bytes(text):
    try:
        tts = gTTS(text=text, lang='en', tld='co.uk')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        return mp3_fp.getvalue()
    except Exception:
        return None

# Helper function to get real text completions from Groq AI model
def get_ai_response(conversation_history):
    if not client:
        return "API Key missing. Please check your st.secrets."
    try:
        # Build systemic language tutor formatting instructions
        messages_payload = [
            {"role": "system", "content": "You are a helpful, encouraging English fluency coach. Keep your responses conversational, concise (2-3 sentences max), and optimized for spoken dialogue."}
        ]
        # Append historical logs
        for m in conversation_history[-6:]: # look at recent context window
            messages_payload.append({"role": m["role"], "content": m["content"]})
            
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=messages_payload,
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error connecting to coach brain: {str(e)}"

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Coach Workspace")
    if st.button("➕ New Chat"):
        new_chat = {"id": f"chat_{time.time()}", "name": f"Chat {len(st.session_state.chats)+1}", "messages": [], "pinned": False}
        st.session_state.chats.append(new_chat)
        save_data(st.session_state.chats)
        st.session_state.active_idx = len(st.session_state.chats) - 1
        st.session_state.active_audio_bytes = None  
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
                st.session_state.active_audio_bytes = None  
                st.rerun()
            if c2.button("📌", key=f"pin_{idx}"):
                chat['pinned'] = not chat.get('pinned', False)
                save_data(st.session_state.chats)
                st.rerun()
            if c3.button("🗑️", key=f"del_{idx}"):
                if len(st.session_state.chats) > 1:
                    st.session_state.chats.pop(idx)
                    st.session_state.active_idx = 0
                    st.session_state.active_audio_bytes = None
                    save_data(st.session_state.chats)
                    st.rerun()

# --- Main Chat Screen ---
if st.session_state.active_idx
