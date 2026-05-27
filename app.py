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

# --- Custom CSS for High-Contrast Bright White Text & Robot Background ---
st.markdown("""
    <style>
    /* 1. Main App Background with Tiled Robot Pattern */
    .stApp {
        background-color: #0e1117 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M10 20h10v10H10zm30 0h10v10H40zM15 42h30v4H15zM5 10h50v40H5zm2 2v36h46V12zm18-7h10v3H25z' fill='%2330363d' fill-opacity='0.4' fill-rule='evenodd'/%3E%3C/svg%3E") !important;
        background-repeat: repeat !important;
    }
    
    /* 2. Global Text Overrides for Ultimate Brightness */
    .stApp, .stApp p, span, div, label, li, ul, ol, .stMarkdown {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* 3. High-Contrast Chat Message Container Blocks */
    div[data-testid="stChatMessage"] {
        background-color: #161b22 !important;
        border: 2px solid #444c56 !important;
        border-radius: 8px !important;
        padding: 15px !important;
        margin-bottom: 12px !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* FORCE ALL CHAT BUBBLE CONTENT & NESTED LISTS TO BE BRIGHT WHITE */
    div[data-testid="stChatMessage"] p, 
    div[data-testid="stChatMessage"] span,
    div[data-testid="stChatMessage"] div,
    div[data-testid="stChatMessage"] li,
    div[data-testid="stChatMessage"] ul,
    div[data-testid="stChatMessage"] ol,
    div[data-testid="stChatMessage"] .stMarkdown p {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.1rem !important;
    }
    
    /* 4. Headings & Titles Brightness */
    h1, h2, h3, .stApp h1, .stApp h2, [data-testid="stHeader"] {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* 5. Fix Chat Input Box Text Color */
    div[data-testid="stChatInput"] textarea {
        color: #ffffff !important;
        background-color: #161b22 !important;
        font-size: 1.05rem !important;
    }
    
    /* 6. Sidebar & Expanders Contrast */
    .stSidebar {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d !important;
    }
    .stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar p, .stSidebar label {
        color: #ffffff !important;
    }
    div[data-testid="stExpander"] {
        background-color: #1f242c !important;
        border: 1px solid #444c56 !important;
    }
    
    /* 7. Caption Text Adjustment */
    .stApp .stCaption, .stApp p.caption, div[data-testid="stCaptionContainer"] {
        color: #c9d1d9 !important;
        font-size: 1rem !important;
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
        tts = gTTS(text=text, lang='en', tld='co.uk')
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
            {"role": "system", "content": "You are a helpful, smart, and friendly AI assistant. Answer questions directly and clearly."}
        ]
        for m in conversation_history[-6:]:
            messages_payload.append({"role": m["role"], "content": m["content"]})
            
        # Using production flagship model 'llama-3.3-70b-versatile'
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload,
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error connecting to coach: {str(e)}"

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Coach Workspace")
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
# FIXED: Added correct colon structure to prevent compilation execution failure
if st.session_state.active_idx >= len(st.session_state.chats):
    st.session_state.active_idx = 0

active_chat = st.session_state.chats[st.session_state.active_idx]

st.title(f"Fluency Coach: {active_chat.get('name', 'Chat')}")

# Render message history cleanly
if "messages" in active_chat and active_chat["messages"]:
    for msg in active_chat["messages"]:
        avatar_icon = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])
else:
    st.caption("This conversation is empty. Talk or type below!")

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

audio_file = st.audio_
