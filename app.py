import streamlit as st
from style import apply_custom_theme

apply_custom_theme()

# --- Initialize Session State ---
if "chats" not in st.session_state:
    st.session_state.chats = [{"id": 0, "name": "New Chat", "pinned": False, "messages": []}]
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = 0

st.title("Fluency Coach")

# --- Sidebar Logic (Rename/Pin/Delete) ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        new_id = len(st.session_state.chats)
        st.session_state.chats.append({"id": new_id, "name": f"Chat {new_id}", "pinned": False, "messages": []})
        st.rerun()

    st.subheader("Your Chats")
    for chat in st.session_state.chats:
        with st.expander(f"{'📌' if chat['pinned'] else ''} {chat['name']}"):
            # Rename functionality
            new_name = st.text_input("Rename:", value=chat['name'], key=f"rename_{chat['id']}")
            if new_name != chat['name']:
                chat['name'] = new_name
                st.rerun()
            
            c1, c2, c3 = st.columns(3)
            with c1:
                if st.button("Open", key=f"open_{chat['id']}"):
                    st.session_state.active_chat_id = chat['id']
                    st.rerun()
            with c2:
                if st.button("📌", key=f"pin_{chat['id']}"):
                    chat['pinned'] = not chat['pinned']
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"del_{chat['id']}"):
                    st.session_state.chats.remove(chat)
                    st.session_state.active_chat_id = 0
                    st.rerun()

# --- Main Chat Area ---
active_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.active_chat_id), st.session_state.chats[0])

# Display messages
for msg in active_chat["messages"]:
    with st.chat_message("user"):
        st.markdown(msg)

# Chat Input
if prompt := st.chat_input("Type your message here..."):
    active_chat["messages"].append(prompt)
    # Logic to "answer" (You can replace this with your LLM call later)
    active_chat["messages"].append(f"Coach: I heard you say '{prompt}'")
    st.rerun()
