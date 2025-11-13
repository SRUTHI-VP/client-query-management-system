import streamlit as st
from auth import login_user
from client import client_interface
from support import support_dashboard
import plotly.express as px

import pandas as pd
from db import get_connection

def get_query_status_counts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM queries GROUP BY status")
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=["Status", "Count"])


st.set_page_config(page_title="Client Query Management System", layout="centered")
st.markdown(
    """
    <style>
    .stApp {
        background-color: #e6f7ff; /* Light blue */
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.title("Client Query Management System")


if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'


if st.session_state['page'] == 'login':
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    selected_role = st.radio("Select your role", ["Client", "Support"] , index = None )
    

    if st.button("Login"):
        actual_role = login_user(username, password)
        if actual_role:
            if actual_role == selected_role:
                st.session_state['role'] = actual_role
                st.session_state['username'] = username
                st.session_state['logged_in'] = True

                
                if actual_role == "Client":
                    st.session_state['page'] = 'client_query'
                elif actual_role == "Support":
                    st.session_state['page'] = 'support_dashboard'

                st.rerun()
            else:
                st.error("Selected role does not match your account role.")
        else:
            st.error("Invalid username or password")


elif st.session_state['page'] == 'client_query':
    st.sidebar.title(f"Welcome, {st.session_state['username']}")
    st.sidebar.write("Role: Client")
    client_interface()


elif st.session_state['page'] == 'support_dashboard':
     st.sidebar.title(f"Welcome, {st.session_state['username']}")
     st.sidebar.write("Role: Support")
     page = st.sidebar.radio("Support Navigation", ["Query Management","Support Analytics"])
     if page == "Query Management":
        support_dashboard()
     elif page == "Support Analytics":
        st.subheader(" Query Status Overview")
        df = get_query_status_counts()

        if not df.empty:
            fig = px.pie(df, names='Status', values='Count', title='Open vs Closed Queries')
            st.plotly_chart(fig, use_container_width=True)

else:
        st.info("No query data available yet.")


if st.session_state['logged_in']:
    if st.sidebar.button("Logout"):
        st.session_state['role'] = None
        st.session_state['username'] = None
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'  
        st.rerun()