import streamlit as st
from streamlit_mic_recorder import mic_recorder
import json
import sqlite3

# --- Database & Setup ---
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (room_id TEXT PRIMARY KEY, history_json TEXT, is_pinned INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def get_rooms():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT room_id, is_pinned FROM conversations ORDER BY is_pinned DESC")
    rooms = c.fetchall()
    conn.close()
    return rooms

# --- Sidebar (Chat List & 3-Dot Options) ---
with st.sidebar:
    st.markdown("### 🤖 Coach Workspace")
    if st.button("➕ New chat"):
        # Logic to create new chat session
        st.rerun()
    
    st.markdown("---")
    for room_id, pinned in get_rooms():
        # Select Chat
        if st.button(f"{'📌 ' if pinned else ''}{room_id}"):
            st.session_state.active_id = room_id
            st.rerun()
        
        # 3-Dot Options Menu (Only for the active chat)
        if st.session_state.get("active_id") == room_id:
            with st.expander("⋮ Options"): # This acts as your 3-dots menu
                if st.button("📌 Pin/Unpin", key=f"p_{room_id}"):
                    # Add Pin Logic
                    st.rerun()
                if st.button("✏️ Rename", key=f"r_{room_id}"):
                    # Add Rename Logic
                    st.rerun()
                if st.button("🗑️ Delete", key=f"d_{room_id}"):
                    # Add Delete Logic
                    st.rerun()

# --- Main Chat Area (Speak/Stop Buttons) ---
st.title("Fluency Coach")
st.write(f"Active Session: **{st.session_state.get('active_id', 'None')}**")

# Interaction Row
col1, col2 = st.columns(2)
with col1:
    st.write("**🎙️ Voice Control:**")
    audio = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with col2:
    st.write("**🛑 Controls:**")
    if st.button("Stop Audio 🔇"):
        # Add Stop logic
        st.rerun()

st.chat_input("Type your message here...")
