import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3
import json
from io import BytesIO
from gtts import gTTS
import requests
import hashlib

# --- 1. Styling ---
st.set_page_config(layout="centered", page_title="Fluency Coach")
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: url("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
        background-size: 80px;
    }
    h1, h2, h3, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Database Engine ---
DB_FILE = "coach_data.db"
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Force reset to fix the persistent OperationalError
    c.execute('DROP TABLE IF EXISTS conversations')
    c.execute('''CREATE TABLE conversations (
                    room_id TEXT PRIMARY KEY, 
                    history_json TEXT, 
                    is_pinned INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Initialize only if the file is fresh (this prevents loop crashes)
try:
    conn = sqlite3.connect(DB_FILE)
    conn.execute("SELECT is_pinned FROM conversations LIMIT 1")
    conn.close()
except:
    init_db()

# --- 3. Sidebar ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.active_id = f"Chat_{hashlib.md5(str(st.time()).encode()).hexdigest()[:5]}"
        st.rerun()

    st.subheader("Your Chats")
    conn = sqlite3.connect(DB_FILE)
    chats = conn.execute("SELECT room_id, is_pinned FROM conversations").fetchall()
    conn.close()
    
    for room_id, pinned in chats:
        if st.button(f"{'📌' if pinned else ''} {room_id}"):
            st.session_state.active_id = room_id
            st.rerun()

# --- 4. Main Chat Interface ---
st.title("Fluency Coach")
if "active_id" not in st.session_state:
    st.session_state.active_id = "General"

# Input Handling
text_input = st.chat_input("Type your message here...")
if text_input:
    st.write(f"You said: {text_input}") # Placeholder for your LLM logic

c1, c2 = st.columns(2)
with c1:
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="rec")
with c2:
    if st.button("Stop Audio 🔇"): st.rerun()
