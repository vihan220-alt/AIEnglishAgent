import streamlit as st

def apply_custom_theme():
    """
    Applies clean UI custom themes and styles to the Streamlit app workspace.
    """
    st.markdown(
        """
        <style>
        /* Custom UI design tweaks can go here */
        .stChatMessage {
            border-radius: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
