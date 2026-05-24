import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

# --- Force Database Reset ---
DB_FILE = "coach_data.db"
conn = sqlite3.connect(DB_FILE)
conn.execute('DROP TABLE IF EXISTS conversations')
conn.execute('CREATE TABLE conversations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)')
conn.commit()
conn.close()

# --- UI Setup ---
st.set_page_config(layout="wide")

# --- Sidebar ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO conversations (name) VALUES (?)", ("New Chat",))
        conn.commit()
        conn.close()
        st.rerun()

    st.subheader("Your Chats")
    conn = sqlite3.connect(DB_FILE)
    chats = conn.execute("SELECT id, name FROM conversations").fetchall()
    conn.close()

    for chat_id, name in chats:
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

# --- Main Interface ---
st.title("Fluency Coach")
col1, col2 = st.columns(2)
with col1:
    mic_recorder(start_prompt="Speak 🎤", stop
