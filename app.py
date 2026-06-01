import streamlit as st
import json
import os
from groq import Groq
from gTTS import gTTS
import io
from streamlit_mic_recorder import mic_recorder

# --- Page Configuration ---
st.set_page_config(page_title="Versatile AI", layout="wide")

# --- CSS Styling ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117 !important;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='60' height='60' viewBox='0 0 60 60'%3E%3Cpath d='M10 20h10v10H10zm30 0h10v10H40zM15 42h30v4H15zM5 10h50v40H5zm2 2v36h46V12zm18-7h10v3H25z' fill='%2330363d' fill-opacity='0.4' fill-rule='evenodd'/%3E%3C/svg%3E") !important;
    }
    div[data-testid="stChatMessage"] { background-color: #161b22 !important; border: 2px solid #444c56 !important; border-radius: 8px !important; }
    </style>
""", unsafe_allow_html=True)

# --- Data Persistence ---
DATA_FILE = "chats.json"
if "chats" not in st.session_state:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: st.session_state.chats = json.load(f)
    else: st.session_state.chats = {"Chat 1": []}

if "active_chat" not in st.session_state: st.session_state.active_chat = "Chat 1"

# --- Sidebar ---
with st.sidebar:
    st.title("Workspace")
    if st.button("➕ New Chat"):
        new_id = f"Chat {len(st.session_state.chats) + 1}"
        st.session_state.chats[new_id] = []
        st.session_state.active_chat = new_id
        with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
        st.rerun()
    
    for chat_id in st.session_state.chats.keys():
        if st.button(chat_id):
            st.session_state.active_chat = chat_id
            st.rerun()

# --- Main Chat ---
st.title(f"Assistant: {st.session_state.active_chat}")

for msg in st.session_state.chats[st.session_state.active_chat]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask me anything..."):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    st.session_state.chats[st.session_state.active_chat].append({"role": "user", "content": prompt})
    
    # Corrected message structure to avoid syntax errors
    system_msg = {"role": "system", "content": "You are a helpful and versatile AI assistant."}
    messages_to_send = [system_msg] + st.session_state.chats[st.session_state.active_chat][-5:]
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages_to_send
    ).choices[0].message.content
    
    st.session_state.chats[st.session_state.active_chat].append({"role": "assistant", "content": response})
    with open(DATA_FILE, "w") as f: json.dump(st.session_state.chats, f)
    
    tts = gTTS(text=response, lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    st.audio(fp.getvalue(), format="audio/mp3", autoplay=True)
    st.rerun()
