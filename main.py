"""
NOUS Personal Assistant - Unified Port Configuration
Google-Only Authentication with Professional Chat Interface
"""
from app import app
from config import PORT, HOST, DEBUG

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)