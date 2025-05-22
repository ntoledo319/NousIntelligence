"""
NOUS Personal Assistant - Runner Script

This script ensures the app runs properly on Replit.
"""

import os
import sys
import subprocess
import signal
import time

def kill_existing_servers():
    """Kill any existing Python processes running on port 5000 or 8080"""
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'main.py' in cmdline or 'app.py' in cmdline:
                    if proc.pid != os.getpid():
                        print(f"Terminating existing Python process: {proc.pid}")
                        try:
                            os.kill(proc.pid, signal.SIGTERM)
                            time.sleep(0.5)
                        except:
                            pass
    except ImportError:
        # If psutil is not available, try a simpler approach
        try:
            # Check for Python processes running our app
            ps_output = subprocess.check_output(['ps', 'aux'], text=True)
            for line in ps_output.splitlines():
                if ('python' in line or 'python3' in line) and ('main.py' in line or 'app.py' in line):
                    try:
                        pid = int(line.split()[1])
                        if pid != os.getpid():
                            print(f"Terminating existing Python process: {pid}")
                            os.kill(pid, signal.SIGTERM)
                            time.sleep(0.5)
                    except:
                        pass
        except:
            print("Unable to check for existing processes")

def main():
    """Run the NOUS application with the right configuration"""
    # Clean up existing processes
    kill_existing_servers()
    
    # Configure the application port
    os.environ['PORT'] = '5000'
    
    print("\n=== NOUS Personal Assistant ===")
    print(f"Starting application on port 5000...")
    
    # Import and run the app
    try:
        # Method 1: Run as module
        from app import app
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting with method 1: {e}")
        # Method 2: Run as subprocess
        try:
            subprocess.run([sys.executable, "main.py"], check=True)
        except Exception as e:
            print(f"Error starting with method 2: {e}")
            print("Trying final fallback method...")
            try:
                # Method 3: Direct import from main
                import main
            except Exception as e:
                print(f"All startup methods failed: {e}")
                sys.exit(1)

if __name__ == "__main__":
    main()