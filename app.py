import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

# --- 1. Database Setup ---
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Safely ensure table exists
    c.execute('CREATE TABLE IF NOT EXISTS conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
    conn.commit()
    conn.close()

def get_chats():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name FROM conversations")
    chats = c.fetchall()
    conn.close()
    return chats

# --- 2. Sidebar Layout ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    
    # New Chat Button
    if st.button("➕ New Chat"):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO conversations (name) VALUES (?)", ("New Chat",))
        conn.commit()
        conn.close()
        st.rerun()

    st.subheader("Your Chats")
    # List Existing Chats
    for chat_id, name in get_chats():
        col1, col2 = st.columns([3, 1])
        with col1:
            st.button(name, key=f"btn_{chat_id}")
        with col2:
            if st.button("🗑️", key=f"del_{chat_id}"):
                conn = sqlite3.connect(DB_FILE)
                conn.execute("DELETE FROM conversations WHERE id = ?", (chat_id,))
                conn.commit()
                conn.close()
                st.rerun()

# --- 3. Main Interface ---
st.title("Fluency Coach")

col1, col2 = st.columns(2)
with col1:
    st.write("**Voice Control**")
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with col2:
    st.write("**Audio Controls**")
    st.button("Stop Audio 🔇")

st.chat_input("Type your message here...")
