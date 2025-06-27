"""
Dashboard Routes for NOUS Personal Assistant

This module defines dashboard routes for the NOUS application.
"""

from flask import Blueprint, render_template, redirect, request, g
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """Dashboard view"""
    try:
        logger.info("Rendering dashboard")
        # Render the dashboard template
        return render_template('dashboard.html')
    except Exception as e:
        logger.error(f"Error rendering dashboard: {str(e)}")
        logger.exception("Full traceback for dashboard error:")
        return redirect('/')