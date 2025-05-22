"""
NOUS Personal Assistant - Run Script

This script starts the NOUS app with Gunicorn for improved reliability.
"""

import os
import sys
import subprocess
import time

print("=== NOUS Personal Assistant ===")
print("Starting application...")

# Kill any existing processes
try:
    subprocess.run(["pkill", "-f", "python"], stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-f", "gunicorn"], stderr=subprocess.DEVNULL)
except:
    pass

# Make sure port is available
try:
    subprocess.run(["fuser", "-k", "8080/tcp"], stderr=subprocess.DEVNULL)
except:
    pass

# Start with gunicorn
try:
    print("\nStarting NOUS with Gunicorn...")
    subprocess.Popen(["python", "-m", "gunicorn", "replit_nous:app", 
                     "-b", "0.0.0.0:8080", "--log-level", "info"])
    print("NOUS is running!")
    print("Visit your Replit URL to access the application")
    
    # Keep script running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nShutting down...")
    sys.exit(0)
except Exception as e:
    print(f"Error: {str(e)}")
    print("Falling back to Flask development server...")
    
    try:
        # Fall back to Flask development server
        import replit_nous
        port = int(os.environ.get('PORT', 8080))
        replit_nous.app.run(host="0.0.0.0", port=port)
    except Exception as e2:
        print(f"Failed to start Flask server: {str(e2)}")
        sys.exit(1)