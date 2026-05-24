import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Safely reset the table structure
    c.execute('DROP TABLE IF EXISTS conversations')
    c.execute('''CREATE TABLE conversations 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, is_pinned INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Initialize the database correctly
init_db()

# --- Sidebar ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        conn.execute("INSERT INTO conversations (name) VALUES (?)", (f"Chat",))
        conn.commit()
        conn.close()
        st.rerun()

    st.subheader("Your Chats")
    conn = sqlite3.connect(DB_FILE)
    # This query matches the table created above
    chats = conn.execute("SELECT id, name, is_pinned FROM conversations").fetchall()
    conn.close()

    for chat_id, name, pinned in chats:
        c1, c2 = st.columns([3, 1])
        with c1:
            st.button(f"{'📌' if pinned else ''} {name}", key=f"btn_{chat_id}", use_container_width=True)
        with c2:
            with st.popover("⋮"):
                if st.button("🗑️ Delete", key=f"del_{chat_id}"):
                    conn = sqlite3.connect(DB_FILE)
                    conn.execute("DELETE FROM conversations WHERE id = ?", (chat_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()

# --- Main Interface ---
st.title("Fluency Coach")
col1, col2 = st.columns(2)
with col1:
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with col2:
    st.button("Stop Audio 🔇")
st.chat_input("Type your message here...")
