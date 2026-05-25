import streamlit as st
import json
import os
from style import apply_custom_theme

apply_custom_theme()

# --- Persistent Storage ---
DATA_FILE = "chat_history.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return [{"id": 0, "name": "Main Chat", "pinned": False, "messages": []}]

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

if "chats" not in st.session_state:
    st.session_state.chats = load_data()
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = 0

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
            if st.button("Open", key=f"open_{chat['id']}"):
                st.session_state.active_chat_id = chat['id']
                st.rerun()
            if st.button("🗑️", key=f"del_{chat['id']}"):
                st.session_state.chats.remove(chat)
                save_data(st.session_state.chats)
                st.rerun()

# --- Main Chat ---
active_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.active_chat_id), st.session_state.chats[0])

for msg in active_chat["messages"]:
    st.chat_message("user").markdown(msg)

if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append(prompt)
    save_data(st.session_state.chats) # Save every time
    st.rerun()
