import streamlit as st
import json
import os
from streamlit_mic_recorder import mic_recorder
from style import apply_custom_theme

apply_custom_theme()

# --- Storage ---
DATA_FILE = "chat_history.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return [{"id": 0, "name": "Main Chat", "pinned": False, "messages": []}]

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

if "chats" not in st.session_state: st.session_state.chats = load_data()
if "active_chat_id" not in st.session_state: st.session_state.active_chat_id = 0

st.title("Fluency Coach")

# --- Sidebar ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        new_id = len(st.session_state.chats)
        st.session_state.chats.append({"id": new_id, "name": f"Chat {new_id}", "pinned": False, "messages": []})
        save_data(st.session_state.chats)
        st.rerun()

    for chat in st.session_state.chats:
        with st.expander(f"{'📌' if chat['pinned'] else ''} {chat['name']}"):
            chat['name'] = st.text_input("Rename:", value=chat['name'], key=f"rn_{chat['id']}")
            c1, c2, c3 = st.columns(3)
            if c1.button("Open", key=f"op_{chat['id']}"): st.session_state.active_chat_id = chat['id']; st.rerun()
            if c2.button("📌", key=f"pi_{chat['id']}"): chat['pinned'] = not chat['pinned']; save_data(st.session_state.chats); st.rerun()
            if c3.button("🗑️", key=f"de_{chat['id']}"): st.session_state.chats.remove(chat); save_data(st.session_state.chats); st.rerun()

# --- Main Interaction ---
active_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.active_chat_id), st.session_state.chats[0])

for msg in active_chat["messages"]:
    st.chat_message("user").markdown(msg)

# Voice Recorder
st.write("### 🎙️ Speech Input")
audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop ⏹️", key="recorder")

if audio:
    # Logic: Convert audio to text here (place holder)
    text = "Audio detected! (Integrate Whisper API here)"
    active_chat["messages"].append(text)
    save_data(st.session_state.chats)
    st.rerun()

# Text Input
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append(prompt)
    save_data(st.session_state.chats)
    st.rerun()
