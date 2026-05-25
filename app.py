import streamlit as st
import json
import os
import io
import time
import base64
import speech_recognition as sr
from gtts import gTTS
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

    sorted_chats = sorted(st.session_state.chats, key=lambda x: x.get("pinned", False), reverse=True)

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

# Function to generate auto-playing HTML audio players with an embedded stop control
def generate_audio_html(text):
    tts = gTTS(text=text, lang='en', tld='co.uk')
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    b64 = base64.b64encode(mp3_fp.read()).decode()
    return f'<audio src="data:audio/mp3;base64,{b64}" autoplay controls></audio>'

# Render conversation bubbles cleanly
for msg in active_chat["messages"]:
    role = msg.get("role", "user") if isinstance(msg, dict) else "user"
    content = msg.get("content", "") if isinstance(msg, dict) else str(msg)
    
    with st.chat_message(role):
        st.markdown(content, unsafe_allow_html=True)
        if role == "assistant" and isinstance(msg, dict) and msg.get("audio_html"):
            st.markdown(msg["audio_html"], unsafe_allow_html=True)

# Main Voice Input Component
st.write("### Speak to your Coach:")
audio_file = st.audio_input("Record your voice")

if audio_file is not None:
    # Read file bytes
    audio_bytes = audio_file.read()
    
    # Check if this is a new voice message to avoid processing loops
    audio_hash = str(len(audio_bytes))
    if st.session_state.get("last_processed_audio") != audio_hash:
        st.session_state.last_processed_audio = audio_hash
        
        r = sr.Recognizer()
        transcribed_text = ""
        
        try:
            with sr.AudioFile(io.BytesIO(audio_bytes)) as source:
                audio_data = r.record(source)
                transcribed_text = r.recognize_google(audio_data)
        except sr.UnknownValueError:
            transcribed_text = "⚠️ [Could not interpret audio track clearly. Please speak again!]"
        except Exception as e:
            transcribed_text = "⚠️ [Voice data translation issue]"

        if transcribed_text and not transcribed_text.startswith("⚠️"):
            active_chat["messages"].append({"role": "user", "content": f"🎤 Spoken: {transcribed_text}"})
            
            reply_text = f"I heard you say: '{transcribed_text}'. Let's continue working on your language flow!"
            audio_player_html = generate_audio_html(reply_text)
            
            active_chat["messages"].append({
                "role": "assistant", 
                "content": reply_text,
                "audio_html": audio_player_html
            })
            
            with open(DATA_FILE, "w") as f: 
                json.dump(st.session_state.chats, f)
            st.rerun()

# Chat Processing Text Input Bar
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append({"role": "user", "content": prompt})
    
    # Text-only replies do NOT attach audio streams
    reply_text = f"Hello! I am your Fluency Coach. I received your text message: '{prompt}'. Let's keep practicing your English conversational skills!"
    active_chat["messages"].append({
        "role": "assistant", 
        "content": reply_text
    })
    
    with open(DATA_FILE, "w") as f: 
        json.dump(st.session_state.chats, f)
    st.rerun()
