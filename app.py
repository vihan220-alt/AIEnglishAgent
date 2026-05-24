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
# CHATGPT-STYLE MULTI-CHAT STORAGE ENGINE
# =========================================================
CHATS_DIR = "saved_chats"
if not os.path.exists(CHATS_DIR):
    os.makedirs(CHATS_DIR)

def get_all_chats():
    """Returns a sorted list of all saved chat names (without extension)."""
    files = [f for f in os.listdir(CHATS_DIR) if f.endswith(".json")]
    chats = [os.path.splitext(f)[0] for f in files]
    return sorted(chats, reverse=True)

def load_chat_history(chat_id):
    """Loads a specific chat history file."""
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return [
        {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}
    ]

def save_chat_history(chat_id, history):
    """Saves the current conversation to its specific file."""
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=4)
    except Exception:
        pass

# Initialize tracking states safely
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# Get latest chat lists right away so they persist during a refresh
saved_chats_list = get_all_chats()

# If absolutely no previous chats exist, create a default timestamped room name
if not saved_chats_list:
    from datetime import datetime
    default_id = f"Chat {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
    saved_chats_list = [default_id]
else:
    default_id = saved_chats_list[0]

# REFRESH FIX: If current_chat_id disappears from memory on refresh, reload the last active chat smoothly
if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in saved_chats_list:
    st.session_state.current_chat_id = default_id

# REFRESH FIX: Always reload the text history corresponding to the persistent active room
st.session_state.chat_history = load_chat_history(st.session_state.current_chat_id)

# Verified high-quality web illustration image URLs
ROBOT_AVATAR_URL = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR_URL = "
