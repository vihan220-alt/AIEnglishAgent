import streamlit as st
import json
import os
from groq import Groq
from gtts import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# --- Page Config ---
st.set_page_config(page_title="Fluency Coach", layout="wide")

# --- Simplified CSS ---
# Keeping background, but removing overly aggressive overrides that might hide buttons
st.markdown("""
    <style>
    .stApp { background-color: #0e1117 !important; }
    div[data-testid="stChatMessage"] { background-color: #161b22 !important; border: 2px solid #444c56 !important; border-radius: 8px !important; }
    </style>
""", unsafe_allow_html=True)

# --- Logic ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])
DATA_FILE = "chats.json"

if "chats" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: st.session_state.chats = json.load(f)
    else: st.session_state.chats = {"Chat 1": []}

if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"

# --- Sidebar (Button Area) ---
with st.sidebar:
    st.title("Workspace")
    if st.button("➕ New Chat"):
        new_id = f"Chat {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_id] = []
        st.session_state.active_chat = new_id
        with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
        st.rerun()
    
    st.markdown("---")
    for chat_id in st.session_state.chats.keys():
        if st.button(chat_id, key=chat_id):
            st.session_state.active_chat = chat_id
            st.rerun()

# --- Main Interface ---
st.title(f"Fluency Coach: {st.session_state.active_chat}")

# Display history
for msg in st.session_state.chats[st.session_state.active_chat]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
if prompt := st.chat_input("Practice your English..."):
    # Append user message
    st.session_state.chats[st.session_state.active_chat].append({"role": "user", "content": prompt})
    
    # Get AI response
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a concise English coach."}] + 
                 st.session_state.chats[st.session_state.active_chat][-5:]
    ).choices[0].message.content
    
    st.session_state.chats[st.session_state.active_chat].append({"role": "assistant", "content": response})
    with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
    
    # TTS
    tts = gTTS(text=response, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
    st.rerun()
