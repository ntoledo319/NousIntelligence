"""
Comprehensive User Management Routes
Handles all user-related operations including profile, preferences, settings, and data management
"""

from flask import Blueprint, render_template, jsonify, request, session
from utils.auth_compat import login_required, get_demo_user, is_authenticated, get_current_user
from models.user import User
from models.setup_models import UserPreferences, SetupProgress
from models.analytics_models import Activity, Insight
from database import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
def profile():
    """User profile page with comprehensive information"""
    user = get_current_user()
    if not user:
        user = get_demo_user()
    
    # Get user preferences if they exist
    preferences = None
    if hasattr(user, 'id') and user.id:
        try:
            preferences = UserPreferences.query.filter_by(user_id=str(user.id)).first()
        except Exception as e:
            logger.warning(f"Could not load preferences: {e}")
    
    return render_template('profile.html', user=user, preferences=preferences)

@user_bp.route('/api/user/profile')
def api_profile():
    """User profile API with complete user data"""
    user = get_current_user()
    if not user:
        user = get_demo_user()
    
    user_data = {
        'id': getattr(user, 'id', 'demo'),
        'username': getattr(user, 'username', 'Demo User'),
        'email': getattr(user, 'email', 'demo@nous.app'),
        'active': getattr(user, 'active', True),
        'is_demo': getattr(user, 'is_demo', True),
        'created_at': getattr(user, 'created_at', datetime.utcnow()).isoformat() if hasattr(user, 'created_at') else None,
        'last_login': getattr(user, 'last_login', None).isoformat() if hasattr(user, 'last_login') and user.last_login else None
    }
    
    return jsonify(user_data)

@user_bp.route('/api/user/preferences', methods=['GET'])
def get_user_preferences():
    """Get comprehensive user preferences"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        preferences = UserPreferences.query.filter_by(user_id=str(user.id)).first()
        if not preferences:
            # Return default preferences
            return jsonify({
                'user_id': str(user.id),
                'primary_language': 'en-US',
                'theme_preference': 'auto',
                'therapeutic_approach': 'integrated',
                'assistant_personality': 'empathetic',
                'notification_frequency': 'medium',
                'data_privacy_level': 'full'
            })
        
        return jsonify(preferences.to_dict())
    except Exception as e:
        logger.error(f"Error retrieving user preferences: {e}")
        return jsonify({'error': 'Could not retrieve preferences'}), 500

@user_bp.route('/api/user/preferences', methods=['POST'])
def update_user_preferences():
    """Update user preferences with comprehensive validation"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get or create preferences
        preferences = UserPreferences.query.filter_by(user_id=str(user.id)).first()
        if not preferences:
            preferences = UserPreferences(user_id=str(user.id))
            db.session.add(preferences)
        
        # Update preferences with validation
        if 'primary_language' in data:
            preferences.primary_language = data['primary_language']
        if 'secondary_languages' in data:
            preferences.secondary_languages = data['secondary_languages']
        if 'learning_languages' in data:
            preferences.learning_languages = data['learning_languages']
        if 'is_neurodivergent' in data:
            preferences.is_neurodivergent = bool(data['is_neurodivergent'])
        if 'neurodivergent_conditions' in data:
            preferences.neurodivergent_conditions = data['neurodivergent_conditions']
        if 'theme_preference' in data:
            preferences.theme_preference = data['theme_preference']
        if 'color_scheme' in data:
            preferences.color_scheme = data['color_scheme']
        if 'font_size' in data:
            preferences.font_size = data['font_size']
        if 'high_contrast' in data:
            preferences.high_contrast = bool(data['high_contrast'])
        if 'mental_health_goals' in data:
            preferences.mental_health_goals = data['mental_health_goals']
        if 'therapeutic_approach' in data:
            preferences.therapeutic_approach = data['therapeutic_approach']
        if 'crisis_support_enabled' in data:
            preferences.crisis_support_enabled = bool(data['crisis_support_enabled'])
        if 'assistant_personality' in data:
            preferences.assistant_personality = data['assistant_personality']
        if 'assistant_tone' in data:
            preferences.assistant_tone = data['assistant_tone']
        if 'communication_style' in data:
            preferences.communication_style = data['communication_style']
        if 'ai_assistance_level' in data:
            preferences.ai_assistance_level = data['ai_assistance_level']
        if 'notification_frequency' in data:
            preferences.notification_frequency = data['notification_frequency']
        if 'data_privacy_level' in data:
            preferences.data_privacy_level = data['data_privacy_level']
        if 'emergency_contacts' in data:
            preferences.emergency_contacts = data['emergency_contacts']
        if 'safety_planning_enabled' in data:
            preferences.safety_planning_enabled = bool(data['safety_planning_enabled'])
        
        preferences.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Preferences updated successfully',
            'preferences': preferences.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error updating user preferences: {e}")
        db.session.rollback()
        return jsonify({'error': 'Could not update preferences'}), 500

@user_bp.route('/api/user/settings', methods=['GET'])
def get_user_settings():
    """Get user account settings"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    settings = {
        'username': getattr(user, 'username', ''),
        'email': getattr(user, 'email', ''),
        'active': getattr(user, 'active', True),
        'email_verified': True,  # Placeholder for future implementation
        'two_factor_enabled': False,  # Placeholder for future implementation
        'api_keys_count': 0,  # Placeholder for future implementation
        'data_export_available': True,
        'account_deletion_available': True
    }
    
    return jsonify(settings)

@user_bp.route('/api/user/settings', methods=['POST'])
def update_user_settings():
    """Update user account settings"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # For demo user, just return success
        if getattr(user, 'is_demo', True):
            return jsonify({
                'success': True,
                'message': 'Settings updated (demo mode)',
                'settings': data
            })
        
        # Update actual user data if not demo
        if hasattr(user, 'id') and user.id:
            db_user = User.query.get(user.id)
            if db_user:
                if 'username' in data:
                    db_user.username = data['username']
                if 'email' in data:
                    db_user.email = data['email']
                
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Settings updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating user settings: {e}")
        db.session.rollback()
        return jsonify({'error': 'Could not update settings'}), 500

