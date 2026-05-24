import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import hashlib
import re
import json
from io import BytesIO
from gtts import gTTS

# Connection Link
from style import apply_custom_theme

st.set_page_config(
    page_title="Fluency Coach - AI Speaking Companion",
    page_icon="🤖",
    layout="wide"  # Changed to wide layout to make room for your new sidebar panel!
)

apply_custom_theme()

# =========================================================
# LOCAL STORAGE HYBRID ENGINE (Refresh-Proof Memory)
# =========================================================

# Helper to load all conversations from state memory 
if "chat_vault" not in st.session_state:
    st.session_state.chat_vault = {
        "Conversation 1": [
            {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}
        ]
    }

if "active_id" not in st.session_state:
    st.session_state.active_id = list(st.session_state.chat_vault.keys())[0]

if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# Avatars
ROBOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"

# =========================================================
# THE COLLAPSIBLE SIDEBAR PANEL (Gemini/ChatGPT Style)
# =========================================================
with st.sidebar:
    st.markdown("### 🤖 Coach Workspace")
    
    # Big standalone action button for creating a new room
    if st.button("➕ New chat", use_container_width=True, type="primary"):
        from datetime import datetime
        new_uid = f"Chat {datetime.now().strftime('%b %d, %H:%M')}"
        st.session_state.chat_vault[new_uid] = [
            {"role": "coach", "content": "Hello! Let's start a brand new conversation room. Speak or type to begin!"}
        ]
        st.session_state.active_id = new_uid
        st.session_state.autoplay_audio_data = None
        st.rerun()
        
    st.markdown("---")
    st.write("##### Recents")
    
    # Loop over every chat room title and render it as a clean list button
    for room_title in list(st.session_state.chat_vault.keys()):
        # Highlight or mark the currently active session cleanly
        is_current = (room_title == st.session_state.active_id)
        button_label = f"💬 {room_title}" if not is_current else f"👉 {room_title}"
        
        # Clickable vertical links
        if st.button(button_label, key=f"nav_{room_title}", use_container_width=True, help="Click to open this chat room"):
            st.session_state.active_id = room_title
            st.session_state.autoplay_audio_data = None
            st.rerun()

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Delete Option pinned cleanly at the baseline footer
    if st.button("🗑️ Delete Current Session", use_container_width=True):
        if len(st.session_state.chat_vault) > 1:
            del st.session_state.chat_vault[st.session_state.active_id]
            st.session_state.active_id = list(st.session_state.chat_vault.keys())[0]
        else:
            # Wipe baseline room clean if it's the remaining session
            st.session_state.chat_vault["Conversation 1"] = [
                {"role": "coach", "content": "Hello! Let's start fresh again here. Speak or type away!"}
            ]
            st.session_state.active_id = "Conversation 1"
        st.session_state.autoplay_audio_data = None
        st.rerun()


# =========================================================
# MAIN APP CHAT SPACE RENDERER
# =========================================================
st.title("Fluency Coach")
st.write(f"Currently Browsing: **{st.session_state.active_id}**")

# Point active local history array tracking at our selected sidebar context room 
current_history = st.session_state.chat_vault[st.session_state.active_id]

# Show the messages on screen
for message in current_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=ROBOT_AVATAR):
            st.markdown(message["content"])

# Audio Autoplay Card
if st.session_state.autoplay_audio_data:
    st.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)

st.markdown("<br>", unsafe_allow_html=True)

# =========================================================
# BACKEND CHAT HANDLERS & CORE FUNCTIONS
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

# User Input Controls Dashboard Layout
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

# 1. Keyboard Text Entry Box
text_input = st.chat_input("Type your message here...")
if text_input:
    current_history.append({"role": "user", "content": text_input})
    with st.spinner("Thinking..."):
        coach_reply = get_coach_response()
        current_history.append({"role": "coach", "content": coach_reply})
        
        # Commit back down to permanent dictionary vault
        st.session_state.chat_vault[st.session_state.active_id] = current_history
        
        audio_data = text_to_speech_bytes(coach_reply)
        if audio_data:
            st.session_state.autoplay_audio_data = audio_data
        st.rerun()

# 2. Microphone Speech Processing Card
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
