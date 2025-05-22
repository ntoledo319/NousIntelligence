"""
NOUS Personal Assistant - App Launcher

This script helps solve routing issues by ensuring the app launches properly.
"""

import os
import sys
import time
import subprocess
import signal

def main():
    print("\n=== NOUS Personal Assistant Launcher ===")
    print("Preparing to start application...")
    
    # Kill any existing processes that might conflict
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            if proc.info['name'] == 'python' or proc.info['name'] == 'python3':
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if ('main.py' in cmdline or 'app.py' in cmdline or 
                    'app_direct.py' in cmdline) and proc.pid != os.getpid():
                    print(f"Stopping existing process: {proc.pid}")
                    try:
                        os.kill(proc.pid, signal.SIGTERM)
                        time.sleep(0.5)
                    except:
                        pass
    except ImportError:
        # If psutil is not available, try using system commands
        try:
            os.system("pkill -f 'python main.py' 2>/dev/null || true")
            os.system("pkill -f 'python app.py' 2>/dev/null || true")
            os.system("pkill -f 'python app_direct.py' 2>/dev/null || true")
        except:
            print("Unable to check for existing processes")
    
    # Create a simplified version of the app if it doesn't exist
    if not os.path.exists('nous_app.py'):
        print("Creating simplified app...")
        with open('nous_app.py', 'w') as f:
            f.write("""
import os
import sys
import logging
from flask import Flask, render_template, jsonify, send_from_directory, request

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nous")

# Create app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "nous-key")

@app.route('/')
def index():
    \"\"\"Homepage with welcome message\"\"\"
    try:
        return render_template('minimal.html')
    except Exception as e:
        logger.error(f"Error rendering template: {str(e)}")
        return jsonify({
            "status": "online",
            "message": "NOUS Personal Assistant is running"
        })

@app.route('/health')
def health():
    \"\"\"Health check endpoint\"\"\"
    return jsonify({"status": "healthy", "version": "1.0.0"})

@app.route('/static/<path:path>')
def serve_static(path):
    \"\"\"Serve static files\"\"\"
    return send_from_directory('static', path)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8080))
    print(f"\\n* NOUS running on http://0.0.0.0:{port}\\n")
    app.run(host='0.0.0.0', port=port)
""")
    
    # Start the application
    print("Starting NOUS application...")
    
    # Try using a different port to avoid conflicts with Replit's default server
    os.environ['PORT'] = '5000'
    
    try:
        subprocess.run([sys.executable, 'nous_app.py'], check=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"\nError: {str(e)}")
        print("Trying alternative approach...")
        try:
            subprocess.run([sys.executable, 'app_direct.py'], check=True)
        except Exception as e2:
            print(f"Alternative approach failed: {str(e2)}")
            print("Please check your configuration")
            sys.exit(1)

if __name__ == "__main__":
    main()