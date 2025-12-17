"""
CLI Entrypoint for NOUS Personal Assistant
"""
from app import app
import os

def main():
    """CLI Entrypoint to run the Flask application."""
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host=host, port=port, debug=debug)

if __name__ == '__main__':
    main()
