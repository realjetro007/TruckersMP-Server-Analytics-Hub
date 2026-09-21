import sqlite3
import time
import requests

# 1. Connects to or creates a local SQL database
DB_NAME = "truckersmp_stats.db"
conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

#Creates a table to log servers available
cursor.execute("""
    CREATE TABLE IF NOT EXISTS servers (
        server_id INTEGER PRIMARY KEY,
        server_name TEXT,
        max_players INTEGER
    )
""")

#Creates a table if it does not exist to hold changing information
cursor.execute("""
    CREATE TABLE IF NOT EXISTS traffic_logs (
        timestamp INTEGER,
        server_id INTEGER,
        players_online INTEGER,
        queue_count INTEGER,
        FOREIGN KEY (server_id) REFERENCES servers(server_id)
        UNIQUE(timestamp, server_id) 
    )
""")
conn.commit()


def fetch_and_store_data():
    url = "https://api.truckersmp.com/v2/servers"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()

            # The API returns a list of individual multiplayer servers
            servers = data.get("response", [])
            current_time = int(time.time())

            for server in servers:
                # Selects only ETS2 Servers
                if server.get("game") == "ETS2":
                    s_id = server.get("id")
                    cursor.execute(
                        "REPLACE INTO servers VALUES (?, ?, ?)",
                        (s_id, server.get("name"), server.get("maxplayers"))
                    )

                    cursor.execute(
                        "INSERT OR IGNORE INTO traffic_logs VALUES (?, ?, ?, ?)",
                        (current_time, s_id, server.get("players"), server.get("queue"))
                    )
            conn.commit()
            print(f"[{time.strftime('%X')}] Successfully logged traffic snapshot to SQL.")
        else:
            print(f"API Error: Status code {response.status_code}")
    except Exception as e:
        print(f"Network error handling request: {e}")

fetch_and_store_data()


conn.close()
