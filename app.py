# --- Main Interaction ---
# 1. Define the active chat correctly
active_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.active_id), st.session_state.chats[0])

# 2. Display existing messages FIRST
for msg in active_chat["messages"]:
    st.chat_message("user").markdown(msg)

# 3. Handle new message input
if prompt := st.chat_input("Type your message..."):
    # Add to list
    active_chat["messages"].append(prompt)
    # Save to file
    with open("chat_history.json", "w") as f:
        json.dump(st.session_state.chats, f)
    # RERUN to show the message immediately
    st.rerun()
