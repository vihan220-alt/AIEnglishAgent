import streamlit as st
import json
import os
from groq import Groq
from gTTS import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# 1. Page Configuration
st.set_page_config(page_title="AI Robot Assistant", layout="wide")

# 2. Persistence (Chat History)
DATA_FILE = "chats.json"
if "chats" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: st.session_state.chats = json.load(f)
    else: st.session_state.chats = {"Chat 1": []}

if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"

# 3. Sidebar (Chat Management)
with st.sidebar:
    st.title("Robot Workspace")
    if st.button("➕ New Chat"):
        new_id = f"Chat {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_id] = []
        st.session_state.active_chat = new_id
        with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
        st.rerun()
    
    st.subheader("Manage Chats")
    for chat_id in list(st.session_state.chats.keys()):
        cols = st.columns([0.7, 0.3])
        if cols[0].button(chat_id):
            st.session_state.active_chat = chat_id
            st.rerun()
        if cols[1].button("📌", key=f"pin_{chat_id}"):
            st.toast(f"{chat_id} pinned!")

# 4. Main Chat Interface
st.title(f"Robot Assistant: {st.session_state.active_chat}")

# Audio Controls
col1, col2 = st.columns([0.2, 0.8])
if col1.button("▶️ Speak"): st.session_state.speak = True
if col1.button("⏹️ Stop"): st.session_state.speak = False

for msg in st.session_state.chats[st.session_state.active_chat]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input Handling
if prompt := st.chat_input("Ask me anything..."):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    st.session_state.chats[st.session_state.active_chat].append({"role": "user", "content": prompt})
    
    # Generate AI Response
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a helpful, gaming-style AI robot."}] + 
                 st.session_state.chats[st.session_state.active_chat][-5:]
    ).choices[0].message.content
    
    st.session_state.chats[st.session_state.active_chat].append({"role": "assistant", "content": response})
    with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
    
    # Text-to-Speech (Auto-trigger if "Speak" is active)
    if st.session_state.get("speak", False):
        tts = gTTS(text=response, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
    st.rerun()
