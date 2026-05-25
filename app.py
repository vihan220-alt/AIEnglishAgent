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
                if isinstance(data, list) and len(data) > 0:
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
        new_id = len(st.session_state.chats) + 1
        st.session_state.chats.append({"id": new_id, "name": f"Chat {len(st.session_state.chats)}", "pinned": False, "messages": []})
        with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
        st.rerun()

    # Fixed sorting line syntax error
    sorted_chats = sorted(st.session_state.chats, key=lambda x: x.get("pinned", False), reverse=True)

    for chat in sorted_chats:
        display_label = f"{'📌 ' if chat.get('pinned') else ''}{chat['name']}"
        with st.expander(display_label):
            # Rename Input Box
            new_name = st.text_input("Rename Chat", value=chat['name'], key=f"rn_{chat['id']}")
            if new_name != chat['name']:
                chat['name'] = new_name
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
            
            # Action Buttons Layout
            c1, c2, c3 = st.columns(3)
            if c1.button("Open", key=f"op_{chat['id']}"): 
                st.session_state.active_id = chat['id']
                st.rerun()
            if c2.button("📌", key=f"pi_{chat['id']}"): 
                chat['pinned'] = not chat.get('pinned', False)
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()
            if c3.button("🗑️", key=f"de_{chat['id']}"): 
                if len(st.session_state.chats) > 1:
                    st.session_state.chats.remove(chat)
                    if st.session_state.active_id == chat['id']:
                        st.session_state.active_id = st.session_state.chats[0]['id']
                else:
                    st.session_state.chats = [{"id": 0, "name": "Main Chat", "pinned": False, "messages": []}]
                    st.session_state.active_id = 0
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()

# --- Active Chat Window ---
active_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.active_id), st.session_state.chats[0])

# Render chat bubbles cleanly
for msg in active_chat["messages"]:
    if isinstance(msg, dict):
        role = msg.get("role", "user")
        content = msg.get("content", "")
    else:
        role = "user"
        content = msg
    
    with st.chat_message(role):
        st.markdown(content)

# Audio Microphone Input
audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop ⏹️", key="rec")

# Text Input
if prompt := st.chat_input("Type your message..."):
    # 1. Save user message
    active_chat["messages"].append({"role": "user", "content": prompt})
    
    # 2. Generate immediate Coach answer
    reply = f"Hello! I am your Fluency Coach. I received your message: '{prompt}'. Let's keep practicing your English conversational skills!"
    active_chat["messages"].append({"role": "assistant", "content": reply})
    
    # 3. Save to file and refresh screen
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.chats, f)
    st.rerun()
