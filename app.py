import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import hashlib

# Connection: Import the style file rules
from style import apply_custom_theme

# Page Config
st.set_page_config(
    page_title="Fluency Coach - AI Speaking Companion",
    page_icon="🤖",
    layout="centered"
)

# Connection: Apply style overrides 
apply_custom_theme()

# App Headers
st.title("Fluency Coach")
st.write("### Interactive AI Speaking Companion")

# Sidebar panel
with st.sidebar:
    st.header("Coach Workspace")
    st.info("This secure dashboard uses artificial intelligence to evaluate speech syntax, pronunciation, and flow in real time.")
    st.caption("Tip: Click 'Speak', say a sentence, and click 'Submit'.")

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below or type a message to start!"}
    ]

# Initialize audio tracker state
if "autoplay_audio_data" not in st.session_state:
    st.session_state.autoplay_audio_data = None

if "last_processed_audio" not in st.session_state:
    st.session_state.last_processed_audio = None

GROQ_API_KEY = "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"

# Render conversation timeline with Robot and User Avatar Blocks
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f'''
            <div class="chat-container-user">
                <div class="avatar-icon avatar-icon-user">🧒</div>
                <div class="chat-bubble-user"><b>You</b>{message["content"]}</div>
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown(f'''
            <div class="chat-container-coach">
                <div class="avatar-icon avatar-icon-coach">🤖</div>
                <div class="chat-bubble-coach"><b>AI Coach</b>{message["content"]}</div>
            </div>
        ''', unsafe_allow_html=True)
st.markdown('<div class="clear-fix"></div>', unsafe_allow_html=True)

# Playback engine handler
if st.session_state.autoplay_audio_data:
    st.audio(st.session_state.autoplay_audio_data, format="audio/mp3", autoplay=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# Helper function: LLM Context Engine
def get_coach_response(text_payload):
    llm_payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are a professional, encouraging, and highly advanced English language coach for kids. Keep responses structurally simple, contextually engaging, and limited to 2-3 concise sentences. Gently correct glaring language structure errors if visible, but prioritize continuous conversational flow. Always prompt the user with a targeted follow-up question to keep them talking."
            },
            {"role": "user", "content": text_payload}
        ]
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

# Helper function: Text to Audio bytes
def text_to_speech_bytes(text_payload):
    try:
        url = f"https://translate.google.com/translate_tts?ie=UTF-8&tl=en&client=tw-ob&q={requests.utils.quote(text_payload)}"
        response = requests.get(url)
        if response.status_code == 200:
            return response.content
    except Exception:
        pass
    return None

# Unified Action Panel
input_col, voice_col, stop_col = st.columns([5, 2, 2])

with input_col:
    with st.form(key="text_form", clear_on_submit=True):
        text_input = st.text_input("Type your message here:", placeholder="Type a message...")
        submit_text = st.form_submit_button(label="Send Text 📩", use_container_width=True)
        
        if submit_text and text_input.strip():
            st.session_state.chat_history.append({"role": "user", "content": text_input})
            with st.spinner("Thinking..."):
                coach_reply = get_coach_response(text_input)
                st.session_state.chat_history.append({"role": "coach", "content": coach_reply})
                st.session_state.autoplay_audio_data = None 
                st.rerun()

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

# Voice processing validation check
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
                        
                        audio_data = text_to_speech_bytes(coach_reply)
                        if audio_data:
                            st.session_state.autoplay_audio_data = audio_data
                        st.rerun()
                except Exception as e:
                    st.error("Audio Processing Error. Please try speaking again.")