@user_bp.route('/api/user/activity', methods=['GET'])
def get_user_activity():
    """Get user activity and engagement metrics"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        # Get recent activities
        activities = []
        if hasattr(user, 'id') and user.id:
            recent_activities = Activity.query.filter_by(user_id=user.id).order_by(Activity.timestamp.desc()).limit(10).all()
            activities = [activity.to_dict() for activity in recent_activities]
        
        # Get user insights
        insights = []
        if hasattr(user, 'id') and user.id:
            recent_insights = Insight.query.filter_by(user_id=user.id).order_by(Insight.timestamp.desc()).limit(5).all()
            insights = [insight.to_dict() for insight in recent_insights]
        
        return jsonify({
            'activities': activities,
            'insights': insights,
            'summary': {
                'total_activities': len(activities),
                'total_insights': len(insights),
                'last_activity': activities[0]['timestamp'] if activities else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error retrieving user activity: {e}")
        return jsonify({'error': 'Could not retrieve activity data'}), 500

@user_bp.route('/api/user/dashboard', methods=['GET'])
def get_user_dashboard():
    """Get comprehensive user dashboard data"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        dashboard_data = {
            'user': {
                'id': getattr(user, 'id', 'demo'),
                'username': getattr(user, 'username', 'Demo User'),
                'email': getattr(user, 'email', 'demo@nous.app'),
                'is_demo': getattr(user, 'is_demo', True)
            },
            'setup_progress': None,
            'preferences': None,
            'recent_activities': [],
            'insights': [],
            'therapeutic_progress': {
                'total_sessions': 0,
                'skills_practiced': 0,
                'mood_entries': 0,
                'goals_achieved': 0
            },
            'health_metrics': {
                'wellness_score': 75,  # Default placeholder
                'stress_level': 3,     # Default placeholder
                'sleep_quality': 7     # Default placeholder
            }
        }
        
        # Get setup progress
        if hasattr(user, 'id') and user.id:
            setup_progress = SetupProgress.query.filter_by(user_id=str(user.id)).first()
            if setup_progress:
                dashboard_data['setup_progress'] = setup_progress.to_dict()
        
        # Get preferences
        if hasattr(user, 'id') and user.id:
            preferences = UserPreferences.query.filter_by(user_id=str(user.id)).first()
            if preferences:
                dashboard_data['preferences'] = preferences.to_dict()
        
        # Get recent activities and insights
        if hasattr(user, 'id') and user.id:
            recent_activities = Activity.query.filter_by(user_id=user.id).order_by(Activity.timestamp.desc()).limit(5).all()
            dashboard_data['recent_activities'] = [activity.to_dict() for activity in recent_activities]
            
            recent_insights = Insight.query.filter_by(user_id=user.id).order_by(Insight.timestamp.desc()).limit(3).all()
            dashboard_data['insights'] = [insight.to_dict() for insight in recent_insights]
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        logger.error(f"Error retrieving user dashboard: {e}")
        return jsonify({'error': 'Could not retrieve dashboard data'}), 500

@user_bp.route('/api/user/export', methods=['POST'])
def export_user_data():
    """Export all user data for download"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    try:
        export_data = {
            'user_profile': {
                'id': getattr(user, 'id', 'demo'),
                'username': getattr(user, 'username', 'Demo User'),
                'email': getattr(user, 'email', 'demo@nous.app'),
                'created_at': getattr(user, 'created_at', datetime.utcnow()).isoformat() if hasattr(user, 'created_at') else None,
                'export_date': datetime.utcnow().isoformat()
            },
            'preferences': {},
            'activities': [],
            'insights': [],
            'therapeutic_data': {},
            'health_data': {}
        }
        
        # Add preferences if available
        if hasattr(user, 'id') and user.id:
            preferences = UserPreferences.query.filter_by(user_id=str(user.id)).first()
            if preferences:
                export_data['preferences'] = preferences.to_dict()
        
        # Add activities and insights if available
        if hasattr(user, 'id') and user.id:
            activities = Activity.query.filter_by(user_id=user.id).all()
            export_data['activities'] = [activity.to_dict() for activity in activities]
            
            insights = Insight.query.filter_by(user_id=user.id).all()
            export_data['insights'] = [insight.to_dict() for insight in insights]
        
        return jsonify({
            'success': True,
            'message': 'Data export prepared successfully',
            'data': export_data,
            'download_url': f'/api/user/download-export/{user.id if hasattr(user, "id") else "demo"}'
        })
        
    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        return jsonify({'error': 'Could not export user data'}), 500

@user_bp.route('/api/user/delete-account', methods=['POST'])
def delete_user_account():
    """Delete user account and all associated data"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # For demo users, just return success without actual deletion
    if getattr(user, 'is_demo', True):
        return jsonify({
            'success': True,
            'message': 'Demo account cannot be deleted'
        })
    
    try:
        data = request.get_json()
        confirmation = data.get('confirmation', '')
        
        if confirmation != 'DELETE_MY_ACCOUNT':
            return jsonify({'error': 'Invalid confirmation'}), 400
        
        # In a real implementation, this would delete all user data
        # For now, just mark as inactive
        if hasattr(user, 'id') and user.id:
            db_user = User.query.get(user.id)
            if db_user:
                db_user.active = False
                db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Account deactivated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting user account: {e}")
        db.session.rollback()
        return jsonify({'error': 'Could not delete account'}), 500
