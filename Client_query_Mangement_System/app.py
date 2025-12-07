import streamlit as st
from auth import login_user
from client import submit_query
from client import track_query
from support import support_dashboard
from support import support_team_page
from support import get_query_status_counts
from support import query_summary_page
import plotly.express as px
# import pandas as pd
# st.set_page_config(page_title="Client Query Management System", layout="centered")
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
# st.title("Client Query Management System")

#  Initialize session state
if 'role' not in st.session_state:
    st.session_state['role'] = None
if 'username' not in st.session_state:
    st.session_state['username'] = None
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# Login Page
if st.session_state['page'] == 'login':
    st.title("Client Query Management System")
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    selected_role = st.radio("Select your role", ["Client", "Support"] , index = None )
    #selected_role = st.radio("Select your role", ["Client", "Support"], index=0)

    if st.button("Login"):
        actual_role = login_user(username, password)
        if actual_role:
            if actual_role == selected_role:
                st.session_state['role'] = actual_role
                st.session_state['username'] = username
                st.session_state['logged_in'] = True

                #  Redirect based on role
                if actual_role == "Client":
                    st.session_state['page'] = 'client_query'
                elif actual_role == "Support":
                    st.session_state['page'] = 'support_dashboard'

                st.rerun()
            else:
                st.error("Selected role does not match your account role.")
        else:
            st.error("Invalid username or password")

# Client Query Page
elif st.session_state['page'] == 'client_query':
    st.sidebar.title(f"Welcome, {st.session_state['username']}")
    st.sidebar.write("Role: Client")
    page = st.sidebar.radio("Client Navigation", ["Submit query","Track query"])
    if page == "Submit query":
        
            submit_query()

    elif page == "Track query":
        
        track_query()
        
#  Support Dashboard Page
elif st.session_state['page'] == 'support_dashboard':
     st.sidebar.title(f"Welcome, {st.session_state['username']}")
     st.sidebar.write("Role: Support")
     page = st.sidebar.radio("Support Navigation", ["Query Summary","Query Management","Support Analytics","Performance"])
     if page == "Query Summary":
        
        query_summary_page()
     
     elif page == "Query Management":
        
        support_dashboard()


     elif page == "Performance":
         
         support_team_page()

     elif page == "Support Analytics":
        st.subheader(" Query Status Overview")
     

        df = get_query_status_counts()
        
        if not df.empty:
            fig = px.pie(df, names='Status', values='Count', title='Open vs Closed Queries',
                          width = 400,
                         height = 400)
            st.plotly_chart(fig, use_container_width=False)
      
else:
        st.info("No query data available yet.")


#Logout Button — always available when logged in
if st.session_state['logged_in']:
    if st.sidebar.button("Logout"):
        st.session_state['role'] = None
        st.session_state['username'] = None
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'  # Redirect to login page
        st.rerun()
        
