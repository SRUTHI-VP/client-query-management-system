import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import time

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="enter your username",         
        password="enter your password", 
        database="enter your database name"
    )

def support_dashboard():
    st.subheader(" All Client Queries")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        
        cursor.execute("""
            SELECT 
                id AS Query_ID,
                name As Name,
                email AS Email,
                mobile AS Mobile,
                heading AS Heading,
                description AS Description,
                query_created_time AS Created_At,
                status AS Status,
                query_closed_time AS Closed_At
            FROM queries
            ORDER BY query_created_time DESC
        """)
        results = cursor.fetchall()

        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            
            st.markdown("---")
            st.subheader(" Close an Open Query")
            open_queries = df[df['Status'] == 'Open']

            if not open_queries.empty:
                query_ids = open_queries['Query_ID'].tolist()
                selected_id = st.selectbox("Select Query ID to close", query_ids)

                if st.button("Mark as Closed"):
                    close_cursor = conn.cursor()
                    close_cursor.execute("""
                        UPDATE queries
                        SET status = 'Closed',
                            query_closed_time = %s
                        WHERE id = %s
                    """, (datetime.now(), selected_id))
                    conn.commit()
                    st.success(f"Query ID {selected_id} marked as Closed.")
                    time.sleep(2)
                    st.rerun()
            else:
                st.info("No open queries to close.")
        else:
            st.info("No queries found.")

        conn.close()

    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")