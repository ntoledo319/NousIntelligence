"""
NOUS Personal Assistant - Main Entry Point

This file serves as the entry point for the NOUS Personal Assistant application.
It imports and runs the cleaned version of the application.
"""

# Import the application from the clean version
from app_clean import app

# Run the application if this file is executed directly
if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    print(f"\n* NOUS Application running on http://0.0.0.0:{port}")
    print(f"* Public URL: https://{os.environ.get('REPL_SLUG', 'your-app')}.replit.app\n")
    app.run(host='0.0.0.0', port=port)