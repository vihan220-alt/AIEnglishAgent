import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import hashlib
import re
import json
import sqlite3
import os
from io import BytesIO
from gtts import gTTS

# Connection Link
from style import apply_custom_theme

st.set_page_config(
    page_title="Fluency Coach - AI Speaking Companion",
    page_icon="🤖",
    layout="centered"  # Keeps the chat layout centered and beautiful
)

apply_custom_theme()

# =========================================================
# SQLITE DATABASE STORAGE (Refresh-Proof Memory)
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

def delete_room(room_id):
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE room_id = ?", (room_id,))
    conn.commit()
    conn.close()

# =========================================================
# SYSTEM STATES
# =========================================================
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

existing_rooms = get_all_rooms()

if not existing_rooms:
    default_title = "Conversation 1"
    initial_log = [
        {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}
    ]
    save_room_history(default_title, initial_log)
    existing_rooms = [default_title]

if "active_id" not in st.session_state or st.session_state.active_id not in existing_rooms:
    st.session_state.active_id = existing_rooms[0]

current_history = load_room_history(st.session_state.active_id)

ROBOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"

# =========================================================
# THE GEMINI SIDEBAR WORKSPACE PANEL
# =========================================================
with st.sidebar:
    st.markdown("### 🤖 Coach Workspace")
    
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        from datetime import datetime
        new_uid = f"Chat {datetime.now().strftime('%b %d, %H:%M')}"
        fresh_intro = [
            {"role": "coach", "content": "Hello! Let's start a brand new conversation room. Speak or type to begin!"}
        ]
        save_room_history(new_uid, fresh_intro)
        st.session_state.active_id = new_uid
        st.session_state.autoplay_audio_data = None
        st.rerun()
        
    st.markdown("---")
    st.write("##### Recents")
    
    for room_title in existing_rooms:
        is_current = (room_title == st.session_state.active_id)
        button_label = f"👉 {room_title}" if is_current else f"💬 {room_title}"
        
        if st.button(button_label, key=f"nav_{room_title}", use_container_width=True):
            st.session_state.active_id = room_title
            st.session_state.autoplay_audio_data = None
            st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.button("🗑️ Delete Current Session", use_container_width=True):
        delete_room(st.session_state.active_id)
        remaining = get_all_rooms()
        if remaining:
            st.session_state.active_id = remaining[0]
        else:
            st.session_state.active_id = "Conversation 1"
            save_room_history("Conversation 1", [
                {"role": "coach", "content": "Hello! Let's start fresh again here. Speak or type away!"}
            ])
        st.session_state.autoplay_audio_data = None
        st.rerun()

# =========================================================
# CHAT INTERFACE SURFACE AREA
# =========================================================
st.title("Fluency Coach")
st.write(f"Currently Browsing: **{st.session_state.active_id}**")

for message in current_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=ROBOT_AVATAR):
            st.markdown(message["content"])

# Only shows and plays audio when microphone responses are triggered
if st.session_state.autoplay_audio_data:
    st.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# BACKEND API UTILITIES
# =========================================================
GROQ_API_KEY = "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"

def get_coach_response():
    messages_payload = [
        {
            "role": "system",
            "content": """You are an engaging, supportive, and highly advanced English language coach for kids. 
            Provide a balanced, medium-length educational response. Do not give a very long answer. Aim for a solid paragraph.
            Explain concepts clearly, provide 1 or 2 examples in quotation marks, and keep it easy to understand. 
            Always close your response with one simple, engaging follow-up question to keep the conversation moving."""
        }
    ]
    
    for msg in current_history:
        role_map = "user" if msg["role"] == "user" else "assistant"
        messages_payload.append({"role": role_map, "content": msg["content"]})
        
    llm_payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages_payload
    }
    
    llm_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GROQ_API_KEY}"
    }
    
    llm_response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=llm_headers,
        json=llm_payload
    )
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
            combined_fp.write(chunk_fp.read())
            
        combined_fp.seek(0)
        return combined_fp.read()
    except Exception as e:
        st.error(f"TTS Error: {e}")
    return None

# =========================================================
# USER CONTROL INPUT SYSTEM
# =========================================================
voice_col, stop_col = st.columns([1, 1])

with voice_col:
    st.write("**🎙️ Voice Input:**")
    audio_source = mic_recorder(
        start_prompt="Speak 🎤",
        stop_prompt="Submit 🔇",
        key="recorder"
    )

with stop_col:
    st.write("**🛑 Controls:**")
    if st.button("Stop Audio 🔇", use_container_width=True):
        st.session_state.autoplay_audio_data = None
        st.rerun()

# 1. Keyboard Input Box Processing (STAYS QUIET - NO TTS GENERATED)
text_input = st.chat_input("Type your message here...")
if text_input:
    current_history.append({"role": "user", "content": text_input})
    save_room_history(st.session_state.active_id, current_history)
    with st.spinner("Thinking..."):
        coach_reply = get_coach_response()
        current_history.append({"role": "coach", "content": coach_reply})
        save_room_history(st.session_state.active_id, current_history)
        
        # Clear any old audio so it does not speak when typing text
        st.session_state.autoplay_audio_data = None
        st.rerun()

# 2. Microphone Input Box Processing (GENERATES TTS VOICE AUDIO)
if audio_source and "bytes" in audio_source:
    audio_bytes = audio_source["bytes"]
    if audio_bytes:
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        if st.session_state.last_processed_audio != audio_hash:
            with st.spinner("Processing speech..."):
                try:
                    st.session_state.last_processed_audio = audio_hash
                    
                    whisper_files = {
                        "file": ("speech.wav", audio_bytes, "audio/wav"),
                        "model": (None, "whisper-large-v3-turbo"),
                        "language": (None, "en")
                    }
                    whisper_headers = {
                        "Authorization": f"Bearer {GROQ_API_KEY}"
                    }
                    
                    whisper_response = requests.post(
                        "https://api.groq.com/openai/v1/audio/transcriptions",
                        headers=whisper_headers,
                        files=whisper_files
                    )
                    user_text = whisper_response.json().get("text", "")
                    
                    if user_text.strip():
                        current_history.append({"role": "user", "content": user_text})
                        save_room_history(st.session_state.active_id, current_history)
                        coach_reply = get_coach_response()
                        current_history.append({"role": "coach", "content": coach_reply})
                        save_room_history(st.session_state.active_id, current_history)
                        
                        # Generates voice audio only for the microphone
                        audio_data = text_to_speech_bytes(coach_reply)
                        if audio_data:
                            st.session_state.autoplay_audio_data = audio_data
                        st.rerun()
                except Exception as e:
                    st.error("Audio Processing Error. Please try speaking again.")
