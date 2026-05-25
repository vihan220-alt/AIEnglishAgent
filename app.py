import streamlit as st
import json
import os
from streamlit_mic_recorder import mic_recorder
from style import apply_custom_theme

# Apply styles
apply_custom_theme()

DATA_FILE = "chat_history.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
                # Ensure structure is valid
                if isinstance(data, list) and len(data) > 0 and "messages" in data[0]:
                    return data
            except:
                pass
    return [{"id": 0, "name": "Main Chat", "pinned": False, "messages": []}]

if "chats" not in st.session_state:
    st.session_state.chats = load_data()
if "active_id" not in st.session_state:
    st.session_state.active_id = 0

st.title("Fluency Coach")

# --- Sidebar Workspace ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", key="new_chat_btn"):
        new_id = int(st.time() * 1000) if hasattr(st, 'time') else len(st.session_state.chats) + 1
        st.session_state.chats.append({"id": new_id, "name": f"Chat {len(st.session_state.chats)}", "pinned": False, "messages": []})
        with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
        st.rerun()

    # Sort chats so pinned ones stay at the top
    sorted_chats = sorted(st.session_state.chats
