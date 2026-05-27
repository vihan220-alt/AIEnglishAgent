import streamlit as st
import os
from groq import Groq
from audio import get_audio_bytes
from message import save_data, load_data

# Initialize Groq Client
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Page Configuration
st.set_page_config(page_title="Fluency Coach", page_icon="👑", layout="wide")

# Custom CSS Import safely handled at top level
try:
    from style import apply_custom_css
    apply_custom_css()
except Exception as e:
    pass

# Helper to Initialize Session States
if "chats" not in st.session_state:
    st.session_state.chats = load_data()
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = "Chat 1"
if "active_audio_bytes" not in st.session_state:
    st.session_state.active_audio_bytes = None

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
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload,
            temperature=0.7,
            max_tokens=150,
            top_p=1,
            stream=False
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# --- Sidebar Workspace Navigation ---
st.sidebar.title("Workspace")
if st.sidebar.button("➕ New Chat", key="new_chat_btn"):
    new_id = f"Chat {len(st.session_state.chats) + 1}"
    st.session_state.chats[new_id] = []
    st.session_state.active_chat_id = new_id
    save_data(st.session_state.chats)
    st.rerun()

# List Available Chats
for chat_id in list(st.session_state.chats.keys()):
    if st.sidebar.button(f"👉 {chat_id}", key=f"nav_{chat_id}"):
        st.session_state.active_chat_id = chat_id
        st.session_state.active_audio_bytes = None
        st.rerun()

# Set current active chat reference context
active_chat_id = st.session_state.active_chat_id
active_chat = st.session_state.chats[active_chat_id]

st.title(f"Fluency Coach: {active_chat_id}")

# --- Render Chat History Interface ---
if not active_chat:
    st.info("This conversation is empty. Talk or type below!")
else:
    for msg in active_chat:
        role_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
        st.markdown(f'<div class="{role_class}">{msg["content"]}</div>', unsafe_allow_html=True)

# --- Render Persistent Audio Output ---
if st.session_state.active_audio_bytes:
    st.audio(st.session_state.active_audio_bytes, format="audio/mp3", autoplay=True)
    if st.button("🛑 Stop Audio Response"):
        st.session_state.active_audio_bytes = None
        st.rerun()

st.write("---")

# --- Process New Messages (Inputs) ---
user_text = st.chat_input("Type your message here...")
if user_text:
    # Append User Message
    active_chat.append({"role": "user", "content": user_text})
    
    # Prune history keeping only the latest 6 interactions to avoid token spillover
    context_history = active_chat[-6:]
    
    # Generate Assistant Short Response
    bot_reply = get_ai_response(context_history)
    active_chat.append({"role": "assistant", "content": bot_reply})
    
    # Save Data Permanently
    save_data(st.session_state.chats)
    
    # Process Voice Generation
    try:
        st.session_state.active_audio_bytes = get_audio_bytes(bot_reply)
    except Exception:
        st.session_state.active_audio_bytes = None
        
    st.rerun()
