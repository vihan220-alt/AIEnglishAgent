import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import hashlib
import re
import json
import sqlite3
from io import BytesIO
from gtts import gTTS
from style import apply_custom_theme

# Page Setup
st.set_page_config(page_title="Fluency Coach", page_icon="🤖", layout="centered")
apply_custom_theme()

# --- Database Setup ---
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (room_id TEXT PRIMARY KEY, history_json TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, is_pinned INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def get_all_rooms():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT room_id, is_pinned FROM conversations ORDER BY is_pinned DESC, updated_at DESC")
    rooms = c.fetchall()
    conn.close()
    return rooms

def load_room_history(room_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT history_json FROM conversations WHERE room_id = ?", (room_id,))
    row = c.fetchone()
    conn.close()
    if row: return json.loads(row[0])
    return [{"role": "coach", "content": "Hello! I am your language partner. Let's practice! How are you feeling today?"}]

def save_room_history(room_id, history):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT OR REPLACE INTO conversations (room_id, history_json, updated_at) 
                 VALUES (?, ?, CURRENT_TIMESTAMP)''', (room_id, json.dumps(history)))
    conn.commit()
    conn.close()

def delete_room(room_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE room_id = ?", (room_id,))
    conn.commit()
    conn.close()

# --- Runtime State ---
init_db()
if "active_id" not in st.session_state:
    rooms = get_all_rooms()
    st.session_state.active_id = rooms[0][0] if rooms else "Chat 1"

# --- Sidebar ---
with st.sidebar:
    st.markdown("### 🤖 Coach Workspace")
    if st.button("➕ New chat"):
        new_id = f"Chat {len(get_all_rooms()) + 1}"
        save_room_history(new_id, [{"role": "coach", "content": "Hello! Let's start a new chat."}])
        st.session_state.active_id = new_id
        st.rerun()
    
    for r_id, pinned in get_all_rooms():
        if st.button(f"{'📌 ' if pinned else ''}{r_id}"):
            st.session_state.active_id = r_id
            st.rerun()

# --- Chat Interface ---
st.title("Fluency Coach")
history = load_room_history(st.session_state.active_id)

for msg in history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type here..."):
    history.append({"role": "user", "content": prompt})
    # Add API call logic for coach response here
    save_room_history(st.session_state.active_id, history)
    st.rerun()

# --- Voice & Cleanup ---
col1, col2 = st.columns(2)
with col1:
    audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with col2:
    if st.button("Delete This Chat"):
        delete_room(st.session_state.active_id)
        st.rerun()
