import streamlit as st
import os
from groq import Groq
from audio import get_audio_bytes
from message import save_data, load_data

client = Groq(api_key=st.secrets["GROQ_API_KEY"])
st.set_page_config(page_title="Fluency Coach", layout="wide")

# Initialize State
if "chats" not in st.session_state: st.session_state.chats = load_data()
if "active_chat_id" not in st.session_state: st.session_state.active_chat_id = "Chat 1"
if "active_audio_bytes" not in st.session_state: st.session_state.active_audio_bytes = None

# Sidebar
st.sidebar.title("Workspace")
if st.sidebar.button("➕ New Chat"):
    new_id = f"Chat {len(st.session_state.chats) + 1}"
    st.session_state.chats[new_id] = []
    st.session_state.active_chat_id = new_id
    save_data(st.session_state.chats)
    st.rerun()

for chat_id in list(st.session_state.chats.keys()):
    if st.sidebar.button(f"💬 {chat_id}"):
        st.session_state.active_chat_id = chat_id
        st.rerun()

# Main Interface
st.title(f"Fluency Coach: {st.session_state.active_chat_id}")

# Display Chat
for msg in st.session_state.chats[st.session_state.active_chat_id]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Audio Handling
if st.session_state.active_audio_bytes:
    st.audio(st.session_state.active_audio_bytes, format="audio/mp3", autoplay=True)
    if st.button("🛑 Stop Audio"):
        st.session_state.active_audio_bytes = None
        st.rerun()

# Input
if prompt := st.chat_input("Say something..."):
    st.session_state.chats[st.session_state.active_chat_id].append({"role": "user", "content": prompt})
    
    # AI Response
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": "You are a concise English coach. Max 2 sentences."}] + 
                 st.session_state.chats[st.session_state.active_chat_id][-5:],
        temperature=0.7
    )
    reply = completion.choices[0].message.content
    st.session_state.chats[st.session_state.active_chat_id].append({"role": "assistant", "content": reply})
    
    # Generate Audio
    st.session_state.active_audio_bytes = get_audio_bytes(reply)
    save_data(st.session_state.chats)
    st.rerun()
