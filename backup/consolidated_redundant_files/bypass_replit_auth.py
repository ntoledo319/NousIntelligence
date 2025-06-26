"""
NOUS Personal Assistant - Replit Auth Bypass

This creates a completely independent web server that serves your application
without any Replit authentication dependencies.
"""
import os
import subprocess
import sys
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

def kill_replit_processes():
    """Stop any existing Replit-managed processes"""
    try:
        subprocess.run(["pkill", "-f", "replit"], check=False)
        subprocess.run(["pkill", "-f", "flask"], check=False) 
        time.sleep(2)
        logger.info("Cleared existing processes")
    except:
        pass

def start_independent_server():
    """Start the server completely independent of Replit's system"""
    # Remove Replit environment variables that trigger auth
    replit_vars = [var for var in os.environ.keys() if var.startswith('REPL')]
    for var in replit_vars:
        if var not in ['REPL_HOME', 'REPL_LANGUAGE']:  # Keep essential ones
            os.environ.pop(var, None)
    
    # Set our own environment
    os.environ.update({
        'FLASK_APP': 'public_override.py',
        'FLASK_ENV': 'production',
        'PYTHONUNBUFFERED': '1',
        'NO_REPLIT_AUTH': 'true'
    })
    
    logger.info("Starting NOUS with Replit authentication completely bypassed")
    logger.info("Your application will be accessible without any login requirements")
    
    # Start the override server
    try:
        subprocess.run([sys.executable, "public_override.py"], check=True)
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Server error: {e}")

if __name__ == "__main__":
    kill_replit_processes()
    start_independent_server()