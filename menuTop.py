# app.py
import pandas as pd
import streamlit as st

# Hide the default Streamlit header and footer
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# Custom CSS for menu and layout
st.markdown("""
    <style>
        .css-18e3th9 {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }
        .css-1d391kg {
            padding-top: 0rem;
            padding-bottom: 0rem;
        }
        .menu-container {
            display: flex;
            justify-content: space-between;
            background-color: #f0f2f6;
            padding: 10px;
            margin: 0;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 999;
        }
        .menu-item {
            padding: 8px 16px;
            text-decoration: none;
            color: #0066cc;
            cursor: pointer;
        }
        .menu-item:hover {
            background-color: #e1e5ea;
            border-radius: 4px;
        }
        .content {
            margin-top: 60px;
        }
    </style>
""", unsafe_allow_html=True)

# Create menu with session state
if 'menu_selection' not in st.session_state:
    st.session_state.menu_selection = 'Home'

# Menu buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button('Home'):
        st.session_state.menu_selection = 'Home'
with col2:
    if st.button('About'):
        st.session_state.menu_selection = 'About'
with col3:
    if st.button('Services'):
        st.session_state.menu_selection = 'Services'
with col4:
    if st.button('Contact'):
        st.session_state.menu_selection = 'Contact'

# Content based on menu selection
if st.session_state.menu_selection == 'Home':
    st.title("Main Content")
    st.write("This is the main content of your application.")

    st.header("Sample Section")
    st.write("Here's some sample text content.")

    # Add a sample chart
    import numpy as np

    chart_data = pd.DataFrame(
        np.random.randn(20, 3),
        columns=['A', 'B', 'C'])
    st.line_chart(chart_data)

elif st.session_state.menu_selection == 'About':
    st.title("About")
    st.header("Contact Information")
    st.write("Phone Number: 05543216547")

elif st.session_state.menu_selection == 'Services':
    st.title("Services")
    st.write("Our services content goes here.")

elif st.session_state.menu_selection == 'Contact':
    st.title("Contact")
    st.write("Contact page content goes here.")
