import streamlit as st
import json
import os
from streamlit_mic_recorder import mic_recorder
from style import apply_custom_theme

apply_custom_theme()

# --- Initialize ---
DATA_FILE = "chat_history.json"
if "chats" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            st.session_state.chats = json.load(f)
    else:
        st.session_state.chats = [{"id": 0, "name": "Main Chat", "pinned": False, "messages": []}]

if "active_id" not in st.session_state:
    st.session_state.active_id = 0

st.title("Fluency Coach")

# --- Sidebar (Everything here is indented) ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        new_id = len(st.session_state.chats)
        st.session_state.chats.append({"id": new_id, "name": f"Chat {new_id}", "pinned": False, "messages": []})
        st.rerun()

    for chat in st.session_state.chats:
        with st.expander(f"{'📌' if chat['pinned'] else ''} {chat['name']}"):
            new_name = st.text_input("Rename", value=chat['name'], key=f"rn_{chat['id']}")
            if new_name != chat['name']:
                chat['name'] = new_name
            if st.button("Open", key=f"op_{chat['id']}"): 
                st.session_state.active_id = chat['id']; st.rerun()

# --- Main Interaction (NOT INDENTED - This goes in the main screen) ---
active_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.active_id), st.session_state.chats[0])

# Display existing messages
for msg in active_chat["messages"]:
    st.chat_message("user").markdown(msg)

# Mic and Input Area
audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop ⏹️", key="rec")
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append(prompt)
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.chats, f)
    st.rerun()
