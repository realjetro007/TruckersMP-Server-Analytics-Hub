import time
import subprocess
import os

INTERVAL = 5

print("==================================================")
print("TRUCKERSMP LIVE DATA SCHEDULER")
print(f"Syncing live API statistics every {INTERVAL} seconds...")
print("Close application with CTRL+C")
print("==================================================")

try:
    while True:
        result = subprocess.run(["python", "tracker.py"], capture_output=True, text=True)
        print(result.stdout.strip())
        time.sleep(INTERVAL)
except KeyboardInterrupt:
    print("Exiting...")