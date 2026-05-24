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
    layout="centered"
)

apply_custom_theme()

st.title("Fluency Coach")
st.write("### Interactive AI Speaking Companion")

# =========================================================
# SQLITE DATABASE ENGINE (Saves history permanently)
# =========================================================
DB_FILE = "coach_database.db"

def init_db():
    """Creates the chat table if it doesn't exist yet."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chats (
            chat_id TEXT,
            messages TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def get_all_chat_ids():
    """Retrieves all chat room names from the database."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT chat_id FROM chats ORDER BY updated_at DESC")
    rows = c.fetchall()
    conn.close()
    return [row[0] for row in rows]

def load_db_chat_history(chat_id):
    """Loads text messages for a specific chat room."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT messages FROM chats WHERE chat_id = ?", (chat_id,))
    row = c.fetchone()
    conn.close()
    
    if row:
        return json.loads(row[0])
    return [
        {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}
    ]

def save_db_chat_history(chat_id, history):
    """Saves or updates a chat room's log in the database."""
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Check if the room already exists
    c.execute("SELECT 1 FROM chats WHERE chat_id = ?", (chat_id,))
    exists = c.fetchone()
    
    messages_json = json.dumps(history, ensure_ascii=False)
    
    if exists:
        c.execute("UPDATE chats SET messages = ?, updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?", (messages_json, chat_id))
    else:
        c.execute("INSERT INTO chats (chat_id, messages) VALUES (?, ?)", (chat_id, messages_json))
        
    conn.commit()
    conn.close()

def delete_db_chat(chat_id):
    """Removes a chat room from the database storage."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM chats WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()

# Initialize basic functional states
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# Scan database records to build the sidebar room list
db_rooms = get_all_chat_ids()

if not db_rooms:
    default_room_title = "Primary Chat Room"
    save_db_chat_history(default_room_title, [
        {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}
    ])
    db_rooms = [default_room_title]

# Safe cross-refresh fallback checks
if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in db_rooms:
    st.session_state.current_chat_id = db_rooms[0]

# Keep memory array linked up to database records
st.session_state.chat_history = load_db_chat_history(st.session_state.current_chat_id)

# Profile Avatar Images
ROBOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"

# =========================================================
# SIDEBAR CONTROL PANEL (The ChatGPT Experience)
# =========================================================
with st.sidebar:
    st.header("Coach Workspace")
    
    # 1. New Chat Room Generation
    if st.button("➕ New Chat", use_container_width=True):
        from datetime import datetime
        generated_room_id = f"Chat {datetime.now().strftime('%b%d-%H%M%S')}"
        initial_greeting = [
            {"role": "coach", "content": "Hello! Let's start a brand new conversation. Tap the microphone below or type a message to start!"}
        ]
        save_db_chat_history(generated_room_id, initial_greeting)
        st.session_state.current_chat_id = generated_room_id
        st.session_state.chat_history = initial_greeting
        st.session_state.autoplay_audio_data = None
        st.rerun()

    st.markdown("---")
    st.subheader("Your Conversations")
    
    try:
        active_dropdown_index = db_rooms.index(st.session_state.current_chat_id)
    except ValueError:
        active_dropdown_index = 0

    # 2. Historical Chat List Dropdown
    selected_room_name = st.selectbox(
        "Select a conversation:",
        options=db_rooms,
        index=active_dropdown_index
    )
    
    if selected_room_name != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_room_name
        st.session_state.chat_history = load_db_chat_history(selected_room_name)
        st.session_state.autoplay_audio_data = None
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 3. Clear/Remove Database Record Entry
    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        delete_db_chat(st.session_state.current_chat_id)
        # Clear out current memory tokens to trigger a fallback selection
        if "current_chat_id" in st.session_state:
            del st.session_state.current_chat_id
        st.session_state.autoplay_audio_data = None
        st.rerun()

GROQ_API_KEY = "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"

# Render Active Message Stream
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=ROBOT_AVATAR):
            st.markdown(message["content"])

# Audio Autoplay Engine
if st.session_state.autoplay_audio_data:
    st.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)

st.markdown("<br>", unsafe_allow_html=True)

def get_coach_response(text_payload):
    messages_payload = [
        {
            "role": "system",
            "content": """You are an engaging, supportive, and highly advanced English language coach for kids. 
            Provide a balanced, medium-length educational response. 
            Do not give an endless or very long answer, and do not make it too short. Aim for a solid paragraph.
            Explain concepts clearly, provide 1 or 2 examples in quotation marks, and keep it easy to understand. 
            Always close your response with one simple, engaging follow-up question to keep the conversation moving."""
        }
    ]
    
    for msg in st.session_state.chat_history:
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

# User Action Panel
voice_col, stop_col = st.columns([1, 1])

with voice_col:
    st.markdown('<p class="control-label">🎙️ Voice Chat:</p>', unsafe_allow_html=True)
    audio_source = mic_recorder(
        start_prompt="Speak 🎤",
        stop_prompt="Submit 🔇",
        key="recorder"
    )

with stop_col:
    st.markdown('<p class="control-label">🛑 Stop Sound:</p>', unsafe_allow_html=True)
    if st.button("Stop Audio 🔇", use_container_width=True):
        st.session_state.autoplay_audio_data = None
        st.rerun()

# 1. Keyboard Text Messaging
text_input = st.chat_input("Type your message here...")
if text_input:
    st.session_state.chat_history.append({"role": "user", "content": text_input})
    save_db_chat_history(st.session_state.current_chat_id, st.session_state.chat_history)
    with st.spinner("Thinking..."):
        coach_reply = get_coach_response(text_input)
        st.session_state.chat_history.append({"role": "coach", "content": coach_reply})
        save_db_chat_history(st.session_state.current_chat_id, st.session_state.chat_history)
        
        audio_data = text_to_speech_bytes(coach_reply)
        if audio_data:
            st.session_state.autoplay_audio_data = audio_data
        st.rerun()

# 2. Microphone Audio Messaging
if audio_source and "bytes" in audio_source:
    audio_bytes = audio_source["bytes"]
    if audio_bytes:
        audio_hash = hashlib.md5(audio_bytes).hexdigest()
        if st.session_state.last_processed_audio != audio_hash:
            with st.spinner("Processing speech..."):
                try:
                    st.session_state.last_processed_audio = audio_hash
                    files = {
                        "file": ("speech.wav", audio_bytes, "audio/wav"),
                        "model": (None, "whisper-large-v3-turbo"),
                        "language": (None, "en") 
                    }
                    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                    whisper_response = requests.post(
                        "https://api.groq.com/openai/v1/audio/transcriptions",
                        headers=headers,
                        files=files
                    )
                    user_text = whisper_response.json().get("text", "")
                    
                    if user_text.strip():
                        st.session_state.chat_history.append({"role": "user", "content": user_text})
                        save_db_chat_history(st.session_state.current_chat_id, st.session_state.chat_history)
                        coach_reply = get_coach_response(user_text)
                        st.session_state.chat_history.append({"role": "coach", "content": coach_reply})
                        save_db_chat_history(st.session_state.current_chat_id, st.session_state.chat_history)
                        
                        audio_data = text_to_speech_bytes(coach_reply)
                        if audio_data:
                            st.session_state.autoplay_audio_data = audio_data
                        st.rerun()
                except Exception as e:
                    st.error("Audio Processing Error. Please try speaking again.")
