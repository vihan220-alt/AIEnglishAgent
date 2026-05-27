import streamlit as st
import json
import os
import time
from groq import Groq

DATA_FILE = "chat_history.json"

# --- Persistent Data Load/Save ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return [{"id": "chat_0", "name": "Chat 1", "messages": [], "pinned": False}]

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

if "chats" not in st.session_state: st.session_state.chats = load_data()
if "active_idx" not in st.session_state: st.session_state.active_idx = 0

# --- Sidebar with Advanced Controls ---
with st.sidebar:
    st.header("Coach Workspace")
    if st.button("➕ New Chat"):
        new_chat = {"id": f"chat_{time.time()}", "name": f"Chat {len(st.session_state.chats)+1}", "messages": [], "pinned": False}
        st.session_state.chats.append(new_chat)
        save_data(st.session_state.chats)
        st.rerun()

    for idx, chat in enumerate(st.session_state.chats):
# Change this line in your app.py:
with st.expander(f"{'📌' if chat.get('pinned', False) else ''} {chat.get('name', 'Chat')}"):
        new_name = st.text_input("Rename", value=chat['name'], key=f"name_{idx}")
            if new_name != chat['name']:
                chat['name'] = new_name
                save_data(st.session_state.chats)
            
            c1, c2, c3 = st.columns(3)
            if c1.button("Open", key=f"open_{idx}"):
                st.session_state.active_idx = idx
                st.rerun()
            if c2.button("📌", key=f"pin_{idx}"):
                chat['pinned'] = not chat.get('pinned', False)
                save_data(st.session_state.chats)
                st.rerun()
            if c3.button("🗑️", key=f"del_{idx}"):
                if len(st.session_state.chats) > 1:
                    st.session_state.chats.pop(idx)
                    st.session_state.active_idx = 0
                    save_data(st.session_state.chats)
                    st.rerun()

# --- Main Logic ---
active_chat = st.session_state.chats[st.session_state.active_idx]
st.title(f"Fluency Coach: {active_chat['name']}")

for msg in active_chat["messages"]:
    with st.chat_message(msg["role"], avatar="🤖" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    active_chat["messages"].append({"role": "assistant", "content": "I received your message."})
    save_data(st.session_state.chats)
    st.rerun()
