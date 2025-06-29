"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

API Routes Module

This module defines API routes for accessing application data.

@module routes.api
@description API routes for data access
"""

import logging
from flask import Blueprint, jsonify, request, session

from models import db, Task
# Chat processor functionality temporarily disabled during cleanup

# Create blueprint with version prefix
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
logger = logging.getLogger(__name__)

@api_bp.route('/status')
def api_status():
    """Return API status information"""
    return jsonify({
        'status': 'online',
        'version': '1.0.0',
        'message': 'NOUS API is operational'
    })

@api_bp.route('/user')
def get_user_info():
    """Get current user information"""
    return jsonify(session.get('user', {}).get('to_dict())

@api_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get user settings"""
    if not session.get('user', {}).get('settings:
        return jsonify({'error': 'Settings not found'}), 404

    return jsonify(session.get('user', {}).get('settings.to_dict())

@api_bp.route('/settings', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def update_settings():
    """Update user settings"""
    try:
        data = request.get_json()

        # Create settings if they don't exist
        if not session.get('user', {}).get('settings:
            from models import UserSettings
            settings = UserSettings(user_id=session.get('user', {}).get('id', 'demo_user'))
            db.session.add(settings)
            session.get('user', {}).get('settings = settings

        # Update valid fields
        valid_fields = [
            'theme', 'ai_name', 'ai_personality', 'preferred_language',
            'enable_voice_responses', 'conversation_difficulty'
        ]

        for field in valid_fields:
            if field in data:
                setattr(session.get('user', {}).get('settings, field, data[field])

        # Save changes
        db.session.commit()

        return jsonify(session.get('user', {}).get('settings.to_dict())
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get user tasks"""
    tasks = [task.to_dict() for task in session.get('user', {}).get('tasks]
    return jsonify(tasks)

@api_bp.route('/tasks', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def create_task():
    """Create a new task"""
    try:
        data = request.get_json()

        # Validate required fields
        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400

        # Create task
        task = Task(
            user_id=session.get('user', {}).get('id', 'demo_user'),
            title=data['title'],
            description=data.get('description'),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date')
        )

        # Save to database
        db.session.add(task)
        db.session.commit()

        return jsonify(task.to_dict()), 201
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def get_task(task_id):
    """Get a specific task"""
    task = Task.query.get(task_id)

    if not task or task.user_id != session.get('user', {}).get('id', 'demo_user'):
        return jsonify({'error': 'Task not found'}), 404

    return jsonify(task.to_dict())

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def update_task(task_id):
    """Update an existing task"""
    try:
        task = Task.query.get(task_id)

        if not task or task.user_id != session.get('user', {}).get('id', 'demo_user'):
            return jsonify({'error': 'Task not found'}), 404

        # Update task with request data
        data = request.get_json()

        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = data['due_date']
        if 'completed' in data:
            task.completed = data['completed']

        # Save changes
        db.session.commit()

        return jsonify(task.to_dict())
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def delete_task(task_id):
    """Delete a task"""
    try:
        task = Task.query.get(task_id)

        if not task or task.user_id != session.get('user', {}).get('id', 'demo_user'):
            return jsonify({'error': 'Task not found'}), 404

        # Delete the task
        db.session.delete(task)
        db.session.commit()

        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/chat', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def process_chat():
    """
    Process chat messages and return responses

    Request JSON format:
    {
        "message": "User's message text",
        "context": {optional context object}
    }

    Response JSON format:
    {
        "success": true/false,
        "response": {
            "text": "Assistant's response text",
            "intent": "detected_intent",
            "action_results": [list of action results]
        }
    }
    """
    if not ('user' in session and session['user']):
        return jsonify({
            "success": False,
            "error": "Authentication required"
        }), 401

    # Get chat message from request
    data = request.json
    if not data or 'message' not in data:
        return jsonify({
            "success": False,
            "error": "No message provided"
        }), 400

    message = data['message']

    try:
        # Get chat processor and process message
        chat_processor = get_chat_processor()
        response = chat_processor.process_message(
            message=message,
            user_id=session.get('user', {}).get('id', 'demo_user'),
            session=session
        )

        return jsonify({
            "success": True,
            "response": response
        })

    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return jsonify({
            "success": False,
            "error": f"Error processing message: {str(e)}"
        }), 500

@api_bp.route('/user/profile', methods=['GET'])
def get_user_profile():
    """Get the current user's profile information"""
    if not ('user' in session and session['user']):
        return jsonify({"error": "Authentication required"}), 401

    try:
        profile = {
            "id": session.get('user', {}).get('id', 'demo_user'),
            "username": session.get('user', {}).get('username,
            "email": session.get('user', {}).get('email,
            "first_name": session.get('user', {}).get('first_name,
            "last_name": session.get('user', {}).get('last_name,
            "created_at": session.get('user', {}).get('created_at.isoformat() if hasattr(session.get('user'), 'created_at') else None,
        }
        return jsonify({"success": True, "profile": profile})
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/user/settings', methods=['GET', 'PUT'])
def user_settings():
    """Get or update user settings"""
    if not ('user' in session and session['user']):
        return jsonify({"error": "Authentication required"}), 401

    # Handle GET request
    if request.method == 'GET':
        try:
            settings = {
                "theme": session.get('user', {}).get('get_setting('theme', 'light'),
                "notifications_enabled": session.get('user', {}).get('get_setting('notifications_enabled', True),
                "language": session.get('user', {}).get('get_setting('language', 'en')
            }
            return jsonify({"success": True, "settings": settings})
        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # Handle PUT request
    elif request.method == 'PUT':
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        try:
            # Update settings
            for key, value in data.items():
                session.get('user', {}).get('set_setting(key, value)

            return jsonify({"success": True, "message": "Settings updated successfully"})
        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500