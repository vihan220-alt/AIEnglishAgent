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
# DATABASE STORAGE ENGINE (With Renaming & Pinning Support)
# =========================================================
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Ensure tables and columns exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            room_id TEXT PRIMARY KEY,
            history_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_pinned INTEGER DEFAULT 0
        )
    ''')
    # Guard case if column is_pinned doesn't exist yet in an older database file
    try:
        c.execute("ALTER TABLE conversations ADD COLUMN is_pinned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass # Column already exists
    conn.commit()
    conn.close()

def get_all_rooms():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Order first by pinned chats, then by latest updated time
    c.execute("SELECT room_id, is_pinned FROM conversations ORDER BY is_pinned DESC, updated_at DESC")
    rooms = c.fetchall()
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

def toggle_pin_room(room_id, current_pin_status):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    new_status = 1 if current_pin_status == 0 else 0
    c.execute("UPDATE conversations SET is_pinned = ? WHERE room_id = ?", (new_status, room_id))
    conn.commit()
    conn.close()

# =========================================================
# SYSTEM CONTROL RUNTIME STATES
# =========================================================
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

existing_rooms_data = get_all_rooms()

if not existing_rooms_data:
    save_room_history("Conversation 1", [{"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}])
    existing_rooms_data = [("Conversation 1", 0)]

room_ids_list = [row[0] for row in existing_rooms_data]

if "active_id" not in st.session_state or st.session_state.active_id not in room_ids_list:
    st.session_state.active_id = room_ids_list[0]

current_history = load_room_history(st.session_state.active_id)

ROBOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"

# Find if the current active room is pinned
is_currently_pinned = 0
for r_id, p_val in existing_rooms_data:
    if r_id == st.session_state.active_id:
        is_currently_pinned = p_val
        break

# =========================================================
# THE SIDEBAR MANAGEMENT INTERFACE
# =========================================================
with st.sidebar:
    st.markdown("### 🤖 Coach Workspace")
    
    # 1. NEW CHAT CREATOR
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        from datetime import datetime
        time_stamp = datetime.now().strftime('%b %d, %H:%M')
        new_uid = "Chat " + str(time_stamp)
        save_room_history(new_uid, [{"role": "coach", "content": "Hello! Let's start a brand new conversation room. Speak or type to begin!"}])
        st.session_state.active_id = new_uid
        st.session_state.autoplay_audio_data = None
        st.rerun()
        
    st.markdown("---")
    st.write("##### Recents")
    
    # 2. SELECT RECENT CHAT ROOMS (Displays Pinned Chats First)
    for room_title, pin_status in existing_rooms_data:
        is_current = (room_title == st.session_state.active_id)
        
        # Determine prefix icon based on pinned vs standard status
        if is_current:
            prefix = "📌 👉" if pin_status == 1 else "👉"
        else:
            prefix = "📌 💬" if pin_status == 1 else "💬"
            
        button_label = f"{prefix} {room_title}"
        
        if st.button(button_label, key=f"
