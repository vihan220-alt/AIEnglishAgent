import streamlit as st

def apply_custom_theme():
    st.markdown(
        """
        <style>
        /* Force sidebar text, widget labels, and subheaders to be dark/visible */
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span {
            color: #1E293B !important;  /* Dark Slate color */
        }

        /* Fix text color inside buttons/logs in the sidebar */
        [data-testid="stSidebar"] button div p {
            color: #1E293B !important;
        }

        /* Ensure input fields have readable dark text typing */
        [data-testid="stSidebar"] input {
            color: #000000 !important;
        }
        </style>
        """,
        unsafe_html=True
    )
