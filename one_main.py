"""
NOUS Personal Assistant - Main Entry Point
This module imports and runs the consolidated public application
"""

from one_app import app

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host="0.0.0.0", port=port, debug=False)