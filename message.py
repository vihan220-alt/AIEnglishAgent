import streamlit as st

def display_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    for msg in st.session_state.messages:
        with st.chat_message("user"):
            st.markdown(msg)

    if prompt := st.chat_input("Type your message here..."):
        st.session_state.messages.append(prompt)
        st.rerun()
