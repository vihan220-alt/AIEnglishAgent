import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
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

# --- Sidebar Management ---
with st.sidebar:
    st.markdown("### 🤖 Coach Workspace")
    if st.button("➕ New chat"):
        # Logic to create new chat
        st.rerun()
    
    st.write("---")
    st.write("##### Your Chats")
    for room_id, pinned in get_rooms():
        # Select Chat
        if st.button(f"{'📌 ' if pinned else ''}{room_id}"):
            st.session_state.active_id = room_id
            st.rerun()
        
        # Management Options (Only show for active chat)
        if st.session_state.get("active_id") == room_id:
            with st.expander("⚙️ Chat Settings Menu"):
                if st.button("📌 Pin/Unpin"):
                    # Pin logic
                    st.rerun()
                new_name = st.text_input("New Name")
                if st.button("💾 Rename"):
                    # Rename logic
                    st.rerun()
                if st.button("🗑️ Delete"):
                    # Delete logic
                    st.rerun()

# --- Chat Display ---
st.title("Fluency Coach")
st.write(f"Active: {st.session_state.get('active_id', 'None')}")
