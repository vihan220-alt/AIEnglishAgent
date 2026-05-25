import streamlit as st
import json
import os
import io
import time
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from style import apply_custom_theme

# Apply CSS styles
apply_custom_theme()

DATA_FILE = "chat_history.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0:
                    # Repair structural anomalies and ensure unique IDs
                    for index, chat in enumerate(data):
                        if "id" not in chat or not chat["id"]:
                            chat["id"] = f"id_{int(time.time())}_{index}"
                        if "messages" not in chat:
                            chat["messages"] = []
                    return data
            except:
                pass
    return [{"id": "main_default", "name": "Chat 1", "pinned": False, "messages": []}]

if "chats" not in st.session_state:
    st.session_state.chats = load_data()

if "active_id" not in st.session_state:
    st.session_state.active_id = st.session_state.chats[0]["id"]

st.title("Fluency Coach")

# --- Sidebar Workspace Management ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    
    if st.button("➕ New Chat", key="new_chat_btn"):
        unique_id = f"id_{int(time.time() * 1000)}"
        new_chat_number = len(st.session_state.chats) + 1
        
        new_chat_node = {"id": unique_id, "name": f"Chat {new_chat_number}", "pinned": False, "messages": []}
        st.
