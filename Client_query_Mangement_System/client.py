import streamlit as st
from db import get_connection
from datetime import datetime
import re
import time
import pandas as pd

def submit_query():
    st.subheader("Submit a Query")

    # Initialize session state
    for key in ["name", "email", "mobile", "heading", "description", "clear_form"]:
        if key not in st.session_state:
            st.session_state[key] = "" if key != "clear_form" else False

    # Clear form if flag is set
    if st.session_state.clear_form:
        st.session_state.update({
            "name" :"",
            "email": "",
            "mobile": "",
            "heading": "",
            "description": "",
            "clear_form": False
        })

    # Input fields
    name = st.text_input("Username", value=st.session_state.name, key="name")
    email = st.text_input("Email", value=st.session_state.email, key="email")
    mobile = st.text_input("Mobile", value=st.session_state.mobile, key="mobile")
    heading = st.text_input("Query Heading", value=st.session_state.heading, key="heading")
    description = st.text_area("Query Description", value=st.session_state.description, key="description")

    # Submit button
    submitted = st.button("Submit")

    # Submission logic with post-submit validation
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

                # Clear fields and rerun
                st.session_state.clear_form = True
                st.rerun()

            except Exception as e:
                st.error(f"Submission failed: {e}")

def track_query():
    st.subheader("Track your queries")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch only queries for the logged-in user
    cursor.execute("""
        SELECT 
            id AS Query_ID,
            name AS Username,
            heading AS Heading,
            description AS Description,
            query_created_time AS Open_Date,
            query_closed_time AS Closed_Date,
            status AS Status,
            closed_by AS Closed_By
        FROM queries
        WHERE name = %s
        ORDER BY query_created_time DESC
    """, (st.session_state['username'],))

    results = cursor.fetchall()
    conn.close()

    if results:
        df = pd.DataFrame(results)

        # Step 1: Add filter option
        filter_option = st.radio(
            "Filter queries by status:",
            ("All", "Open", "Closed")
        )

        # Step 2: Apply filter
        if filter_option == "Open":
            df = df[df["Status"] == "Open"]
        elif filter_option == "Closed":
            df = df[df["Status"] == "Closed"]

        # Step 3: Display filtered table
        if filter_option == "Closed":
            st.dataframe(
                df[["Query_ID", "Heading", "Description", "Open_Date", "Closed_Date", "Status", "Closed_By"]],
                use_container_width=True
            )
        else:
            st.dataframe(
                df[["Query_ID", "Heading", "Description", "Open_Date", "Closed_Date", "Status"]],
                use_container_width=True
            )
    else:
        st.info("No queries found.")
        # Show empty table with headers for clarity
        empty_df = pd.DataFrame(columns=["Query_ID", "Heading", "Description", "Open_Date", "Closed_Date", "Status", "Closed_By"])
        st.dataframe(empty_df, use_container_width=True)