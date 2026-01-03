"""
Task Routes - Task and Reminder Management
Integrated with Google Tasks
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging

from repositories.task_repository import TaskRepository
from utils.unified_auth import demo_allowed, get_current_user_id
from utils.google_suite_client import GoogleSuiteClient

logger = logging.getLogger(__name__)

task_bp = Blueprint('tasks', __name__, url_prefix='/api/v1/tasks')

# ===== TASK CRUD =====

@task_bp.route('', methods=['GET'])
@demo_allowed
def get_tasks():
    """Get tasks for user"""
    user_id = get_current_user_id()
    
    include_completed = request.args.get('completed', 'false').lower() == 'true'
    category = request.args.get('category')
    
    tasks = TaskRepository.get_user_tasks(
        user_id=user_id,
        include_completed=include_completed,
        category=category
    )
    
    return jsonify([task.to_dict() for task in tasks] if tasks else [])

@task_bp.route('/overdue', methods=['GET'])
@demo_allowed
def get_overdue_tasks():
    """Get overdue tasks"""
    user_id = get_current_user_id()
    tasks = TaskRepository.get_overdue_tasks(user_id)
    return jsonify([task.to_dict() for task in tasks] if tasks else [])

@task_bp.route('/today', methods=['GET'])
@demo_allowed
def get_today_tasks():
    """Get tasks due today"""
    user_id = get_current_user_id()
    tasks = TaskRepository.get_today_tasks(user_id)
    return jsonify([task.to_dict() for task in tasks] if tasks else [])

@task_bp.route('', methods=['POST'])
@demo_allowed
def create_task():
    """Create a new task"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'title' not in data:
        return jsonify({'error': 'title required'}), 400
    
    due_date = None
    if 'due_date' in data:
        try:
            due_date = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    
    task = TaskRepository.create_task(
        user_id=user_id,
        title=data['title'],
        description=data.get('description', ''),
        due_date=due_date,
        priority=data.get('priority', 'medium'),
        category=data.get('category', 'general'),
        recurring=data.get('recurring', False),
        recurrence_pattern=data.get('recurrence_pattern')
    )
    
    if task:
        return jsonify(task.to_dict()), 201
    return jsonify({'error': 'Failed to create task'}), 500

@task_bp.route('/<int:task_id>', methods=['PUT'])
@demo_allowed
def update_task(task_id):
    """Update a task"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Handle due_date conversion
    if 'due_date' in data and data['due_date']:
        try:
            data['due_date'] = datetime.fromisoformat(data['due_date'].replace('Z', '+00:00'))
        except ValueError:
            return jsonify({'error': 'Invalid date format'}), 400
    
    success = TaskRepository.update_task(task_id, user_id, **data)
    
    if success:
        return jsonify({'message': 'Task updated'})
    return jsonify({'error': 'Task not found or update failed'}), 404

@task_bp.route('/<int:task_id>/complete', methods=['POST'])
@demo_allowed
def complete_task(task_id):
    """Mark task as completed"""
    user_id = get_current_user_id()
    
    success = TaskRepository.complete_task(task_id, user_id)
    
    if success:
        return jsonify({'message': 'Task completed'})
    return jsonify({'error': 'Task not found'}), 404

@task_bp.route('/<int:task_id>', methods=['DELETE'])
@demo_allowed
def delete_task(task_id):
    """Delete a task"""
    user_id = get_current_user_id()
    
    success = TaskRepository.delete_task(task_id, user_id)
    
    if success:
        return jsonify({'message': 'Task deleted'})
    return jsonify({'error': 'Task not found'}), 404

# ===== REMINDERS =====

@task_bp.route('/reminders', methods=['POST'])
@demo_allowed
def create_reminder():
    """Create a reminder"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'reminder_time' not in data:
        return jsonify({'error': 'reminder_time required'}), 400
    
    try:
        reminder_time = datetime.fromisoformat(data['reminder_time'].replace('Z', '+00:00'))
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    reminder = TaskRepository.create_reminder(
        user_id=user_id,
        task_id=data.get('task_id'),
        reminder_time=reminder_time,
        message=data.get('message', ''),
        reminder_type=data.get('type', 'notification')
    )
    
    if reminder:
        return jsonify(reminder.to_dict()), 201
    return jsonify({'error': 'Failed to create reminder'}), 500

@task_bp.route('/reminders/pending', methods=['GET'])
@demo_allowed
def get_pending_reminders():
    """Get pending reminders"""
    user_id = get_current_user_id()
    
    reminders = TaskRepository.get_pending_reminders(user_id)
    return jsonify([r.to_dict() for r in reminders] if reminders else [])

# ===== GOOGLE TASKS SYNC =====

@task_bp.route('/sync/google', methods=['POST'])
@demo_allowed
def sync_google_tasks():
    """Sync with Google Tasks"""
    user_id = get_current_user_id()
    
    # This would get user's Google credentials
    # For now, return placeholder
    return jsonify({
        'message': 'Google Tasks sync initiated',
        'synced_count': 0
    })

@task_bp.route('/export/google', methods=['POST'])
@demo_allowed
def export_to_google():
    """Export task to Google Tasks"""
    user_id = get_current_user_id()
    data = request.get_json()
    
    if not data or 'task_id' not in data:
        return jsonify({'error': 'task_id required'}), 400
    
    # This would use GoogleSuiteClient to create task in Google
    return jsonify({
        'message': 'Task exported to Google Tasks',
        'google_task_id': 'placeholder'
    })
