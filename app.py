import streamlit as st
import json
import os
import io
import time
import base64
from groq import Groq
from gtts import gTTS
from style import apply_custom_theme

apply_custom_theme()
DATA_FILE = "chat_history.json"

# Initialize Groq
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

# --- Session State for Audio Control ---
if "stop_audio" not in st.session_state: st.session_state.stop_audio = False

st.title("Fluency Coach")

# --- Permanent Stop Button ---
if st.button("🛑 Stop Audio"):
    st.session_state.stop_audio = True
    st.rerun()

def generate_audio_html(text):
    if st.session_state.stop_audio:
        return ""
    tts = gTTS(text=text, lang='en', tld='co.uk')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    b64 = base64.b64encode(mp3_fp.read()).decode()
    return f'<audio src="data:audio/mp3;base64,{b64}" autoplay controls></audio>'

# --- Load Data (Keep your existing function) ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except: pass
    return [{"id": "main_default", "name": "Chat 1", "messages": []}]

if "chats" not in st.session_state: st.session_state.chats = load_data()
active_chat = st.session_state.chats[0] # Simplified for brevity

# --- Voice Input Logic ---
audio_file = st.audio_input("Speak to your Coach 🎤")

if audio_file:
    # 1. Transcribe
    buffer = io.BytesIO(audio_file.read())
    buffer.name = "audio.wav"
    translation = client.audio.transcriptions.create(file=buffer, model="whisper-large-v3", response_format="text")
    transcribed_text = translation.strip()
    
    # 2. Generate Reply Text
    reply_text = f"I heard you say: '{transcribed_text}'. Let's keep practicing!"
    
    # 3. Add to chat
    active_chat["messages"].append({"role": "user", "content": transcribed_text})
    active_chat["messages"].append({"role": "assistant", "content": reply_text})
    
    # 4. Generate Audio ONLY if not stopped
    st.session_state.stop_audio = False
    audio_html = generate_audio_html(reply_text)
    
    with st.chat_message("assistant"):
        st.write(reply_text)
        if audio_html:
            st.markdown(audio_html, unsafe_allow_html=True)
    
    st.rerun()

# --- Text Input Logic ---
if prompt := st.chat_input("Type your message..."):
    reply_text = f"Received your text: '{prompt}'."
    active_chat["messages"].append({"role": "user", "content": prompt})
    active_chat["messages"].append({"role": "assistant", "content": reply_text})
    st.rerun()
