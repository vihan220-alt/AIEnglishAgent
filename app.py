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

if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    client = None

# --- State Management ---
if "chats" not in st.session_state: st.session_state.chats = load_data() # (Keep your existing load_data)
if "stop_audio" not in st.session_state: st.session_state.stop_audio = False

st.title("Fluency Coach")

# --- Stop Audio Button (Always available when coach is speaking) ---
if st.button("🛑 Stop Speaking"):
    st.session_state.stop_audio = True
    st.rerun()

# --- Audio Logic with Interruption ---
def generate_audio_html(text):
    if st.session_state.stop_audio:
        st.session_state.stop_audio = False
        return None # Halt generation
    
    tts = gTTS(text=text, lang='en', tld='co.uk')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    b64 = base64.b64encode(mp3_fp.read()).decode()
    return f'<audio src="data:audio/mp3;base64,{b64}" autoplay controls></audio>'

# --- Main Interaction ---
audio_file = st.audio_input("Speak to your Coach 🎤")

if audio_file is not None and not st.session_state.stop_audio:
    # (Your existing Groq processing block here)
    # When generating the response:
    audio_html = generate_audio_html(reply_text)
    if audio_html:
        # Display the audio player
        st.markdown(audio_html, unsafe_allow_html=True)
