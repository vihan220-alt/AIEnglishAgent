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
# DATABASE STORAGE ENGINE (With Renaming, Pinning & Deleting)
# =========================================================
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            room_id TEXT PRIMARY KEY,
            history_json TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_pinned INTEGER DEFAULT 0
        )
    ''')
    try:
        c.execute("ALTER TABLE conversations ADD COLUMN is_pinned INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass 
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

def delete_room_from_db(room_id):
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
    
    # Create New Session
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
    
    # List available sessions
    for room_title, pin_status in existing_rooms_data:
        is_current = (room_title == st.session_state.active_id)
        
        # Display special prefix graphics for quick context tracking
        if is_current:
            prefix = "📌 👉" if pin_status == 1 else "👉"
        else:
            prefix = "📌 💬" if pin_status == 1 else "💬"
            
        button_label = f"{prefix} {room_title}"
        
        if st.button(button_label, key=f"nav_{room_title}", use_container_width=True):
            st.session_state.active_id = room_title
            st.session_state.autoplay_audio_data = None
            st.rerun()
            
        # The Three-Dots Dropdown Options Expander Panel
        if is_current:
            with st.expander("⚙️ Chat Settings Menu", expanded=False):
                # 1. PIN ACTION BUTTON
                pin_action_text = "📌 Unpin Session" if pin_status == 1 else "📌 Pin to Top List"
                if st.button(pin_action_text, key=f"pin_{room_title}", use_container_width=True):
                    toggle_pin_room(room_title, pin_status)
                    st.rerun()
                
                # 2. RENAME CONFIGURATION FIELD
                new_title_val = st.text_input("Edit Title Text:", value=room_title, key=f"edit_{room_title}")
                if st.button("💾 Rename Title", key=f"save_{room_title}", use_container_width=True):
                    if new_title_val.strip() and new_title_val.strip() != room_title:
                        rename_room(room_title, new_title_val.strip())
                        st.session_state.active_id = new_title_val.strip()
                        st.rerun()
                
                st.markdown("---")
                # 3. SECURE DELETION ENGINE
                allow_delete = st.checkbox("Confirm Deletion", key=f"check_{room_title}")
                if st.button("🗑️ Delete Chat Permanently", key=f"del_{room_title}", use_container_width=True, type="secondary"):
                    if allow_delete:
                        delete_room_from_db(room_title)
                        updated_rooms = get_all_rooms()
                        if updated_rooms:
                            st.session_state.active_id = updated_rooms[0][0]
                        else:
                            st.session_state.active_id = "Conversation 1"
                            save_room_history("Conversation 1", [{"role": "coach", "content": "Hello! Let's practice speaking English together. Tap the microphone below or type a message to start!"}])
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
GROQ_API_KEY = "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"

def get_coach_response():
    messages_payload = [
        {
            "role": "system",
            "content": """You are an engaging, supportive English language coach for kids.
            
            CRITICAL INSTRUCTION FOR SHORT GREETINGS: 
            If the user simply says 'hello', 'hi', 'hey', 'good morning', or a basic greeting, DO NOT write a long paragraph. Respond dynamically with a short, welcoming one-sentence greeting and ask them what they would like to talk about today.
            
            INSTRUCTION FOR PRACTICE QUESTIONS:
            If the user asks a language question or shares a story, provide a balanced, medium-length paragraph response explaining concepts clearly with examples, and always close with one simple follow-up question."""
        }
    ]
    for msg in current_history:
        role_map = "user" if msg["role"] == "user" else "assistant"
        messages_payload.append({"role": role_map, "content": msg["content"]})
        
    llm_payload = {"model": "llama-3.3-70b-versatile", "messages": messages_payload}
    llm_headers = {"Content-Type": "application/json", "Authorization": f"Bearer {GROQ_API_KEY}"}
    
    llm_response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=llm_headers, json=llm_payload)
    return llm_response.json()["choices"][0]["message"]["content"]

def text_to_speech_bytes(text_payload):
    try:
        sentences = re.split(r'(?<=[.!?])\s+|\n+', text_payload)
        chunks = [st_item.strip() for st_item in sentences if st_item.strip()]
        
        combined_fp = BytesIO()
        for chunk in chunks:
            tts_chunk = gTTS(text=chunk, lang='en', slow=False)
            chunk_fp = BytesIO()
            tts_chunk.write_to_fp(chunk_fp)
            chunk_fp.seek(0)
            combined_fp.write(chunk_fp.read())
            
        combined_fp.seek(0)
        return combined_fp.read()
    except Exception as e:
        return None

# User Interaction Interface Columns
voice_col, stop_col = st.columns([1, 1])
with voice_col:
    st.write("**🎙️ Voice Input:**")
    audio_source = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="recorder")

with stop_col:
    st.write("**🛑 Controls:**")
    if st.button("Stop Audio 🔇", use_container_width=True):
        st.session_state.autoplay_audio_data = None
        st.rerun()

# Text message handler
text_input = st.chat_input("Type your message here...")
if text_input:
    current_history.append({"role": "user", "content": text_input})
    save_room_history(st.session_state.active_id, current_history)
    with st.spinner("Thinking..."):
        coach_reply = get_coach_response()
        current_history.append({"role": "coach", "content": coach_reply})
        save_room_history(st.session_state.active_id, current_history)
        st.session_state.autoplay_audio_data = None
        st.rerun()

# Mic voice handler
if audio_source and "bytes" in audio_source and audio_source["bytes"]:
    audio_bytes = audio_source["bytes"]
    audio_hash = hashlib.md5(audio_bytes).hexdigest()
    if st.session_state.last_processed_audio != audio_hash:
        st.session_state.last_processed_audio = audio_hash
        with st.spinner("Processing speech..."):
            try:
                whisper_files = {"file": ("speech.wav", audio_bytes, "audio/wav"), "model": (None, "whisper-large-v3-turbo"), "language": (None, "en")}
                whisper_headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                whisper_response = requests.post("https://api.groq.com/openai/v1/audio/transcriptions", headers=whisper_headers, files=whisper_files)
                user_text = whisper_response.json().get("text", "")
                
                if user_text.strip():
                    current_history.append({"role": "user", "content": user_text})
                    save_room_history(st.session_state.active_id, current_history)
                    coach_reply = get_coach_response()
                    current_history.append({"role": "coach", "content": coach_reply})
                    save_room_history(st.session_state.active_id, current_history)
                    
                    audio_data = text_to_speech_bytes(coach_reply)
                    if audio_data:
                        st.session_state.autoplay_audio_data = audio_data
                    st.rerun()
            except Exception as e:
                st.error("Audio Processing Error.")
