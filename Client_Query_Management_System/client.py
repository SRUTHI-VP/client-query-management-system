import streamlit as st
from db import get_connection
from datetime import datetime
import re
import time

def client_interface():
    st.subheader("Submit a Query")

    for key in ["name", "email", "mobile", "heading", "description", "clear_form"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key != "clear_form" else False


    if st.session_state.clear_form:
        st.session_state.update({
            "name" :"",
            "email": "",
            "mobile": "",
            "heading": "",
            "description": "",
            "clear_form": False
        })

    
    name = st.text_input("Username", value=st.session_state.name, key="name")
    email = st.text_input("Email", value=st.session_state.email, key="email")
    mobile = st.text_input("Mobile", value=st.session_state.mobile, key="mobile")
    heading = st.text_input("Query Heading", value=st.session_state.heading, key="heading")
    description = st.text_area("Query Description", value=st.session_state.description, key="description")

    submitted = st.button("Submit")

    if submitted:
        errors = []

        if not email or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            errors.append("Invalid or missing email format.")
        if not mobile or not mobile.isdigit() or len(mobile) != 10:
            errors.append("Mobile number must be exactly 10 digits.")
        if not heading.strip():
            errors.append("Query heading is required.")
        if not description.strip():
            errors.append("Query description is required.")
        if name.strip().lower() != st.session_state.get('username', '').strip().lower():
            errors.append("Username does not match the logged-in Username.")


        if errors:
            st.error("Please correct the following errors before resubmitting:")
            for err in errors:
                st.write(f"- {err}")
        else:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO queries (name, email, mobile, heading, description, query_created_time, status, query_closed_time)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (name, email, mobile, heading, description, datetime.now(), "Open", None))
                conn.commit()
                conn.close()
                st.success("Your query has been submitted successfully")
                time.sleep(2)
                st.session_state.clear_form = True
                st.rerun()

            except Exception as e:
                st.error(f"Submission failed: {e}")


