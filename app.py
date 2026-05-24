import streamlit as st
from streamlit_mic_recorder import mic_recorder

# --- 1. Background Style ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        background-image: url("https://cdn-icons-png.flaticon.com/512/4712/4712035.png");
        background-size: 80px;
    }
    h1, h2, p { color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. Interface ---
st.title("Fluency Coach")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for msg in st.session_state.messages:
    with st.chat_message("user"):
        st.markdown(msg)

# Clean chat input
if prompt := st.chat_input("Type your message here..."):
    st.session_state.messages.append(prompt)
    st.rerun()

# Controls
c1, c2 = st.columns(2)
with c1:
    mic_recorder(start_prompt="Speak 🎤", stop_prompt="Submit 🔇", key="rec")
with c2:
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
