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

    sorted_chats = sorted(st.session_state.chats, key=lambda x: x.get("pinned", False), reverse=True)

    for chat in sorted_chats:
        display_label = f"{'📌 ' if chat.get('pinned') else ''}{chat['name']}"
        with st.expander(display_label):
            new_name = st.text_input("Rename Chat", value=chat['name'], key=f"rn_{chat['id']}")
            if new_name != chat['name']:
                chat['name'] = new_name
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
            
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
    role = msg.get("role", "user") if isinstance(msg, dict) else "user"
    content = msg.get("content", msg) if isinstance(msg, dict) else msg
    with st.chat_message(role):
        st.markdown(content)

# Audio Microphone Input Setup
audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop ⏹️", key="rec")

# Fix 1: Handle Voice Input safely without infinite repetition loops
if audio and "last_audio" not in st.session_state:
    st.session_state.last_audio = audio
    # Note: To turn voice to text here, an audio transcription API is needed.
    # For now, we log the audio entry cleanly to keep your app from freezing.
    user_voice_placeholder = "🎤 [Recorded Audio Message]"
    active_chat["messages"].append({"role": "user", "content": user_voice_placeholder})
    
    reply = "I received your audio recording! Once we connect our Speech-to-Text API engine, I will transcribe and critique your spoken pronunciation right here."
    active_chat["messages"].append({"role": "assistant", "content": reply})
    
    with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
    st.rerun()

# Clear out the audio trigger flag if the mic state is empty/reset
if not audio and "last_audio" in st.session_state:
    del st.session_state.last_audio

# Fix 2: Text Input Box processing
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    
    reply = f"Hello! I am your Fluency Coach. I received your text message: '{prompt}'. Let's keep practicing your English conversational skills!"
    active_chat["messages"].append({"role": "assistant", "content": reply})
    
    with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
    st.rerun()
