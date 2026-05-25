import streamlit as st
import json
import os
import io
import time
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
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
                    # Make sure old entries have valid string keys
                    for index, chat in enumerate(data):
                        if "id" not in chat or chat["id"] == 0:
                            chat["id"] = f"chat_{int(time.time())}_{index}"
                    return data
            except:
                pass
    return [{"id": f"chat_{int(time.time())}_main", "name": "Chat 1", "pinned": False, "messages": []}]

if "chats" not in st.session_state:
    st.session_state.chats = load_data()

if "active_id" not in st.session_state or not st.session_state.active_id:
    st.session_state.active_id = st.session_state.chats[0]["id"]

st.title("Fluency Coach")

# --- Sidebar Workspace ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    
    if st.button("➕ New Chat", key="new_chat_btn"):
        # Create a unique timestamp string ID so keys never collide
        unique_id = f"chat_{int(time.time() * 1000)}"
        new_chat_number = len(st.session_state.chats) + 1
        
        new_chat_node = {"id": unique_id, "name": f"Chat {new_chat_number}", "pinned": False, "messages": []}
        st.session_state.chats.append(new_chat_node)
        st.session_state.active_id = unique_id
        
        with open(DATA_FILE, "w") as f: 
            json.dump(st.session_state.chats, f)
        st.rerun()

    # Sort chats cleanly
    sorted_chats = sorted(st.session_state.chats, key=lambda x: x.get("pinned", False), reverse=True)

    for chat in sorted_chats:
        chat_id = str(chat["id"])
        is_active_marker = "🟢 " if chat_id == str(st.session_state.active_id) else ""
        pin_marker = "📌 " if chat.get("pinned") else ""
        display_label = f"{is_active_marker}{pin_marker}{chat['name']}"
        
        with st.expander(display_label, expanded=(chat_id == str(st.session_state.active_id))):
            # Unique Text Input Key assignment
            new_name = st.text_input("Rename Chat", value=chat['name'], key=f"input_rn_{chat_id}")
            if new_name != chat['name']:
                chat['name'] = new_name
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()
            
            c1, c2, c3 = st.columns(3)
            
            if c1.button("Open", key=f"btn_op_{chat_id}"): 
                st.session_state.active_id = chat_id
                st.rerun()
                
            if c2.button("📌", key=f"btn_pi_{chat_id}"): 
                chat['pinned'] = not chat.get('pinned', False)
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()
                
            if c3.button("🗑️", key=f"btn_de_{chat_id}"): 
                if len(st.session_state.chats) > 1:
                    st.session_state.chats = [c for c in st.session_state.chats if str(c["id"]) != chat_id]
                    if str(st.session_state.active_id) == chat_id:
                        st.session_state.active_id = st.session_state.chats[0]['id']
                else:
                    st.session_state.chats = [{"id": f"chat_{int(time.time())}_main", "name": "Chat 1", "pinned": False, "messages": []}]
                    st.session_state.active_id = st.session_state.chats[0]['id']
                    
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()

# --- Active Chat Window Context Logic ---
active_chat = next((c for c in st.session_state.chats if str(c["id"]) == str(st.session_state.active_id)), None)
if not active_chat:
    active_chat = st.session_state.chats[0]
    st.session_state.active_id = active_chat["id"]

# Display text history logs
for msg in active_chat["messages"]:
    role = msg.get("role", "user") if isinstance(msg, dict) else "user"
    content = msg.get("content", msg) if isinstance(msg, dict) else msg
    with st.chat_message(role):
        st.markdown(content)

# Audio Microphone Component Interface
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
        transcribed_text = "⚠️ [Could not interpret audio track clearly]"
    except Exception as e:
        transcribed_text = "⚠️ [Audio engine processing fallback]"

    if transcribed_text:
        active_chat["messages"].append({"role": "user", "content": f"🎤 Spoken: {transcribed_text}"})
        reply = f"I heard you say: '{transcribed_text}'. Let's continue working on your conversational flow!"
        active_chat["messages"].append({"role": "assistant", "content": reply})
        
        with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
        st.rerun()

if not audio and "last_audio" in st.session_state:
    del st.session_state.last_audio

# Main Interactive Text Processing
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    reply = f"Hello! I am your Fluency Coach. I received your text: '{prompt}'. Let's keep practicing!"
    active_chat["messages"].append({"role": "assistant", "content": reply})
    
    with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
    st.rerun()
