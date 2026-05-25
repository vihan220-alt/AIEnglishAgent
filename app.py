# --- Sidebar ---
with st.sidebar:
    st.header("🤖 Coach Workspace")
    if st.button("➕ New Chat"):
        new_id = len(st.session_state.chats)
        st.session_state.chats.append({"id": new_id, "name": f"Chat {new_id}", "pinned": False, "messages": []})
        st.rerun()

    # Use a unique key by combining chat ID and a static string
    for chat in st.session_state.chats:
        with st.expander(f"{'📌' if chat['pinned'] else ''} {chat['name']}"):
            # We use a unique key here that includes the chat ID
            new_name = st.text_input("Rename", value=chat['name'], key=f"input_{chat['id']}")
            if new_name != chat['name']:
                chat['name'] = new_name
                # Save here...
                
            c1, c2, c3 = st.columns(3)
            if c1.button("Open", key=f"open_{chat['id']}"): 
                st.session_state.active_id = chat['id']
                st.rerun()
            if c2.button("📌", key=f"pin_{chat['id']}"): 
                chat['pinned'] = not chat['pinned']
                st.rerun()
            if c3.button("🗑️", key=f"del_{chat['id']}"): 
                st.session_state.chats.remove(chat)
                st.rerun()
