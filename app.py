import streamlit as st
import json
import os
from groq import Groq
from gtts import gTTS
import io
from style import apply_custom_css  # Importing your style file

# Apply the custom styles
apply_custom_css()

# Setup
st.set_page_config(page_title="Fluency Coach", layout="wide")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Data persistence
DATA_FILE = "chat_history.json"
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except: pass
    return {"Chat 1": []}

if "chats" not in st.session_state: st.session_state.chats = load_data()
if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"

# Sidebar
st.sidebar.title("Workspace")
if st.sidebar.button("➕ New Chat"):
    new_id = f"Chat {len(st.session_state.chats) + 1}"
    st.session_state.chats[new_id] = []
    st.session_state.active_chat = new_id
    save_data(st.session_state.chats)
    st.rerun()

for chat_id in st.session_state.chats.keys():
    if st.sidebar.button(chat_id):
        st.session_state.active_chat = chat_id
        st.rerun()

# UI: Chat
st.title(f"Fluency Coach: {st.session_state.active_chat}")
for msg in st.session_state.chats[st.session_state.active_chat]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Say something..."):
    st.session_state.chats[st.session_state.active_chat].append({"role": "user", "content": prompt})
    
    # AI Logic
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a concise English coach. Limit response to 2 sentences."}] + 
                 st.session_state.chats[st.session_state.active_chat][-5:]
    ).choices[0].message.content
    
    st.session_state.chats[st.session_state.active_chat].append({"role": "assistant", "content": response})
    save_data(st.session_state.chats)
    
    # Text-to-Speech
    tts = gTTS(text=response, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
    st.rerun()
