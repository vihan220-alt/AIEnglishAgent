import streamlit as st
import json
import os
import time
import io
import hashlib
from groq import Groq
from gtts import gTTS

# --- File Sync Setup ---
DATA_FILE = "chat_history.json"
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

st.set_page_config(layout="wide")

# --- Custom CSS for High-Contrast Text & Robot Face Background ---
st.markdown("""
    <style>
    /* Main App Background with Crisp SVG Robot Face Pattern */
    .stApp {
        background-color: #0e1117 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M10 20h10v10H10zm30 0h10v10H40zM15 42h30v4H15zM5 10h50v40H5zm2 2v36h46V12zm18-7h10v3H25z' fill='%231f242c' fill-opacity='0.6' fill-rule='evenodd'/%3E%3C/svg%3E") !important;
        background-repeat: repeat !important;
    }
    
    /* Global Text Contrast Rules */
    .stApp, .stApp p, div[data-testid="stMarkdownContainer"] p {
        color: #ffffff !important;
        font-weight: 500 !important;
        font-size: 1.05rem !important;
    }
    
    /* Make chat bubbles high contrast */
    div[data-testid="stChatMessage"] {
        background-color: #1f242c !important;
        border: 1px solid #30363d !important;
        border-radius: 8px !important;
        padding: 10px !important;
        margin-bottom: 10px !important;
    }
    
    /* Ensure chat input text is dark/readable during typing */
    div[data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }
    
    /* Clear captions */
    .stApp .stCaption, div[data-testid="stCaptionContainer"] {
        color: #9ca3af !important;
        font-size: 0.95rem !important;
    }

    /* Sidebar Background styling */
    .stSidebar {
        background-color: #161b22 !important;
    }
    
    /* Expander boxes styling */
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
if "last_processed_audio_hash" not in st.session_state:
    st.session_state.last_processed_audio_hash = None

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
        tts = gTTS(text=text, lang='en', tld='co.in')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        return mp3_fp.getvalue()
    except Exception:
        return None

# Helper function to get real text completions from Groq AI model
def get_ai_response(conversation_history):
    if not client:
        return "Groq API Key is missing. Please add it to your Streamlit secrets."
    try:
        messages_payload = [
            {
                "role": "system", 
                "content": "You are a helpful, direct, and concise AI assistant. Provide short, exact responses (maximum 1-2 sentences). Do not give long explanations or ask unnecessary follow-up questions."
            }
        ]
        for m in conversation_history[-6:]:
            messages_payload.append({"role": m["role"], "content": m["content"]})
            
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages_payload,
            temperature=0.5
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error connecting to assistant: {str(e)}"

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Workspace")
    if st.button("➕ New Chat"):
        new_chat = {"id": f"chat_{time.time()}", "name": f"Chat {len(st.session_state.chats)+1}", "messages": [], "pinned": False}
        st.session_state.chats.append(new_chat)
        save_data(st.session_state.chats)
        st.session_state.active_idx = len(st.session_state.chats) - 1
        st.session_state.active_audio_bytes = None  
        st.session_state.last_processed_audio_hash = None
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
                st.session_state.last_processed_audio_hash = None
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
                    st.session_state.last_processed_audio_hash = None
                    save_data(st.session_state.chats)
                    st.rerun()

# --- Main Chat Screen ---
if st.session_state.active_idx >= len(st.session_state.chats):
    st.session_state.active_idx = 0

active_chat = st.session_state.chats[st.session_state.active_idx]

st.title(f"AI Assistant: {active_chat.get('name', 'Chat')}")

# Render message history cleanly
if "messages" in active_chat and active_chat["messages"]:
    for msg in active_chat["messages"]:
        avatar_icon = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])
else:
    st.caption("Ask a question by typing or speaking below!")

# --- ONE-TIME VOICE PLAYBACK ENGINE ---
if st.session_state.active_audio_bytes and not st.session_state.stop_audio:
    st.audio(st.session_state.active_audio_bytes, format="audio/mp3", autoplay=True)
    st.session_state.active_audio_bytes = None  

st.divider()

# --- Control & Input Section ---
if not st.session_state.stop_audio:
    if st.button("🛑 Stop Audio Response"):
        st.session_state.stop_audio = True
        st.session_state.active_audio_bytes = None
        st.rerun()
else:
    if st.button("▶️ Enable Audio Response"):
        st.session_state.stop_audio = False
        st.rerun()

audio_file
