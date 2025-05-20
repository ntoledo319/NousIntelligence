"""
API Routes Module

This module defines API routes for accessing application data.

@module routes.api
@description API routes for data access
"""

import logging
from flask import Blueprint, jsonify, request, session
from flask_login import login_required, current_user
from models import db, Task
from utils.chat_processor import get_chat_processor

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
@login_required
def get_user_info():
    """Get current user information"""
    return jsonify(current_user.to_dict())

@api_bp.route('/settings', methods=['GET'])
@login_required
def get_settings():
    """Get user settings"""
    if not current_user.settings:
        return jsonify({'error': 'Settings not found'}), 404
    
    return jsonify(current_user.settings.to_dict())

@api_bp.route('/settings', methods=['POST'])
@login_required
def update_settings():
    """Update user settings"""
    try:
        data = request.get_json()
        
        # Create settings if they don't exist
        if not current_user.settings:
            from models import UserSettings
            settings = UserSettings(user_id=current_user.id)
            db.session.add(settings)
            current_user.settings = settings
        
        # Update valid fields
        valid_fields = [
            'theme', 'ai_name', 'ai_personality', 'preferred_language',
            'enable_voice_responses', 'conversation_difficulty'
        ]
        
        for field in valid_fields:
            if field in data:
                setattr(current_user.settings, field, data[field])
        
        # Save changes
        db.session.commit()
        
        return jsonify(current_user.settings.to_dict())
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/tasks', methods=['GET'])
@login_required
def get_tasks():
    """Get user tasks"""
    tasks = [task.to_dict() for task in current_user.tasks]
    return jsonify(tasks)

@api_bp.route('/tasks', methods=['POST'])
@login_required
def create_task():
    """Create a new task"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
            
        # Create task
        task = Task(
            user_id=current_user.id,
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
@login_required
def get_task(task_id):
    """Get a specific task"""
    task = Task.query.get(task_id)
    
    if not task or task.user_id != current_user.id:
        return jsonify({'error': 'Task not found'}), 404
        
    return jsonify(task.to_dict())

@api_bp.route('/tasks/<int:task_id>', methods=['PUT'])
@login_required
def update_task(task_id):
    """Update an existing task"""
    try:
        task = Task.query.get(task_id)
        
        if not task or task.user_id != current_user.id:
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
@login_required
def delete_task(task_id):
    """Delete a task"""
    try:
        task = Task.query.get(task_id)
        
        if not task or task.user_id != current_user.id:
            return jsonify({'error': 'Task not found'}), 404
            
        # Delete the task
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/chat', methods=['POST'])
@login_required
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
    if not current_user.is_authenticated:
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
            user_id=current_user.id,
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
@login_required
def get_user_profile():
    """Get the current user's profile information"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    try:
        profile = {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "first_name": current_user.first_name,
            "last_name": current_user.last_name,
            "created_at": current_user.created_at.isoformat() if hasattr(current_user, 'created_at') else None,
        }
        return jsonify({"success": True, "profile": profile})
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@api_bp.route('/user/settings', methods=['GET', 'PUT'])
@login_required
def user_settings():
    """Get or update user settings"""
    if not current_user.is_authenticated:
        return jsonify({"error": "Authentication required"}), 401
    
    # Handle GET request
    if request.method == 'GET':
        try:
            settings = {
                "theme": current_user.get_setting('theme', 'light'),
                "notifications_enabled": current_user.get_setting('notifications_enabled', True),
                "language": current_user.get_setting('language', 'en')
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
                current_user.set_setting(key, value)
            
            return jsonify({"success": True, "message": "Settings updated successfully"})
        except Exception as e:
            logger.error(f"Error updating user settings: {str(e)}")
            return jsonify({"success": False, "error": str(e)}), 500 