import streamlit as st
import json
import os
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io
from style import apply_custom_theme

# Apply styles
apply_custom_theme()

DATA_FILE = "chat_history.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list) and len(data) > 0 and "id" in data[0]:
                    return data
            except:
                pass
    # Base configuration if file is empty or corrupted
    return [{"id": 0, "name": "Chat 1", "pinned": False, "messages": []}]

# Securely bind state profiles
if "chats" not in st.session_state:
    st.session_state.chats = load_data()

if "active_id" not in st.session_state:
    # Set the first available chat ID as the active target
    st.session_state.active_id = st.session_state.chats[0]["id"]

st.title("Fluency Coach")

# --- Sidebar Workspace ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    
    if st.button("➕ New Chat", key="new_chat_btn"):
        # Generate a unique timestamp-based ID so rooms never conflict
        import time
        new_id = int(time.time() * 1000)
        new_chat_number = len(st.session_state.chats) + 1
        
        # Build new configuration block
        new_chat_node = {"id": new_id, "name": f"Chat {new_chat_number}", "pinned": False, "messages": []}
        st.session_state.chats.append(new_chat_node)
        
        # Instantly shift active viewport to our newly generated room
        st.session_state.active_id = new_id
        
        with open(DATA_FILE, "w") as f: 
            json.dump(st.session_state.chats, f)
        st.rerun()

    # Dynamic arrangement system (Pinned items float to top)
    sorted_chats = sorted(st.session_state.chats, key=lambda x: x.get("pinned", False), reverse=True)

    for chat in sorted_chats:
        is_active_marker = "🟢 " if chat["id"] == st.session_state.active_id else ""
        pin_marker = "📌 " if chat.get("pinned") else ""
        display_label = f"{is_active_marker}{pin_marker}{chat['name']}"
        
        with st.expander(display_label, expanded=(chat["id"] == st.session_state.active_id)):
            # Rename Input Element
            new_name = st.text_input("Rename Chat", value=chat['name'], key=f"rn_{chat['id']}")
            if new_name != chat['name']:
                chat['name'] = new_name
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()
            
            # Workspace Dashboard Controls
            c1, c2, c3 = st.columns(3)
            
            if c1.button("Open", key=f"op_{chat['id']}"): 
                st.session_state.active_id = chat['id']
                st.rerun()
                
            if c2.button("📌", key=f"pi_{chat['id']}", help="Pin Workspace"): 
                chat['pinned'] = not chat.get('pinned', False)
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()
                
            if c3.button("🗑️", key=f"de_{chat['id']}", help="Delete Workspace"): 
                if len(st.session_state.chats) > 1:
                    # Find backup workspace context before deletion
                    remaining_chats = [c for c in st.session_state.chats if c["id"] != chat["id"]]
                    st.session_state.chats.remove(chat)
                    if st.session_state.active_id == chat['id']:
                        st.session_state.active_id = remaining_chats[0]['id']
                else:
                    # Hard defaults if last room is cleared
                    st.session_state.chats = [{"id": 0, "name": "Chat 1", "pinned": False, "messages": []}]
                    st.session_state.active_id = 0
                    
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()

# --- Main Chat Window Rendering Engine ---
# Safety verification check for matching active ID targets
active_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.active_id), None)
if not active_chat:
    active_chat = st.session_state.chats[0]
    st.session_state.active_id = active_chat["id"]

# Render active chat history layout bubbles
for msg in active_chat["messages"]:
    role = msg.get("role", "user") if isinstance(msg, dict) else "user"
    content = msg.get("content", msg) if isinstance(msg, dict) else msg
    with st.chat_message(role):
        st.markdown(content)

# Audio Microphone Capture Logic
audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop ⏹️", key="rec")

if audio and "last_audio" not in st.session_state:
    st.session_state.last_audio = audio
    audio_bytes = audio['bytes']
    r = sr.Recognizer()
    transcribed_text = ""
    
    try:
        with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
            audio_data = r.record(source)
            transcribed_text = r.recognize_google(audio_data)
    except sr.UnknownValueError:
        transcribed_text = "⚠️ [Could not understand audio. Speak clearly!]"
    except Exception as e:
        transcribed_text = "⚠️ [Audio processing engine error]"

    if transcribed_text:
        active_chat["messages"].append({"role": "user", "content": f"🎤 Spoken: {transcribed_text}"})
        reply = f"I heard you say: '{transcribed_text}'. Your core speech structure is developing nicely. Let's practice another sentence!"
        active_chat["messages"].append({"role": "assistant", "content": reply})
        
        with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
        st.rerun()

if not audio and "last_audio" in st.session_state:
    del st.session_state.last_audio

# Chat Box Processing Logic
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    reply = f"Hello! I am your Fluency Coach. I received your text message: '{prompt}'. Let's keep practicing your English conversational skills!"
    active_chat["messages"].append({"role": "assistant", "content": reply})
    
    with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
    st.rerun()
