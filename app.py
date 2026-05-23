import streamlit as st
from streamlit_mic_recorder import mic_recorder, speech_to_text
import requests
import json

# Set up professional page configuration
st.set_page_config(
    page_title="Fluency Coach - AI Speaking Companion",
    page_icon="🤖",
    layout="centered"
)

# Premium Dark Theme/SaaS Custom Styling
st.markdown("""
    <style>
    .main { background-color: #090d16; color: #f8fafc; }
    .stHeading h1 { font-size: 28px; font-weight: 700; background: linear-gradient(to right, #ffffff, #06b6d4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stHeading h3 { font-size: 16px; color: #64748b; font-weight: 400; }
    div[data-testid="stExpander"] { background-color: #111927; border: 1px solid rgba(255,255,255,0.06); border-radius: 12px; }
    .chat-bubble-user { background-color: #0369a1; padding: 12px 18px; border-radius: 16px 16px 0px 16px; margin: 10px 0; max-width: 80%; float: right; clear: both; color: white; }
    .chat-bubble-coach { background-color: #1e293b; padding: 12px 18px; border-radius: 16px 16px 16px 0px; margin: 10px 0; max-width: 80%; float: left; clear: both; border: 1px solid rgba(255,255,255,0.06); color: white; }
    .clear-fix { clear: both; }
    </style>
""", unsafe_allow_back_allowed=True, unsafe_allow_html=True)

# App Headers
st.title("Fluency Coach")
st.write("### Interactive AI Speaking Companion")

# Sidebar panel for professional SaaS look
with st.sidebar:
    st.header("Coach Workspace")
    st.info("This secure dashboard uses artificial intelligence to evaluate speech syntax, pronunciation, and flow in real time. Perfect for young learners building language confidence.")
    st.caption("Tip: Click 'Start recording', say a sentence, and click 'Stop'.")

# Initialize persistent chat history in Streamlit session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "coach", "content": "Hello! I am your conversational language partner. Let's practice speaking English together. Tap the microphone below and tell me what you did today!"}
    ]

# Hardcoded Groq Credentials (For your personal project use)
GROQ_API_KEY = "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"

# Render the professional layout timeline
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f'<div class="chat-bubble-user"><b>You:</b> {message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble-coach"><b>Coach:</b> {message["content"]}</div>', unsafe_allow_html=True)
st.markdown('<div class="clear-fix"></div>', unsafe_allow_html=True)

st.markdown("---")

# Voice Input Section
st.write("🎙️ **Tap to Speak:**")
# The native mic recorder returns a dictionary when an audio recording finishes
audio_source = mic_recorder(
    start_prompt="Start Recording 🎤",
    stop_prompt="Stop & Submit 🔇",
    key="recorder",
    format="wav"
)

# Process Voice Input if recorded
if audio_source and "bytes" in audio_source:
    audio_bytes = audio_source["bytes"]
    
    if audio_bytes:
        with st.spinner("Processing your speech..."):
            try:
                # 1. Transcribe the audio bytes into text using Groq's Whisper model
                files = {
                    "file": ("speech.wav", audio_bytes, "audio/wav"),
                    "model": (None, "whisper-large-v3-turbo")
                }
                headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
                
                whisper_response = requests.post(
                    "https://api.groq.com/openai/v1/audio/transcriptions",
                    headers=headers,
                    files=files
                )
                
                user_text = whisper_response.json().get("text", "")
                
                if user_text.strip():
                    # Append user text to chat history
                    st.session_state.chat_history.append({"role": "user", "content": user_text})
                    
                    # 2. Get the English Teacher response from Llama model
                    llm_payload = {
                        "model": "llama-3.3-70b-versatile",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a professional, encouraging, and highly advanced English language coach for kids. Keep responses structurally simple, contextually engaging, and limited to 2-3 concise sentences. Gently correct glaring language structure errors if visible, but prioritize continuous conversational flow. Always prompt the user with a targeted follow-up question to keep them talking."
                            },
                            {"role": "user", "content": user_text}
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
                    
                    coach_reply = llm_response.json()["choices"][0]["message"]["content"]
                    
                    # Append coach response to timeline
                    st.session_state.chat_history.append({"role": "coach", "content": coach_reply})
                    
                    # Force page reload to render the updated chat bubbles seamlessly
                    st.rerun()
                    
            except Exception as e:
                st.error("Audio Processing Error. Please try speaking again.")
