import streamlit as st
import json
import os
from streamlit_mic_recorder import mic_recorder
from style import apply_custom_theme

# 1. ALWAYS apply styles first
apply_custom_theme()

# 2. DEFINE your data functions before using them
DATA_FILE = "chat_history.json"
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try: return json.load(f)
            except: pass
    return [{"id": 0, "name": "Main Chat", "pinned": False, "messages": []}]

# 3. INITIALIZE session state (This must happen before you try to use it)
if "chats" not in st.session_state:
    st.session_state.chats = load_data()
if "active_id" not in st.session_state:
    st.session_state.active_id = 0

st.title("Fluency Coach")

# 4. NOW it is safe to use st.session_state
active_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.active_id), st.session_state.chats[0])

# --- Sidebar ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    # ... rest of your sidebar code ...
