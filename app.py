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
# DATABASE STORAGE ENGINE (With Pinning & Renaming Support)
# =========================================================
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Table includes columns to track pinned state and custom titles
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            room_id TEXT PRIMARY KEY,
            history_json TEXT,
            is_pinned INTEGER DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_all_rooms():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Pinned chats always stay at the top, followed by most recent updates
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
        {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together."}
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
        pass # Handle duplicate names safely
    conn.close()

def toggle_pin_room(room_id, current_status):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    new_status = 1 if current_status == 0 else 0
    c.execute("UPDATE conversations SET is_pinned = ? WHERE room_id = ?", (new_status, room_id))
    conn.commit()
    conn.close()

def delete_room(room_id):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE room_id = ?", (room_id,))
    conn.commit()
    conn.close()

# =========================================================
# STATE APP CONTROL INITIALIZATION
# =========================================================
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

existing_rooms_data = get_all_rooms()

if not existing_rooms_data:
    save_room_history("Conversation 1", [{"role": "coach", "content": "Hello! Let's practice speaking English together."}])
    existing_rooms_data = [("Conversation 1", 0)]

room_names = [row[0] for row in existing_rooms_data]

if "active_id" not in st.session_state or st.session_state.active_id not in room_names:
    st.session_state.active_id = room_names[0]

current_history = load_room_history(st.session_state.active_id)

ROBOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"

# =========================================================
# THE ADVANCED GEMINI-STYLE SIDEBAR NAV PANEL
# =========================================================
with st.sidebar:
    st.markdown("### 🤖 Coach Workspace")
    
    # ACTION 1: SELECT NEW CHAT Button
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        from datetime import datetime
        new_uid = f"Chat {datetime.now().strftime('%b %d, %H:%M')}"
        save_room_history(new_uid, [{"role": "coach", "content": "Hello! Let's start a brand new conversation room. Speak or type to begin!"}])
        st.session_state.active_id = new_uid
        st.session_state.autoplay_audio_data = None
        st.rerun()
        
    st.markdown("---")
    st.write("##### Recents")
    
    # Render all chat choices dynamically with custom tool buttons
    for room_title, is_pinned in existing_rooms_data:
        is_current = (room_title == st.session_state.active_id)
        
        # Display indicator icons based on active or pinned status
        prefix = "📌" if is_pinned else "💬"
        if is_current:
            prefix = "👉"
            
        # ACTION 2: SELECT ANOTHER CHAT Button
        if st.button(f"{prefix} {room_title}", key=f"nav_{room_title}", use_container_width=True):
            st.session_state.active_id = room_title
            st.session_state.autoplay_audio_data = None
            st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.write("##### 🛠️ Current Chat Actions")
    
    # ACTION 3: RENAME CURRENT ACTIVE CHAT
    new_name_input = st.text_input("Rename Chat Title:", value=st.session_state.active_id)
    if st.button("💾 Save New Title", use_container_width=True):
        if new_name_input.strip() and new_name_input != st.session_state.active_id:
            rename_room(st.session_state.active_id, new_name_input.strip())
            st.session_state.active_id = new_name_input.strip()
            st.rerun()
            
    # Find pinned state info for active chat session
    active_pin_status = 0
    for r_name, p_status in existing_rooms_data:
        if r_name == st.session_state.active_id:
            active_pin_status = p_status
            break

    # ACTION 4: PIN / UNPIN CHAT SESSION Toggle
    pin_label = "📌 Pin Chat to Top" if not active_pin_status else "📍 Unpin Chat Session"
    if st.button(pin_label, use_container_width=True):
        toggle_pin_room(st.session_state.active_id, active_pin_status)
        st.rerun()
        
    # ACTION 5: DELETE CHAT SESSION Button
    if st.button("🗑️ Delete Current Session", use_container_width=True, type="secondary"):
        delete_room(st.session_state.active_id)
        updated_rooms = get_all_rooms()
        if updated_rooms:
            st.session_state.active_id = updated_rooms[0][0]
        else:
            st.session_state.active_id = "Conversation 1"
            save_room_history("Conversation 1", [{"role": "coach", "content": "Hello! Let's start fresh again here. Speak or type away!"}])
        st.session_state.autoplay_audio_data = None
        st.rerun()


# =========================================================
# MAIN APP DISPLAY SURFACE
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
# API NETWORK BACKEND
# =========================================================
GROQ_API_KEY = "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"

def get_coach_response():
    messages_payload = [
        {
            "role": "system",
            "content": """You are an engaging English language coach for kids. 
            Provide a balanced, medium-length paragraph response. Explain concepts clearly. 
            Always close your response with one simple, engaging follow-up question."""
        }
    ]
    for msg in current_history:
        messages_payload.append({"role": "user" if msg["role"] == "user" else "assistant", "content": msg["content"]})
        
    llm_payload = {"model": "llama-3.3-70b-versatile", "messages": messages_payload}
    llm_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"}
    
    llm_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=llm_headers, json=llm_payload)
    return llm_response.json()["choices"][0]["message"]["content"]

def text_to_speech_bytes(text_payload):
    try:
        sentences = re.split(r'(?<=[.!?])\s+|\n+', text_payload)
        chunks = [s.strip() for s in sentences if s.strip()]
        combined_fp = BytesIO()
        for chunk in chunks:
            tts_chunk = gTTS(text=chunk, lang='en', slow=False)
            chunk_fp = BytesIO()
            tts_chunk.write_to_fp(chunk_fp)
            chunk_fp.seek(0)
            combined_fp.
