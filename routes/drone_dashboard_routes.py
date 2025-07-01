"""
Drone Swarm Dashboard Routes
Web interface routes for the drone swarm management dashboard
"""

import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash

logger = logging.getLogger(__name__)

# Create blueprint
drone_dashboard_bp = Blueprint('drone_dashboard', __name__)

@drone_dashboard_bp.route('/drone-swarm-dashboard')
def drone_swarm_dashboard():
    """Display the drone swarm management dashboard"""
    try:
        # Render the dashboard template
        return render_template(
            'drone_swarm_dashboard.html',
            title='SEED Drone Swarm Dashboard',
            page_description='Autonomous System Management & Optimization'
        )
        
    except Exception as e:
        logger.error(f"Dashboard route error: {e}")
        flash('Error loading drone swarm dashboard', 'error')
        return redirect(url_for('main.index'))

@drone_dashboard_bp.route('/drone-swarm')
def drone_swarm_redirect():
    """Redirect to the main dashboard"""
    return redirect(url_for('drone_dashboard.drone_swarm_dashboard'))