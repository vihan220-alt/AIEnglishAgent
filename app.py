import streamlit as st
from streamlit_mic_recorder import mic_recorder
from style import apply_custom_theme

apply_custom_theme()

# --- Initialize Session State ---
if "chats" not in st.session_state:
    st.session_state.chats = [{"id": 1, "name": "Chat 1", "pinned": False, "messages": []}]
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = 1

st.title("Fluency Coach")

# --- Sidebar Logic ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        new_id = len(st.session_state.chats) + 1
        st.session_state.chats.append({"id": new_id, "name": f"Chat {new_id}", "pinned": False, "messages": []})
        st.rerun()

    st.subheader("Your Chats")
    # Sort: Pinned chats first
    sorted_chats = sorted(st.session_state.chats, key=lambda x: not x["pinned"])
    
    for chat in sorted_chats:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            if st.button(f"{'📌' if chat['pinned'] else ''} {chat['name']}", key=f"sel_{chat['id']}"):
                st.session_state.active_chat_id = chat['id']
        with col2:
            if st.button("📌", key=f"pin_{chat['id']}"):
                chat['pinned'] = not chat['pinned']
                st.rerun()
        with col3:
            if st.button("🗑️", key=f"del_{chat['id']}"):
                st.session_state.chats.remove(chat)
                st.rerun()

# --- Main Chat Area ---
active_chat = next(c for c in st.session_state.chats if c["id"] == st.session_state.active_chat_id)

for msg in active_chat["messages"]:
    with st.chat_message("user"):
        st.markdown(msg)

if prompt := st.chat_input("Type your message here..."):
    active_chat["messages"].append(prompt)
    st.rerun()
