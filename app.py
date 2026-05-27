import streamlit as st
import json
import os
import time
from groq import Groq

# --- File Sync Setup ---
DATA_FILE = "chat_history.json"
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

st.set_page_config(layout="wide")

# --- Persistent Data Load/Save ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return [{"id": "chat_default", "name": "Chat 1", "messages": [], "pinned": False}]

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

if "chats" not in st.session_state: 
    st.session_state.chats = load_data()
if "active_idx" not in st.session_state: 
    st.session_state.active_idx = 0

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("Coach Workspace")
    if st.button("➕ New Chat"):
        new_chat = {"id": f"chat_{time.time()}", "name": f"Chat {len(st.session_state.chats)+1}", "messages": [], "pinned": False}
        st.session_state.chats.append(new_chat)
        save_data(st.session_state.chats)
        st.session_state.active_idx = len(st.session_state.chats) - 1
        st.rerun()

    st.divider()
    
    # Loop to render your options dropdown (st.expander)
    for idx, chat in enumerate(st.session_state.chats):
        with st.expander(f"{'📌' if chat.get('pinned', False) else ''} {chat.get('name', 'Chat')}"):
            new_name = st.text_input("Rename", value=chat.get('name', 'Chat'), key=f"name_{idx}")
            if new_name != chat.get('name'):
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

# --- Main Chat Screen ---
active_chat = st.session_state.chats[st.session_state.active_idx]
st.title(f"Fluency Coach: {active_chat.get('name', 'Chat')}")

# Always show past messages if they exist
for msg in active_chat["messages"]:
    avatar_icon = "🤖" if msg["role"] == "assistant" else "👤"
    with st.chat_message(msg["role"], avatar=avatar_icon):
        st.markdown(msg["content"])

# Main Input Controls (Always visible at the bottom)
if prompt := st.chat_input("Type your message here..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    
    # Simple direct reply text to keep it responsive
    bot_reply = f"Awesome! I've received your text: '{prompt}'. Let's chat!"
    active_chat["messages"].append({"role": "assistant", "content": bot_reply})
    
    save_data(st.session_state.chats)
    st.rerun()
