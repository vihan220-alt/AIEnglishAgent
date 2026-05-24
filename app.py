import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

# --- 1. Database Setup ---
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)''')
    conn.commit()
    conn.close()

def add_chat(name):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO conversations (name) VALUES (?)", (name,))
    conn.commit()
    conn.close()

def delete_chat(chat_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM conversations WHERE id = ?", (chat_id,))
    conn.commit()
    conn.close()

init_db()

# --- 2. Sidebar Layout ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    
    # Add new chat
    if st.button("➕ New Chat"):
        add_chat(f"New Chat {len(get_chats()) + 1}")
        st.rerun()

    st.subheader("Your Chats")
    # Display chats
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name FROM conversations")
    chats = c.fetchall()
    conn.close()

    for chat_id, name in chats:
        c1, c2 = st.columns([3, 1])
        with c1:
            if st.button(name, key=f"btn_{chat_id}"):
                st.session_state.active_id = chat_id
        with c2:
            if st.button("🗑️", key=f"del_{chat_id}"):
                delete_chat(chat_id)
                st.rerun()

# --- 3. Main Chat Interface ---
st.title("Fluency Coach")

# Voice & Control Layout
col1, col2 = st.columns(2)
with col1:
    st.write("**Voice Input**")
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with col2:
    st.write("**Controls**")
    if st.button("Stop Audio 🔇"):
        st.rerun()

st.chat_input("Type your message here...")
