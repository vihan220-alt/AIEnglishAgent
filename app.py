import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import hashlib
import re
import json
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
# PERSISTENT STORAGE ENGINE (Saves history across refreshes)
# =========================================================
BACKUP_FILE = "chat_backup.json"

def load_saved_history():
    """Loads chat history from the backup file if it exists."""
    if os.path.exists(BACKUP_FILE):
        try:
            with open(BACKUP_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Default starting message if no backup exists
    return [
        {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}
    ]

def save_current_history():
    """Saves the current session chat history to the backup file."""
    try:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

# Initialize history from backup file instead of resetting on refresh
if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_saved_history()

if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

GROQ_API_KEY = "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"

# Verified high-quality web illustration image URLs
ROBOT_AVATAR_URL = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR_URL = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"

# Sidebar Workspace Controls
with st.sidebar:
    st.header("Coach Workspace")
    st.info("This secure dashboard uses artificial intelligence to evaluate speech syntax, pronunciation, and flow in real time.")
    st.caption("Tip: Click 'Speak', say a sentence, and click 'Submit'.")
    
    st.markdown("---")
    # Clear Chat Button to reset the saved file manually
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        if os.path.exists(BACKUP_FILE):
            os.remove(BACKUP_FILE)
        st.session_state.chat_history = [
            {"role": "coach", "content": "Hello! Let's start fresh. Tap the microphone below or type a message to start!"}
        ]
        st.session_state.autoplay_audio_data = None
        st.rerun()

# Render Conversation Timeline
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_AVATAR_URL):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=ROBOT_AVATAR_URL):
            st.markdown(message["content"])

# AUTOPLAY ENGINE
if st.session_state.autoplay_audio_data:
    st.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)

st.markdown("<br>", unsafe_allow_html=True)

def get_coach_response(text_payload):
    messages_payload = [
        {
            "role": "system",
            "content": """You are an engaging, supportive, and highly advanced English language coach for kids. 
            Provide a balanced, medium-length educational response. 
            Do not give an endless or very long answer, and do not make it too short (like 2 sentences). Aim for a solid, medium paragraph.
            Explain the requested grammar, vocabulary, or speaking concept clearly, provide 1 or 2 clear examples in quotation marks, and keep it easy to understand. 
            Always close your response with one simple, engaging follow-up question to keep the conversation moving."""
        }
    ]
    
    for msg in st.session_state.chat_history:
        role_map = "user" if msg["role"] == "user" else "assistant"
        messages_payload.append({"role": role_map, "content": msg["content"]})
        
    llm_payload = {
