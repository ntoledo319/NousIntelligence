from flask import Blueprint, jsonify, request
from src.infrastructure.di_container import container
from utils.unified_auth import demo_allowed, get_demo_user
from utils.encryption import encrypt_field, decrypt_field
import logging

logger = logging.getLogger(__name__)

tasks_bp = Blueprint('tasks', __name__, url_prefix='/api/tasks')

@tasks_bp.route('/health')
def health():
    """Health check for tasks service"""
    return jsonify({'status': 'healthy', 'service': 'tasks'})

@tasks_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@tasks_bp.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error in tasks: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@tasks_bp.route('/tasks', methods=['GET'])
@demo_allowed
def get_tasks():
    """Get all tasks for the authenticated user"""
    # In a real implementation, this would fetch tasks for the current user
    # For now, return an empty list for testing
    return jsonify([])

@tasks_bp.route('/tasks', methods=['POST'])
@demo_allowed
def create_task():
    """Create a new task"""
    # Use silent JSON parsing so tests exercising validation don't receive
    # a 415 Unsupported Media Type for empty or invalid bodies.
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    if 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    # Create task (simplified for demo)
    task = {
        'id': '1',
        'title': data['title'],
        'description': data.get('description', ''),
        'completed': False,
        'user_id': get_demo_user().get('id', 'demo_user')
    }
    return jsonify(task), 201

@tasks_bp.route('/tasks/<task_id>', methods=['GET'])
@demo_allowed
def get_task(task_id):
    """Get a specific task by ID"""
    # In a real implementation, this would fetch the task by ID
    # For now, return a 404 if the task doesn't exist
    if task_id != '1':
        return jsonify({'error': 'Task not found'}), 404
    
    task = {
        'id': task_id,
        'title': 'Sample Task',
        'description': 'This is a sample task',
        'completed': False
    }
    return jsonify(task)

@tasks_bp.route('/tasks/<task_id>', methods=['PUT'])
@demo_allowed
def update_task(task_id):
    """Update an existing task"""
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # In a real implementation, this would update the task
    # For now, return a success response with the updated task data
    task = {
        'id': task_id,
        'title': data.get('title', 'Updated Task'),
        'description': data.get('description', ''),
        'completed': data.get('completed', False)
    }
    return jsonify(task)

@tasks_bp.route('/tasks/<task_id>', methods=['DELETE'])
@demo_allowed
def delete_task(task_id):
    """Delete a task"""
    # In a real implementation, this would delete the task
    # For now, return a success response
    return '', 204
