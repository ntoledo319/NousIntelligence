"""
API Routes Module (Fixed Version)

This module defines API routes for accessing application data.
Fixed syntax errors and improved structure from routes/api.py

@module routes.api_fixed
@description Fixed API routes for data access
"""

import logging
from flask import Blueprint, jsonify, request, session

# Fixed import structure
try:
    from models import db, Task
except ImportError:
    # Fallback for testing
    db = None
    Task = None

# Create blueprint with version prefix
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
logger = logging.getLogger(__name__)

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
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_demo_user():
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
    user = session.get('user', {})
    if hasattr(user, 'to_dict') and callable(user.to_dict):
        return jsonify(user.to_dict())
    else:
        return jsonify(user)

@api_bp.route('/settings', methods=['GET'])
def get_settings():
    """Get user settings"""
    user = session.get('user', {})
    settings = getattr(user, 'settings', None)
    
    if not settings:
        return jsonify({'error': 'Settings not found'}), 404

    if hasattr(settings, 'to_dict') and callable(settings.to_dict):
        return jsonify(settings.to_dict())
    else:
        return jsonify(settings)

@api_bp.route('/settings', methods=['POST'])
def update_settings():
    """Update user settings"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        user = session.get('user', {})
        
        # Create settings if they don't exist
        if not getattr(user, 'settings', None):
            if db and Task:  # Only if models are available
                from models import UserSettings
                settings = UserSettings(user_id=user.get('id', 'demo_user'))
                db.session.add(settings)
                user['settings'] = settings

        # Update valid fields
        valid_fields = [
            'theme', 'ai_name', 'ai_personality', 'preferred_language',
            'enable_voice_responses', 'conversation_difficulty'
        ]

        settings = user.get('settings', {})
        for field in valid_fields:
            if field in data:
                if hasattr(settings, field):
                    setattr(settings, field, data[field])
                else:
                    settings[field] = data[field]

        # Save changes if database is available
        if db:
            db.session.commit()

        if hasattr(settings, 'to_dict') and callable(settings.to_dict):
            return jsonify(settings.to_dict())
        else:
            return jsonify(settings)
            
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks', methods=['GET'])
def get_tasks():
    """Get user tasks"""
    user = session.get('user', {})
    tasks = getattr(user, 'tasks', [])
    
    if hasattr(tasks, '__iter__'):
        task_list = []
        for task in tasks:
            if hasattr(task, 'to_dict') and callable(task.to_dict):
                task_list.append(task.to_dict())
            else:
                task_list.append(task)
        return jsonify(task_list)
    else:
        return jsonify([])

@api_bp.route('/tasks', methods=['POST'])
def create_task():
    """Create a new task"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400

        if Task and db:
            # Create task with proper model
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
        else:
            # Fallback for demo mode
            task = {
                'id': 'demo_task',
                'user_id': session.get('user', {}).get('id', 'demo_user'),
                'title': data['title'],
                'description': data.get('description'),
                'priority': data.get('priority', 'medium'),
                'due_date': data.get('due_date'),
                'completed': False
            }
            return jsonify(task), 201
            
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Get a specific task"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    if Task:
        task = Task.query.get(task_id)
        if not task or task.user_id != session.get('user', {}).get('id', 'demo_user'):
            return jsonify({'error': 'Task not found'}), 404
        return jsonify(task.to_dict())
    else:
        # Demo fallback
        return jsonify({'error': 'Task not found'}), 404

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Update an existing task"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        if Task and db:
            task = Task.query.get(task_id)
            if not task or task.user_id != session.get('user', {}).get('id', 'demo_user'):
                return jsonify({'error': 'Task not found'}), 404

            # Update task with request data
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
        else:
            return jsonify({'error': 'Task not found'}), 404
            
    except Exception as e:
        logger.error(f"Error updating task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Delete a task"""
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    try:
        if Task and db:
            task = Task.query.get(task_id)
            if not task or task.user_id != session.get('user', {}).get('id', 'demo_user'):
                return jsonify({'error': 'Task not found'}), 404

            # Delete the task
            db.session.delete(task)
            db.session.commit()
            return jsonify({'message': 'Task deleted successfully'}), 200
        else:
            return jsonify({'error': 'Task not found'}), 404
            
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/chat', methods=['POST'])
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
    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result
        
    # Get chat message from request
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({
            "success": False,
            "error": "No message provided"
        }), 400

    message = data['message']

    try:
        # Demo response for now
        response = {
            "text": f"I received your message: {message}",
            "intent": "demo",
            "action_results": []
        }

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
        return jsonify({"error": "Demo mode - limited access"}), 401

    try:
        user = session.get('user', {})
        profile = {
            "id": user.get('id', 'demo_user'),
            "username": user.get('username'),
            "email": user.get('email'),
            "first_name": user.get('first_name'),
            "last_name": user.get('last_name'),
            "created_at": user.get('created_at').isoformat() if hasattr(user.get('created_at'), 'isoformat') else None,
        }
        return jsonify({"success": True, "profile": profile})
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/user/settings', methods=['GET', 'PUT'])
def user_settings():
    """Get or update user settings"""
    if not ('user' in session and session['user']):
        return jsonify({"error": "Demo mode - limited access"}), 401

    user = session.get('user', {})
    
    # Handle GET request
    if request.method == 'GET':
        try:
            settings = {
                "theme": user.get('theme', 'light'),
                "notifications_enabled": user.get('notifications_enabled', True),
                "language": user.get('language', 'en')
            }
            return jsonify({"success": True, "settings": settings})
        except Exception as e:
            logger.error(f"Error getting user settings: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500

    # Handle PUT request
    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"}), 400

        try:
            # Update settings in session
            for key, value in data.items():
                user[key] = value
            session['user'] = user

            return jsonify({"success": True, "message": "Settings updated successfully"})
        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500