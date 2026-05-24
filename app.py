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

# Initialize tracking states
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# Verified high-quality web illustration image URLs
ROBOT_AVATAR_URL = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR_URL = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"

# =========================================================
# SIDEBAR CONTROL PANEL (The ChatGPT Experience)
# =========================================================
with st.sidebar:
    st.header("Coach Workspace")
    
    # 1. Start a New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        from datetime import datetime
        new_chat_id = f"Chat {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
        st.session_state.current_chat_id = new_chat_id
        st.session_state.chat_history = [
            {"role": "coach", "content": "Hello! Let's start a brand new conversation. Tap the microphone below or type a message to start!"}
        ]
        save_chat_history(new_chat_id, st.session_state.chat_history)
        st.session_state.autoplay_audio_data = None
        st.rerun()

    st.markdown("---")
    st.subheader("Your Conversations")
    
    # Get list of all past chats
    saved_chats_list = get_all_chats()
    
    # Fallback if there are no chats at all yet
    if not saved_chats_list:
        from datetime import datetime
        default_id = f"Chat {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
        saved_chats_list = [default_id]
        
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = saved_chats_list[0]

    # 2. ChatGPT Selection Dropdown
    selected_chat = st.selectbox(
        "Select a conversation:",
        options=saved_chats_list,
        index=saved_chats_list.index(st.session_state.current_chat_id) if st.session_state.current_chat_id in saved_chats_list else 0
    )
    
    # Switch history if user selects a different chat room
    if selected_chat != st.session_state.current_chat_id:
        st.session_state.current_chat_id = selected_chat
        st.session_state.chat_history = load_chat_history(selected_chat)
        st.session_state.autoplay_audio_data = None
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 3. Delete Current Chat Button
    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        filepath = os.path.join(CHATS_DIR, f"{st.session_state.current_chat_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
        if "current_chat_id" in st.session_state:
            del st.session_state.current_chat_id
        if "chat_history" in st.session_state:
            del st.session_state.chat_history
        st.session_state.autoplay_audio_data = None
        st.rerun()

# Ensure variables exist before running
