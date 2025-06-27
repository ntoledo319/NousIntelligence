"""
Notification Routes

This module provides API endpoints for notification management functionality.
"""

from flask import Blueprint, request, jsonify, session
import logging

# Create blueprint
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/v1/notifications')

logger = logging.getLogger(__name__)

def is_authenticated():
    """Check if user is authenticated"""
    return 'user' in session

@notifications_bp.route('/', methods=['GET'])
def get_notifications():
    """Get user notifications"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.notification_service import NotificationService
        
        user_id = session['user']['id']
        include_read = request.args.get('include_read', 'true').lower() == 'true'
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        notification_service = NotificationService(db)
        notifications_data = notification_service.get_user_notifications(
            user_id, include_read, limit, offset
        )
        
        return jsonify({
            'success': True,
            'data': notifications_data
        })
        
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        return jsonify({'error': 'Failed to get notifications'}), 500

@notifications_bp.route('/summary', methods=['GET'])
def get_notification_summary():
    """Get notification summary"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.notification_service import NotificationService
        
        user_id = session['user']['id']
        
        notification_service = NotificationService(db)
        summary = notification_service.get_notification_summary(user_id)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting notification summary: {str(e)}")
        return jsonify({'error': 'Failed to get summary'}), 500

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
def mark_as_read(notification_id):
    """Mark notification as read"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.notification_service import NotificationService
        
        user_id = session['user']['id']
        
        notification_service = NotificationService(db)
        success = notification_service.mark_as_read(user_id, notification_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification marked as read'
            })
        else:
            return jsonify({'error': 'Notification not found'}), 404
            
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        return jsonify({'error': 'Failed to mark as read'}), 500

@notifications_bp.route('/mark-all-read', methods=['POST'])
def mark_all_as_read():
    """Mark all notifications as read"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.notification_service import NotificationService
        
        user_id = session['user']['id']
        
        notification_service = NotificationService(db)
        count = notification_service.mark_all_as_read(user_id)
        
        return jsonify({
            'success': True,
            'message': f'Marked {count} notifications as read'
        })
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {str(e)}")
        return jsonify({'error': 'Failed to mark all as read'}), 500

@notifications_bp.route('/<int:notification_id>/dismiss', methods=['POST'])
def dismiss_notification(notification_id):
    """Dismiss notification"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.notification_service import NotificationService
        
        user_id = session['user']['id']
        
        notification_service = NotificationService(db)
        success = notification_service.dismiss_notification(user_id, notification_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Notification dismissed'
            })
        else:
            return jsonify({'error': 'Notification not found'}), 404
            
    except Exception as e:
        logger.error(f"Error dismissing notification: {str(e)}")
        return jsonify({'error': 'Failed to dismiss notification'}), 500

@notifications_bp.route('/', methods=['POST'])
def create_notification():
    """Create a new notification (for testing/admin purposes)"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.notification_service import NotificationService
        
        user_id = session['user']['id']
        data = request.get_json()
        
        required_fields = ['notification_type', 'title', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        notification_service = NotificationService(db)
        notification = notification_service.create_notification(
            user_id=user_id,
            notification_type=data['notification_type'],
            title=data['title'],
            message=data['message'],
            priority=data.get('priority', 'normal'),
            action_url=data.get('action_url'),
            metadata=data.get('metadata')
        )
        
        if notification:
            return jsonify({
                'success': True,
                'data': notification,
                'message': 'Notification created successfully'
            })
        else:
            return jsonify({'error': 'Failed to create notification'}), 500
            
    except Exception as e:
        logger.error(f"Error creating notification: {str(e)}")
        return jsonify({'error': 'Failed to create notification'}), 500

@notifications_bp.route('/cleanup', methods=['POST'])
def cleanup_notifications():
    """Clean up expired notifications"""
    if not is_authenticated():
        return jsonify({'error': 'Authentication required'}), 401
    
    try:
        from app import db
        from utils.notification_service import NotificationService
        
        user_id = session['user']['id']
        
        notification_service = NotificationService(db)
        count = notification_service.cleanup_expired_notifications(user_id)
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {count} expired notifications'
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up notifications: {str(e)}")
        return jsonify({'error': 'Failed to cleanup notifications'}), 500
