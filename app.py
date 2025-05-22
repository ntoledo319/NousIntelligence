"""
NOUS Personal Assistant - Backward Compatibility Layer

This file provides backward compatibility with existing references
to the app module, redirecting to the unified application entry point.
"""

# Import the Flask app instance from our main entry point
from main import app

# This file now simply re-exports the app object

# When run directly, execute the main module
if __name__ == "__main__":
    import main