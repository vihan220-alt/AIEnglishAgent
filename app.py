# --- Main Interaction ---
active_chat = next((c for c in st.session_state.chats if c["id"] == st.session_state.active_chat_id), st.session_state.chats[0])

# Display existing messages
for msg in active_chat["messages"]:
    st.chat_message("user").markdown(msg)

# Voice Recorder
st.write("### 🎙️ Speech Input")
# The 'audio_info' contains the recording data
audio_info = mic_recorder(start_prompt="Speak 🎤", stop_prompt="Stop ⏹️", key="recorder_unique")

if audio_info:
    # 1. This is where you would normally call a transcription API (like Whisper)
    # 2. For now, we simulate the text output so you see it in the chat
    simulated_text = "Voice Input: Hello! How are you?" 
    
    # 3. Add to messages and save
    active_chat["messages"].append(simulated_text)
    save_data(st.session_state.chats)
    st.rerun()

# Text Input
if prompt := st.chat_input("Type your message..."):
    active_chat["messages"].append(f"User: {prompt}")
    save_data(st.session_state.chats)
    st.rerun()
