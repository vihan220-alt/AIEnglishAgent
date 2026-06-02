import streamlit as st
import json
import os
from groq import Groq
from gTTS import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# --- 1. Page Configuration ---
st.set_page_config(page_title="Versatile AI", layout="wide")

# --- 2. Data Persistence ---
DATA_FILE = "chats.json"
if "chats" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: 
            st.session_state.chats = json.load(f)
    else: 
        st.session_state.chats = {"Chat 1": []}

if "active_chat" not in st.session_state: 
    st.session_state.active_chat = "Chat 1"

# --- 3. Sidebar ---
with st.sidebar:
    st.title("Workspace")
    if st.button("➕ New Chat"):
        new_id = f"Chat {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_id] = []
        st.session_state.active_chat = new_id
        with open(DATA_FILE, "w") as f: 
            json.dump(st.session_state.chats, f)
        st.rerun()
    
    for chat_id in st.session_state.chats.keys():
        if st.button(chat_id):
            st.session_state.active_chat = chat_id
            st.rerun()

# --- 4. Main Chat Interface ---
st.title(f"Assistant: {st.session_state.active_chat}")

for msg in st.session_state.chats[st.session_state.active_chat]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask me anything..."):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    st.session_state.chats[st.session_state.active_chat].append({"role": "user", "content": prompt})
    
    system_msg = {"role": "system", "content": "You are a helpful and versatile AI assistant."}
    messages_to_send = [system_msg] + st.session_state.chats[st.session_state.active_chat][-5:]
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages_to_send
    ).choices[0].message.content
    
    st.session_state.chats[st.session_state.active_chat].append({"role": "assistant", "content": response})
    with open(DATA_FILE, "w") as f: 
        json.dump(st.session_state.chats, f)
    
    tts = gTTS(text=response, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
    st.rerun()
