import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime
import time

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="your username",         
        password="your password", 
        database="your database name"
    )


def support_dashboard():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch all queries including Closed_By
        cursor.execute("""
            SELECT 
                id AS Query_ID,
                name AS Name,
                email AS Email,
                mobile AS Mobile,
                heading AS Heading,
                description AS Description,
                query_created_time AS Created_At,
                status AS Status,
                query_closed_time AS Closed_At,
                closed_by AS Closed_By
            FROM queries
            ORDER BY query_created_time DESC
        """)
        results = cursor.fetchall()

        if results:
            df = pd.DataFrame(results)

            # Filter option
            filter_option = st.radio(
                "Filter queries by status:",
                ("All", "Open", "Closed"),
                horizontal=True
            )

            if filter_option == "Open":
                df = df[df["Status"] == "Open"]
            elif filter_option == "Closed":
                df = df[df["Status"] == "Closed"]

            # Display filtered queries
            st.subheader(f"{filter_option} Queries")

            if filter_option == "Closed":
                st.dataframe(
                    df[["Query_ID", "Heading", "Description", "Created_At", "Closed_At", "Status", "Closed_By"]],
                    use_container_width=True
                )
            else:
                  st.dataframe(df, use_container_width=True)
                # st.dataframe(
                #     df[["Query_ID", "Heading", "Description", "Created_At", "Closed_At", "Status"]],
                #     use_container_width=True)

            # --- Close query section (only if Open queries are visible) ---
            if filter_option == "Open" and not df.empty:
                st.markdown("---")
                st.subheader("🔒 Close an Open Query")

                query_ids = df['Query_ID'].tolist()
                selected_id = st.selectbox("Select Query ID to close", query_ids)

                if st.button("Mark as Closed"):
                    close_cursor = conn.cursor()
                    close_cursor.execute("""
                        UPDATE queries
                        SET status = 'Closed',
                            query_closed_time = %s,
                            closed_by = %s
                        WHERE id = %s
                    """, (datetime.now(), st.session_state['username'], selected_id))
                    conn.commit()
                    st.success(f"✅ Query ID {selected_id} marked as Closed by {st.session_state['username']}.")
                    time.sleep(2)
                    st.rerun()
            elif filter_option == "Open" and df.empty:
                st.info("No open queries to close.")


        else:
            st.info("No queries found.")

        conn.close()

    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")


def get_query_status_counts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM queries GROUP BY status")
    data = cursor.fetchall()
    conn.close()
    return pd.DataFrame(data, columns=["Status", "Count"])

def query_summary_page():
    st.subheader("📊 Query Summary")

    df = get_query_status_counts()

    if not df.empty:
        total_queries = df["Count"].sum()
        open_queries = df.loc[df["Status"] == "Open", "Count"].sum()
        closed_queries = df.loc[df["Status"] == "Closed", "Count"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Total Queries", total_queries)
        col2.metric("✅ Closed Queries", closed_queries)
        col3.metric("🔴 Open Queries", open_queries)
    else:
        st.info("No queries found.")


import altair as alt

def support_team_page():
    st.subheader("👥 Support Team Performance")

    # --- Query 1: Overall counts ---
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) FROM queries GROUP BY status")
    status_data = cursor.fetchall()

    # --- Query 2: Closed queries by support person ---
    cursor.execute("""
        SELECT closed_by AS support_person, COUNT(*) AS closed_count
        FROM queries
        WHERE status = 'Closed'
        GROUP BY closed_by
    """)
    closed_data = cursor.fetchall()
    conn.close()

    # --- Convert to DataFrames ---
    df_status = pd.DataFrame(status_data, columns=["Status", "Count"])
    df_closed = pd.DataFrame(closed_data, columns=["Support Person", "Closed Queries"])

    # --- Metrics ---
    if not df_status.empty:
        total_queries = df_status["Count"].sum()
        open_queries = df_status.loc[df_status["Status"] == "Open", "Count"].sum()
        closed_queries = df_status.loc[df_status["Status"] == "Closed", "Count"].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Total Queries", int(total_queries))
        col2.metric("✅ Closed Queries", int(closed_queries))
        col3.metric("🔴 Open Queries", int(open_queries))
    else:
        st.info("No queries found.")

    # --- Visualization: Closed queries per support person ---
    if not df_closed.empty:
        chart = alt.Chart(df_closed).mark_bar().encode(
            x="Closed Queries",
            y=alt.Y("Support Person", sort="-x"),
            color="Support Person",
            tooltip=["Support Person", "Closed Queries"]
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("No closed queries found for support team.")

