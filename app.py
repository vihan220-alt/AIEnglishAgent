import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

# --- Database & Setup ---
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Ensure the table has the right columns
    c.execute('''CREATE TABLE IF NOT EXISTS conversations 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, is_pinned INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def get_chats():
    init_db()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, is_pinned FROM conversations ORDER BY is_pinned DESC")
    chats = c.fetchall()
    conn.close()
    return chats

init_db()

# --- Sidebar ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO conversations (name) VALUES (?)", (f"Chat {len(get_chats()) + 1}",))
        conn.commit()
        conn.close()
        st.rerun()

    st.subheader("Your Chats")
    for chat_id, name, pinned in get_chats():
        # Sidebar Chat Row
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(f"{'📌' if pinned else ''} {name}", key=f"btn_{chat_id}", use_container_width=True):
                st.session_state.active_id = chat_id
        with col2:
            # The "3-dots" (options) menu
            with st.popover("⋮"):
                if st.button("🗑️ Delete", key=f"del_{chat_id}"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("DELETE FROM conversations WHERE id = ?", (chat_id,))
                    conn.commit()
                    conn.close()
                    st.rerun()
                if st.button("✏️ Rename", key=f"ren_{chat_id}"):
                    # Renaming logic
                    st.rerun()

# --- Main Area ---
st.title("Fluency Coach")
st.write(f"Active Session: {st.session_state.get('active_id', 'None')}")

col1, col2 = st.columns(2)
with col1:
    st.write("**🎙️ Voice Input**")
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇")
with col2:
    st.write("**🛑 Controls**")
    st.button("Stop Audio 🔇")

st.chat_input("Type your message here...")
