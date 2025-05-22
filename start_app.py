"""
NOUS Personal Assistant - Application Starter

This script ensures the app runs on the correct port and with proper configuration.
"""

import os
import sys
import signal
import subprocess
import time

def main():
    # Kill any existing Flask processes to avoid port conflicts
    try:
        print("Checking for existing processes...")
        # Find Python processes that might be running our app
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        
        for line in result.stdout.splitlines():
            if "python" in line and "main.py" in line and not "start_app.py" in line:
                try:
                    pid = int(line.split()[1])
                    print(f"Stopping existing process: {pid}")
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(1)  # Give it time to shut down
                except Exception as e:
                    print(f"Error stopping process: {e}")
    except Exception as e:
        print(f"Error checking processes: {e}")

    # Set the port for Flask
    os.environ['PORT'] = '5000'
    
    print("\n* Starting NOUS Personal Assistant...")
    print(f"* App will be available at http://0.0.0.0:5000")
    print(f"* Public URL: https://{os.environ.get('REPL_SLUG', 'nous-assistant')}.replit.app\n")
    
    # Run the application with the updated configuration
    try:
        subprocess.run([sys.executable, "main.py"])
    except KeyboardInterrupt:
        print("\nShutting down application...")
    except Exception as e:
        print(f"Error running application: {e}")

if __name__ == "__main__":
    main()