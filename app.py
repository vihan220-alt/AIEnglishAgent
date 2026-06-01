import streamlit as st
import json
import os
from groq import Groq
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
from style import apply_custom_css

apply_custom_css()
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# State setup
if "chats" not in st.session_state: st.session_state.chats = {"Chat 1": []}
if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"

# Sidebar
st.sidebar.title("Workspace")
if st.sidebar.button("➕ New Chat"):
    new_id = f"Chat {len(st.session_state.chats) + 1}"
    st.session_state.chats[new_id] = []
    st.rerun()

for chat_name in list(st.session_state.chats.keys()):
    col1, col2 = st.sidebar.columns([0.8, 0.2])
    if col1.button(chat_name): st.session_state.active_chat = chat_name
    if col2.button("🗑️", key=chat_name): 
        del st.session_state.chats[chat_name]
        st.rerun()

# Main Interface
st.title("Fluency Coach")

# Speech Input Logic
audio = mic_recorder(start_prompt="🎤 Speak", stop_prompt="🛑 Stop", just_once=True)
if audio:
    # Note: Requires a transcription service like OpenAI Whisper to convert audio to text
    st.write("Processing your voice...")

# Text Input
if prompt := st.chat_input("Type your message..."):
    st.session_state.chats[st.session_state.active_chat].append({"role": "user", "content": prompt})
    
    # AI Logic
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    ).choices[0].message.content
    
    st.session_state.chats[st.session_state.active_chat].append({"role": "assistant", "content": response})
    
    # Speak Response
    tts = gTTS(text=response, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
    st.rerun()

# Display Messages
for msg in st.session_state.chats[st.session_state.active_chat]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
