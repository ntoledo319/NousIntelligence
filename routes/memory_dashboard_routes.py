"""
Memory Dashboard Routes

This module provides routes for the memory dashboard UI, displaying
the user's accumulated conversation history and memory data.

@module routes.memory_dashboard_routes
@description User memory dashboard routes
"""

import logging
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from services.memory_service import get_memory_service

logger = logging.getLogger(__name__)

# Create blueprint
memory_dashboard_bp = Blueprint('memory_dashboard', __name__, url_prefix='/memory')

@memory_dashboard_bp.route('/', methods=['GET'])
@login_required
def memory_dashboard():
    """
    Display the memory dashboard with user memory data

    Returns:
        Rendered memory dashboard template
    """
    try:
        memory_service = get_memory_service()

        # Ensure memory is initialized for the user
        memory_service.initialize_memory_for_user(current_user.id)

        # Render the dashboard
        return render_template('memory_dashboard.html')
    except Exception as e:
        logger.error(f"Error displaying memory dashboard: {str(e)}")
        flash("An error occurred while loading your memory dashboard", "danger")
        return redirect(url_for('dashboard.dashboard'))

def register_memory_dashboard_routes(app):
    """Register memory dashboard routes with the Flask app"""
    app.register_blueprint(memory_dashboard_bp)
    logger.info("Memory dashboard routes registered")