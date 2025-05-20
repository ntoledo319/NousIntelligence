"""
Main application module
======================

This module provides a unified interface to create and access the NOUS application.
The actual application factory is imported from app_factory.py.
"""

from app_factory import create_app, db

# Create an application instance for direct import
# This allows modules to import 'app' directly
app = create_app()

# Export key components for easy importing
__all__ = ['app', 'db']

# Add direct execution capability
if __name__ == '__main__':
    import os
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))