"""
NOUS Personal Assistant - Replit App Entry Point

This file is specifically designed to work with Replit's runtime environment
and keep your application running continuously.
"""

# Simply import and run the public version of the app
from nous_public import app

# This will be used when Replit looks for the app object
if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    print(f"\n* NOUS Personal Assistant running on http://0.0.0.0:{port}")
    print(f"* Public URL: https://{os.environ.get('REPL_SLUG', 'your-app')}.replit.app\n")
    app.run(host='0.0.0.0', port=port)