"""
Routes for Recovery Insights and Progress Tracking
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from utils.aa_helper import get_recovery_stats
from utils.ai_helper import generate_ai_text

recovery_bp = Blueprint('recovery_routes', __name__, url_prefix='/recovery')

@recovery_bp.route('/insights')
@login_required
def insights_dashboard():
    """Renders the main recovery insights dashboard."""
    user_id = current_user.id
    
    # Get recovery stats
    stats = get_recovery_stats(user_id)
    
    # This is a placeholder for more advanced AI insights.
    # A real implementation would fetch journal entries and other data
    # to generate more personalized insights.
    insight_prompt = f"Based on the following recovery stats, provide a brief, encouraging insight for the user: {stats}"
    ai_insight = generate_ai_text(insight_prompt)

    return render_template('recovery_insights.html', stats=stats, insight=ai_insight) 