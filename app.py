import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title = "TruckersMP Analytics Hub",
    layout = "wide"
)


st.title("TruckersMP Live Server Analytics Hub")
st.markdown("---")

DB_NAME = "truckersmp_stats.db"

query = """
    SELECT 
        t.timestamp,
        s.server_name,
        t.players_online,
        t.queue_count,
        s.max_players
    FROM traffic_logs t
    JOIN servers s ON t.server_id = s.server_id
"""

try:
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(query, conn)
    conn.close()

    if not df.empty:
        #Converts unix time into regular time
        df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")

        st.sidebar.header("Filter Settings")
        server_list = sorted(df["server_name"].unique())
        selected_server = st.sidebar.selectbox("Choose Server to Analyze", server_list)

        filtered_df = df[df["server_name"] == selected_server].sort_values("timestamp")

        latest_record = filtered_df.iloc[-1]
        players = int(latest_record["players_online"])
        max_capacity = int(latest_record["max_players"])
        queue = int(latest_record["queue_count"])

        saturation_pct = (players / max_capacity) * 100

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Active Drivers Online", f"{players:,}")
        col2.metric("Queue Wait Line", f"{queue:,}")
        col3.metric("Total Server Limit", f"{max_capacity:,}")
        col4.metric("Server Saturation", f"{saturation_pct:.1f}%")

        if saturation_pct >= 90.0:
            st.error(f"WARNING: {selected_server} is experiences high congestion Expect delays.")
        elif saturation_pct >= 60.0:
            st.warning(f"NOTICE: {selected_server} is highly populated. Moderate traffic density expected.")
        else:
            st.success(f"{selected_server} has a low player count. Roads should be clear.")

        st.markdown("---")

        st.subheader(f"Traffic Congestion Trends: {selected_server}")
        st.line_chart(data=filtered_df, x="datetime", y="players_online")

    else:
        st.warning("The database file exists, but it is currently empty. Please run scheduler.py for a few minutes to log data points.")

except Exception as e:
    st.error(f"Frontend Pipeline Error: {e}")
    st.info("Tip: Make sure you run your scheduler.py script first to initialize and generate the truckersmp_stats.db file.")