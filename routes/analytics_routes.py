"""
Analytics Routes

This module provides API endpoints for analytics and insights functionality.
"""

from flask import Blueprint, request, jsonify, session, redirect, render_template
from datetime import datetime, timedelta, date
import logging

# Create blueprint
analytics_bp = Blueprint('analytics', __name__, url_prefix='/api/v1/analytics')

logger = logging.getLogger(__name__)

def is_authenticated():
    """Check if user is authenticated"""
    return 'user' in session

@analytics_bp.route('/dashboard', methods=['GET'])
def get_analytics_dashboard():
    """Get comprehensive analytics dashboard"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.analytics_service import AnalyticsService
        
        user_id = session['user']['id']
        days = request.args.get('days', 30, type=int)
        
        analytics_service = AnalyticsService(db)
        dashboard_data = analytics_service.get_user_analytics_dashboard(user_id, days)
        
        return jsonify({
            'success': True,
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Error getting analytics dashboard: {str(e)}")
        return jsonify({'error': 'Failed to get analytics dashboard'}), 500

@analytics_bp.route('/activity', methods=['POST'])
def track_activity():
    """Track user activity"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.analytics_service import AnalyticsService
        
        user_id = session['user']['id']
        data = request.get_json()
        
        activity_type = data.get('activity_type')
        activity_category = data.get('activity_category')
        activity_data = data.get('activity_data', {})
        duration_seconds = data.get('duration_seconds', 0)
        session_id = data.get('session_id')
        
        if not activity_type:
            return jsonify({'error': 'Activity type is required'}), 400
        
        analytics_service = AnalyticsService(db)
        result = analytics_service.track_activity(
            user_id, activity_type, activity_category, 
            activity_data, duration_seconds, session_id
        )
        
        if result:
            return jsonify({
                'success': True,
                'data': result
            })
        else:
            return jsonify({'error': 'Failed to track activity'}), 500
            
    except Exception as e:
        logger.error(f"Error tracking activity: {str(e)}")
        return jsonify({'error': 'Failed to track activity'}), 500

@analytics_bp.route('/goals', methods=['GET'])
def get_goals():
    """Get user goals"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from models.analytics_models import UserGoal
        from sqlalchemy import and_
        
        user_id = session['user']['id']
        active_only = request.args.get('active_only', 'true').lower() == 'true'
        
        query = db.session.query(UserGoal).filter(
            UserGoal.user_id == user_id
        )
        
        if active_only:
            query = query.filter(UserGoal.is_active == True)
        
        goals = query.order_by(UserGoal.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [goal.to_dict() for goal in goals]
        })
        
    except Exception as e:
        logger.error(f"Error getting goals: {str(e)}")
        return jsonify({'error': 'Failed to get goals'}), 500

@analytics_bp.route('/goals', methods=['POST'])
def create_goal():
    """Create a new goal"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from models.analytics_models import UserGoal
        
        user_id = session['user']['id']
        data = request.get_json()
        
        required_fields = ['goal_type', 'title', 'target_value']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        goal = UserGoal(
            user_id=user_id,
            goal_type=data['goal_type'],
            title=data['title'],
            description=data.get('description', ''),
            target_value=data['target_value'],
            unit=data.get('unit', ''),
            target_date=datetime.fromisoformat(data['target_date']).date() if data.get('target_date') else None
        )
        
        db.session.add(goal)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': goal.to_dict(),
            'message': 'Goal created successfully'
        })
        
    except Exception as e:
        logger.error(f"Error creating goal: {str(e)}")
        return jsonify({'error': 'Failed to create goal'}), 500

@analytics_bp.route('/dashboard-view', methods=['GET'])
def analytics_dashboard_view():
    """Render analytics dashboard page"""
    if not is_authenticated():
        return redirect('/login')
    
    return render_template('analytics_dashboard.html', user=session['user'])
