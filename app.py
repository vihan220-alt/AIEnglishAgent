import streamlit as st
from streamlit_mic_recorder import mic_recorder
import sqlite3

# --- Database Setup ---
DB_FILE = "coach_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Force creation of the correct schema
    c.execute('DROP TABLE IF EXISTS conversations')
    c.execute('''CREATE TABLE conversations 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, is_pinned INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

# Only initialize if the table doesn't exist to prevent constant resetting
def check_or_init():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("SELECT is_pinned FROM conversations LIMIT 1")
    except sqlite3.OperationalError:
        init_db()
    conn.close()

check_or_init()

# --- Sidebar ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat", use_container_width=True):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO conversations (name) VALUES (?)", (f"Chat {len(list(c.execute('SELECT id FROM conversations')))+1}",))
        conn.commit()
        conn.close()
        st.rerun()

    st.subheader("Your Chats")
    conn = sqlite3.connect(DB_FILE)
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
