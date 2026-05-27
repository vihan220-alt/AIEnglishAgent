import streamlit as st
import json
import os
import time
import io
import hashlib
from groq import Groq
from gtts import gTTS
from style import apply_custom_css

# Initial configurations
st.set_page_config(layout="wide", page_title="Fluency Coach")
apply_custom_css()

DATA_FILE = "chat_history.json"
client = Groq(api_key=st.secrets["GROQ_API_KEY"]) if "GROQ_API_KEY" in st.secrets else None

if "stop_audio" not in st.session_state:
    st.session_state.stop_audio = False
if "active_audio_bytes" not in st.session_state:
    st.session_state.active_audio_bytes = None
if "last_processed_audio_hash" not in st.session_state:
    st.session_state.last_processed_audio_hash = None

def load_data():
    default_chat = [{"id": "chat_default", "name": "Chat 1", "messages": [], "pinned": False}]
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                return json.loads(content) if content else default_chat
        except Exception:
            return default_chat
    return default_chat

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

if "chats" not in st.session_state: 
    st.session_state.chats = load_data()
if "active_idx" not in st.session_state: 
    st.session_state.active_idx = 0

def get_audio_bytes(text):
    try:
        tts = gTTS(text=text, lang='en', tld='co.uk')
        mp3_fp = io.BytesIO()
        tts.write_to_fp(mp3_fp)
        return mp3_fp.getvalue()
    except Exception:
        return None

def get_ai_response(conversation_history):
    if not client:
  def get_ai_response(messages):
    try:
        system_instruction = (
            "You are Gemini, an authentic, adaptive, and witty conversational collaborator. "
            "Your role is to act as a supportive, world-class English Fluency Coach. "
            "CRITICAL RESPONSE RULE: Keep all your answers short, crisp, and highly conversational. "
            "Never write long essays or bullet points. Limit your responses to a maximum of 2 to 3 sentences total. "
            "MANDATE: Speak, explain, and reply EXCLUSIVELY in English at all times, no matter what language the user types."
        )
        
        messages_payload = [{"role": "system", "content": system_instruction}] + messages
        
        messages_payload = [{"role": "system", "content": system_instruction}]
        )
        messages_payload = [{"role": "system", "content": system_instruction}]
        for m in conversation_history[-6:]:
            messages_payload.append({"role": m["role"], "content": m["content"]})
            
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload,
            temperature=0.6
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Error connecting to coach: {str(e)}"

# --- Workspace Sidebar Layout ---
with st.sidebar:
    st.header("Coach Workspace")
    if st.button("➕ New Chat"):
        new_chat = {"id": f"chat_{time.time()}", "name": f"Chat {len(st.session_state.chats)+1}", "messages": [], "pinned": False}
        st.session_state.chats.append(new_chat)
        save_data(st.session_state.chats)
        st.session_state.active_idx = len(st.session_state.chats) - 1
        st.session_state.active_audio_bytes = None  
        st.session_state.last_processed_audio_hash = None
        st.rerun()

    st.divider()
    
    for idx, chat in enumerate(st.session_state.chats):
        with st.expander(f"{'📌' if chat.get('pinned', False) else ''} {chat.get('name', 'Chat')}"):
            new_name = st.text_input("Rename", value=chat.get('name', 'Chat'), key=f"name_{idx}")
            if new_name != chat.get('name'):
                chat['name'] = new_name
                save_data(st.session_state.chats)
            
            c1, c2, c3 = st.columns(3)
            if c1.button("Open", key=f"open_{idx}"):
                st.session_state.active_idx = idx
                st.session_state.active_audio_bytes = None  
                st.session_state.last_processed_audio_hash = None
                st.rerun()
            if c2.button("📌", key=f"pin_{idx}"):
                chat['pinned'] = not chat.get('pinned', False)
                save_data(st.session_state.chats)
                st.rerun()
            if c3.button("🗑️", key=f"del_{idx}"):
                if len(st.session_state.chats) > 1:
                    st.session_state.chats.pop(idx)
                    st.session_state.active_idx = 0
                    st.session_state.active_audio_bytes = None
                    st.session_state.last_processed_audio_hash = None
                    save_data(st.session_state.chats)
                    st.rerun()

if st.session_state.active_idx >= len(st.session_state.chats):
    st.session_state.active_idx = 0

active_chat = st.session_state.chats[st.session_state.active_idx]
st.title(f"Fluency Coach: {active_chat.get('name', 'Chat')}")

if "messages" in active_chat and active_chat["messages"]:
    for msg in active_chat["messages"]:
        avatar_icon = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.markdown(msg["content"])
else:
    st.caption("This conversation is empty. Talk or type below!")

if st.session_state.active_audio_bytes and not st.session_state.stop_audio:
    st.audio(st.session_state.active_audio_bytes, format="audio/mp3", autoplay=True)
    st.session_state.active_audio_bytes = None  

st.divider()

if not st.session_state.stop_audio:
    if st.button("🛑 Stop Audio Response"):
        st.session_state.stop_audio = True
        st.session_state.active_audio_bytes = None
        st.rerun()
else:
    if st.button("▶️ Enable Audio Response"):
        st.session_state.stop_audio = False
        st.rerun()

# --- Custom Dual Input Container ---
with st.container():
    col_input, col_voice = st.columns([6, 2])
    with col_input:
        prompt = st.text_input(
            label="Ask Gemini Input", 
            placeholder="➕   Ask Gemini...", 
            label_visibility="collapsed",
            key="gemini_text_prompt"
        )
    with col_voice:
        audio_file = st.audio_input("Speak to your Coach 🎤", label_visibility="collapsed")

if audio_file:
    audio_bytes = audio_file.read()
    current_audio_hash = hashlib.sha256(audio_bytes).hexdigest()
    
    if st.session_state.last_processed_audio_hash != current_audio_hash:
        st.session_state.last_processed_audio_hash = current_audio_hash
        if client:
            with st.spinner("Listening to your voice..."):
                buffer = io.BytesIO(audio_bytes)
                buffer.name = "audio.wav"
                translation = client.audio.transcriptions.create(file=buffer, model="whisper-large-v3", response_format="text")
                user_text = translation.strip()
                
                if user_text:
                    if "messages" not in active_chat:
                        active_chat["messages"] = []
                    active_chat["messages"].append({"role": "user", "content": user_text})
                    
                    bot_reply = get_ai_response(active_chat["messages"])
                    active_chat["messages"].append({"role": "assistant", "content": bot_reply})
                    save_data(st.session_state.chats)
                    
                    st.session_state.active_audio_bytes = get_audio_bytes(bot_reply)
                    st.rerun()

if prompt:
    if "last_processed_prompt" not in st.session_state or st.session_state.last_processed_prompt != prompt:
        st.session_state.last_processed_prompt = prompt
        st.session_state.active_audio_bytes = None  
        
        if "messages" not in active_chat:
            active_chat["messages"] = []
        active_chat["messages"].append({"role": "user", "content": prompt})
        
        bot_reply = get_ai_response(active_chat["messages"])
        active_chat["messages"].append({"role": "assistant", "content": bot_reply})
        save_data(st.session_state.chats)
        st.rerun()
