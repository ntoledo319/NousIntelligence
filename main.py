"""
NOUS Personal Assistant - Entry Point

This module serves as the entry point for the NOUS application.
It imports and runs the public application to ensure it's 
accessible without requiring login.
"""
from public_app import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)