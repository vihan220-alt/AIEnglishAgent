import streamlit as st
from streamlit_mic_recorder import mic_recorder
import requests
import json
import sqlite3

# --- Setup ---
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

# --- Sidebar Logic ---
with st.sidebar:
    st.markdown("### 🤖 Coach Workspace")
    
    if st.button("➕ New chat"):
        # Add logic to generate a new room_id here
        st.rerun()
    
    st.markdown("---")
    st.write("##### Your Chats")
    
    for room_id, pinned in get_rooms():
        # Display the chat button
        if st.button(f"{'📌 ' if pinned else ''}{room_id}"):
            st.session_state.active_id = room_id
            st.rerun()
        
        # Nested Management Options (Only show for the active chat)
        if st.session_state.get("active_id") == room_id:
            with st.expander("⚙️ Chat Settings"):
                if st.button("📌 Pin/Unpin", key=f"pin_{room_id}"):
                    # Pin logic goes here
                    st.rerun()
                
                new_name = st.text_input("New Name", key=f"name_{room_id}")
                if st.button("💾 Rename", key=f"rename_{room_id}"):
                    # Rename logic goes here
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"del_{room_id}"):
                    # Delete logic goes here
                    st.rerun()

# --- Main Interface ---
st.title("Fluency Coach")
st.write(f"Active Session: **{st.session_state.get('active_id', 'None')}**")
