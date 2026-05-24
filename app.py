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

# Initialize tracking states safely before the sidebar renders
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# CRITICAL FIX: Ensure active chat id is verified before rendering sidebar UI
saved_chats_list = get_all_chats()
if not saved_chats_list:
    from datetime import datetime
    default_id = f"Chat {datetime.now().strftime('%Y-%m-%d %H-%M-%S')}"
    saved_chats_list = [default_id]
else:
    default_id = saved_chats_list[0]

if "current_chat_id" not in st.session_state or st.session_state.current_chat_id not in saved_chats_list:
    st.session_state.current_chat_id = default_id

if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history(st.session_state.current_chat_id)

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
    
    # Calculate the proper dropdown indexing position safely
    try:
        dropdown_index = saved_chats_list.index(st.session_state.current_chat_id)
    except ValueError:
        dropdown_index = 0

    # 2. ChatGPT Selection Dropdown
    selected_chat = st.selectbox(
        "Select a conversation:",
        options=saved_chats_list,
        index=dropdown_index
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

GROQ_API_KEY = "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"

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

# Action Control Deck Layout
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

# 1. TEXT ENTRY PROCESSING
text_input = st.chat_input("Type your message here...")
if text_input:
    st.session_state.chat_history.append({"role": "user", "content": text_input})
    save_chat_history(st.session_state.current_chat_id, st.session_state.chat_history)
    with st.spinner("Thinking..."):
        coach_reply = get_coach_response(text_input)
        st.session_state.chat_history.append({"role": "coach", "content": coach_reply})
        save_chat_history(st.session_state.current_chat_id, st.session_state.chat_history)
        
        audio_data = text_to_speech_bytes(coach_reply)
        if audio_data:
            st.session_state.autoplay_audio_data = audio_data
        st.rerun()

# 2. VOICE ENTRY PROCESSING
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
                        save_chat_history(st.session_state.current_chat_id, st.session_state.chat_history)
                        coach_reply = get_coach_response(user_text)
                        st.session_state.chat_history.append({"role": "coach", "content": coach_reply})
                        save_chat_history(st.session_state.current_chat_id, st.session_state.chat_history)
                        
                        audio_data = text_to_speech_bytes(coach_reply)
                        if audio_data:
                            st.session_state.autoplay_audio_data = audio_data
                        st.rerun()
                except Exception as e:
                    st.error("Audio Processing Error. Please try speaking again.")
