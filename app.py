import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import hashlib
import re
import json
import sqlite3
from io import BytesIO
from gtts import gTTS

# Connection Link
from style import apply_custom_theme

st.set_page_config(
    page_title="Fluency Coach - AI Speaking Companion",
    page_icon="🤖",
    layout="centered"
)

apply_custom_theme()

# =========================================================
# DATABASE STORAGE ENGINE (With Renaming Support)
# =========================================================
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            room_id TEXT PRIMARY KEY,
            history_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_all_rooms():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT room_id FROM conversations ORDER BY updated_at DESC")
    rooms = [row[0] for row in c.fetchall()]
    conn.close()
    return rooms

def load_room_history(room_id):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT history_json FROM conversations WHERE room_id = ?", (room_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return [
        {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}
    ]

def save_room_history(room_id, history):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    history_string = json.dumps(history, ensure_ascii=False)
    c.execute('''
        INSERT INTO conversations (room_id, history_json, updated_at)
        VALUES (?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(room_id) DO UPDATE SET
            history_json = excluded.history_json,
            updated_at = CURRENT_TIMESTAMP
    ''', (room_id, history_string))
    conn.commit()
    conn.close()

def rename_room(old_id, new_id):
    if not new_id.strip() or old_id == new_id:
        return
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("UPDATE conversations SET room_id = ? WHERE room_id = ?", (new_id, old_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass 
    conn.close()

def delete_room(room_id):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE room_id = ?", (room_id,))
    conn.commit()
    conn.close()

# =========================================================
# SYSTEM CONTROL RUNTIME STATES
# =========================================================
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

existing_rooms = get_all_rooms()

if not existing_rooms:
    save_room_history("Conversation 1", [{"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}])
    existing_rooms = ["Conversation 1"]

if "active_id" not in st.session_state or st.session_state.active_id not in existing_rooms:
    st.session_state.active_id = existing_rooms[0]

current_history = load_room_history(st.session_state.active_id)

ROBOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"

# =========================================================
# THE SIDEBAR MANAGEMENT INTERFACE
# =========================================================
with st.sidebar:
    st.markdown("### 🤖 Coach Workspace")
    
    # 1. SELECT NEW CHAT Button
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        from datetime import datetime
        new_uid = f"Chat {datetime.now().strftime('%b %d, %H:%M')}"
        save_room_history(new_uid, [{"role": "coach", "content": "Hello! Let's start a brand new conversation room. Speak or type to begin!"}])
        st.session_state.active_id = new_uid
        st.session_state.autoplay_audio_data = None
        st.rerun()
        
    st.markdown("---")
    st.write("##### Recents")
    
    # 2. SELECT ANOTHER CHAT List Selection
    for room_title in existing_rooms:
        is_current = (room_title == st.session_state.active_id)
        button_label = f"👉 {room_title}" if is_current else f"💬 {room_title}"
        
        if st.button(button_label, key=f"nav_{room_title}", use_container_width=True):
            st.session_state.active_id = room_title
            st.session_state.autoplay_audio_data = None
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("##### 🛠️ Current Chat Actions")
    
    # 3. RENAME ACTIVE CHAT Input Tool
    new_name_input = st.text_input("Rename Current Chat:", value=st.session_state.active_id)
    if st.button("💾 Save Title Name", use_container_width=True):
        if new_name_input.strip() and new_name_input != st.session_state.active_id:
            rename_room(st.session_state.active_id, new_name_input.strip())
            st.session_state.active_id = new_name_input.strip()
            st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    # 4. DELETE ACTIVE CHAT Button Tool
    if st.button("🗑️ Delete Current Session", use_container_width=True, type="secondary"):
        delete_room(st.session_state.active_id)
        remaining = get_all_rooms()
        if remaining:
            st.session_state.active_id = remaining[0]
        else:
            st.session_state.active_id = "Conversation 1"
            save_room_history("Conversation 1", [{"role": "coach", "content": "Hello! Let's start fresh again here. Speak or type away!"}])
        st.session_state.autoplay_audio_data = None
        st.rerun()


# =========================================================
# CHAT ROOM SURFACE DISPLAY
# =========================================================
st.title("Fluency Coach")
st.write(f"Active Session: **{st.session_state.active_id}**")

for message in current_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=ROBOT_AVATAR):
            st.markdown(message["content"])

if st.session_state.autoplay_audio_data:
    st.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)

# =========================================================
# BACKEND API CONNECTIONS
# =========================================================
GROQ_API
