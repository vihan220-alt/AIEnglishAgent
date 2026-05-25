import streamlit as st
import json
import os
import io
import time
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
from pydub import AudioSegment
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
        st.session_state.chats.append(new_chat_node)
        st.session_state.active_id = unique_id
        
        with open(DATA_FILE, "w") as f: 
            json.dump(st.session_state.chats, f)
        st.rerun()

    # Sort Pinned items to the top
    sorted_chats = sorted(st.session_state.chats, key=lambda x: x.get("pinned", False), reverse=True)

    # Use index enumeration to guarantee unique element keys
    for idx, chat in enumerate(sorted_chats):
        chat_id = chat["id"]
        is_active = (str(chat_id) == str(st.session_state.active_id))
        
        is_active_marker = "🟢 " if is_active else ""
        pin_marker = "📌 " if chat.get("pinned") else ""
        display_label = f"{is_active_marker}{pin_marker}{chat['name']}"
        
        with st.expander(display_label, expanded=is_active):
            new_name = st.text_input("Rename Chat", value=chat['name'], key=f"text_input_key_{idx}_{chat_id}")
            if new_name != chat['name']:
                chat['name'] = new_name
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()
            
            c1, c2, c3 = st.columns(3)
            
            if c1.button("Open", key=f"btn_open_key_{idx}_{chat_id}"): 
                st.session_state.active_id = chat_id
                st.rerun()
                
            if c2.button("📌", key=f"btn_pin_key_{idx}_{chat_id}"): 
                chat['pinned'] = not chat.get('pinned', False)
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()
                
            if c3.button("🗑️", key=f"btn_del_key_{idx}_{chat_id}"): 
                if len(st.session_state.chats) > 1:
                    st.session_state.chats = [c for c in st.session_state.chats if c["id"] != chat_id]
                    if str(st.session_state.active_id) == str(chat_id):
                        st.session_state.active_id = st.session_state.chats[0]['id']
                else:
                    st.session_state.chats = [{"id": "main_default", "name": "Chat 1", "pinned": False, "messages": []}]
                    st.session_state.active_id = "main_default"
                    
                with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
                st.rerun()

# --- Main Interactive Chat Window Area ---
active_chat = next((c for c in st.session_state.chats if str(c["id"]) == str(st.session_state.active_id)), None)
if not active_chat:
    active_chat = st.session_state.chats[0]
    st.session_state.active_id = active_chat["id"]

# Render conversation bubbles safely
for msg in active_chat["messages"]:
    if isinstance(msg, dict):
        role = msg.get("role", "user")
        content = msg.get("content", "")
    else:
        role = "user"
        content = str(msg)
    with st.chat_message(role):
        st.markdown(content)

# Audio Microphone Component Interface 
audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop ⏹️", key="rec")

if audio and "last_audio" not in st.session_state:
    st.session_state.last_audio = audio
    audio_bytes = audio['bytes']
    
    # Fix 1: Typo safely cleared here
    r = sr.Recognizer()
    transcribed_text = ""
    
    try:
        # Fix 2: Convert standard raw recorded audio bytes cleanly to an uncorrupted WAV file via pydub
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
        wav_buffer = io.BytesIO()
        audio_segment.export(wav_buffer, format="wav")
        wav_buffer.seek(0)
        
        with sr.AudioFile(wav_buffer) as source:
            audio_data = r.record(source)
            transcribed_text = r.recognize_google(audio_data)
    except sr.UnknownValueError:
        transcribed_text = "⚠️ [Could not understand your speech. Try speaking again clearly!]"
    except Exception as e:
        transcribed_text = f"⚠️ [Audio processing issue]"

    if transcribed_text:
        active_chat["messages"].append({"role": "user", "content": f"🎤 Spoken: {transcribed_text}"})
        reply = f"I heard you say: '{transcribed_text}'. Let's continue working on your language flow!"
        active_chat["messages"].append({"role": "assistant", "content": reply})
        
        with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
        st.rerun()

if not audio and "last_audio" in st.session_state:
    del st.session_state.last_audio

# Chat Processing Text Bar
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    reply = f"Hello! I am your Fluency Coach. I received your text message: '{prompt}'. Let's keep practicing your English conversational skills!"
    active_chat["messages"].append({"role": "assistant", "content": reply})
    
    with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
    st.rerun()
