"""
NOUS Personal Assistant - Port-Safe Runner
This script tries multiple ports until it finds one that works
"""
import os
import sys
import subprocess

# Try to find an available port
ports_to_try = [3000, 4000, 5000, 6000, 7000]

for port in ports_to_try:
    try:
        print(f"Attempting to start on port {port}...")
        # Set environment variable for Flask
        os.environ['PORT'] = str(port)
        # Start the Flask app as a subprocess
        process = subprocess.Popen([sys.executable, "new_app.py"])
        # Wait a moment to see if it starts successfully
        process.wait(timeout=5)
        # If we get here without an exception, the process started successfully
        print(f"Application started on port {port}")
        break
    except subprocess.TimeoutExpired:
        # This means the process is still running (which is good!)
        print(f"Success! Application running on port {port}")
        # Keep the main process running
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            sys.exit(0)
        break
    except Exception as e:
        print(f"Failed to start on port {port}: {e}")
        # Try the next port
        continue
else:
    print("Failed to start on any port. Please check if the application is already running.")