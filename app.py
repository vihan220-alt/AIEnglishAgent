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
    layout="centered"
)

apply_custom_theme()

st.title("Fluency Coach")
st.write("### Interactive AI Speaking Companion")

# =========================================================
# REFRESH-SAFE PERSISTENCE ENGINE (Uses URL Query Parameters)
# =========================================================

# Initialize overall chat vaults inside Streamlit's global state
if "all_chats_vault" not in st.session_state:
    st.session_state.all_chats_vault = {
        "Default Chat": [
            {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}
        ]
    }

# Read browser address bar parameters
query_params = st.query_parameters

# Synchronize current active chat session with browser address bar state
if "chat" in query_params:
    active_chat_title = query_params["chat"]
    # If the room exists in vault, sync it; otherwise fall back safely
    if active_chat_title not in st.session_state.all_chats_vault:
        active_chat_title = list(st.session_state.all_chats_vault.keys())[0]
else:
    active_chat_title = list(st.session_state.all_chats_vault.keys())[0]

st.session_state.current_chat_id = active_chat_title
st.session_state.chat_history = st.session_state.all_chats_vault[active_chat_title]

if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

# Verified illustration avatar image strings structured safely to prevent syntax truncation
ROBOT_AVATAR = "https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
USER_AVATAR = "https://cdn-icons-png.flaticon.com/512/3048/3048122.png"

# =========================================================
# SIDEBAR CONTROL PANEL (The ChatGPT Experience)
# =========================================================
with st.sidebar:
    st.header("Coach Workspace")
    
    # 1. Start a New Chat Button
    if st.button("➕ New Chat", use_container_width=True):
        from datetime import datetime
        new_room_name = f"Chat {datetime.now().strftime('%b%d-%H%M%S')}"
        
        # Inject fresh room into session state vault
        st.session_state.all_chats_vault[new_room_name] = [
            {"role": "coach", "content": "Hello! Let's start a brand new conversation. Tap the microphone below or type a message to start!"}
        ]
        
        # Update browser address query parameters so refresh points here
        st.query_parameters["chat"] = new_room_name
        st.session_state.current_chat_id = new_room_name
        st.session_state.chat_history = st.session_state.all_chats_vault[new_room_name]
        st.session_state.autoplay_audio_data = None
        st.rerun()

    st.markdown("---")
    st.subheader("Your Conversations")
    
    available_rooms = list(st.session_state.all_chats_vault.keys())
    try:
        current_dropdown_index = available_rooms.index(st.session_state.current_chat_id)
    except ValueError:
        current_dropdown_index = 0

    # 2. ChatGPT Selection Dropdown
    selected_room = st.selectbox(
        "Select a conversation:",
        options=available_rooms,
        index=current_dropdown_index
    )
    
    # Switch room context immediately if selection state transitions
    if selected_room != st.session_state.current_chat_id:
        st.query_parameters["chat"] = selected_room
        st.session_state.current_chat_id = selected_room
        st.session_state.chat_history = st.session_state.all_chats_vault[selected_room]
        st.session_state.autoplay_audio_data = None
        st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # 3. Delete Current Chat Button
    if st.button("🗑️ Delete Current Chat", use_container_width=True):
        if len(st.session_state.all_chats_vault) > 1:
            del st.session_state.all_chats_vault[st.session_state.current_chat_id]
            fallback_room = list(st.session_state.all_chats_vault.keys())[0]
            st.query_parameters["chat"] = fallback_room
        else:
            # If it's the last chat, just wipe it clean to factory settings
            st.session_state.all_chats_vault["Default Chat"] = [
                {"role": "coach", "content": "Hello! Let's start fresh. Tap the microphone below or type a message to start!"}
            ]
            st.query_parameters["chat"] = "Default Chat"
            
        st.session_state.autoplay_audio_data = None
        st.rerun()

GROQ_API_KEY = "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"

# Render Conversation Timeline
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user", avatar=USER_AVATAR):
            st.markdown(message["content"])
    else:
        with st.chat_message("assistant", avatar=ROBOT_AVATAR):
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
    with st.spinner("Thinking..."):
        coach_reply = get_coach_response(text_input)
        st.session_state.chat_history.append({"role": "coach", "content": coach_reply})
        
        # Update our master state session vault values immediately
        st.session_state.all_chats_vault[st.session_state.current_chat_id] = st.session_state.chat_history
        
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
                        coach_reply = get_coach_response(user_text)
                        st.session_state.chat_history.append({"role": "coach", "content": coach_reply})
                        
                        # Update our master state session vault values immediately
                        st.session_state.all_chats_vault[st.session_state.current_chat_id] = st.session_state.chat_history
                        
                        audio_data = text_to_speech_bytes(coach_reply)
                        if audio_data:
                            st.session_state.autoplay_audio_data = audio_data
                        st.rerun()
                except Exception as e:
                    st.error("Audio Processing Error. Please try speaking again.")
