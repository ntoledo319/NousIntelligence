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

Routes for Task and Productivity Management
"""
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for

from models import db, Task
from datetime import datetime
from utils.google_tasks_helper import get_tasks_service, get_task_lists, create_task
from google.oauth2.credentials import Credentials

tasks_bp = Blueprint('tasks_routes', __name__, url_prefix='/tasks')

@tasks_bp.route('/')
def tasks_dashboard():
    """Renders the main tasks dashboard."""
    user_id = session.get('user', {}).get('id', 'demo_user')
    tasks = Task.query.filter_by(user_id=user_id).order_by(Task.due_date.asc()).all()
    return render_template('tasks.html', tasks=tasks)

@tasks_bp.route('/add', methods=['POST'])
def add_task():
    """Adds a new task."""
    title = request.form.get('title')
    due_date_str = request.form.get('due_date')
    if title:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d') if due_date_str else None
        new_task = Task(user_id=session.get('user', {}).get('id', 'demo_user'), title=title, due_date=due_date)
        db.session.add(new_task)
        db.session.commit()
        flash('Task added successfully.', 'success')
    return redirect(url_for('tasks_routes.tasks_dashboard'))

@tasks_bp.route('/complete/<int:task_id>')
def complete_task(task_id):
    """Marks a task as complete."""
    task = Task.query.get(task_id)
    if task and task.user_id == session.get('user', {}).get('id', 'demo_user'):
        task.status = 'completed'
        db.session.commit()
        flash('Task marked as complete.', 'success')
    return redirect(url_for('tasks_routes.tasks_dashboard'))

@tasks_bp.route('/sync')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def sync_with_google():
    """Syncs local tasks with Google Tasks."""
    creds_data = session.get('google_creds') # Assuming creds are stored in session
    if not creds_data:
        flash('Please connect your Google account to sync tasks.', 'warning')
        return redirect(url_for('auth.authorize')) # Or your Google login route

    credentials = Credentials(**creds_data)
    service = get_tasks_service(credentials)
    
    # Get the primary task list
    task_lists = get_task_lists(service)
    task_list_id = task_lists['items'][0]['id'] if task_lists['items'] else None

    if not task_list_id:
        flash('Could not find a primary task list in your Google Tasks.', 'danger')
        return redirect(url_for('tasks_routes.tasks_dashboard'))

    # Get local tasks
    local_tasks = Task.query.filter_by(user_id=session.get('user', {}).get('id', 'demo_user')).all()

    # Simple one-way sync: local -> google
    for task in local_tasks:
        # A real implementation would check for existing tasks to avoid duplicates
        task_body = {
            'title': task.title,
            'notes': task.description,
            'due': task.due_date.isoformat() + "Z" if task.due_date else None,
            'status': 'completed' if task.status == 'completed' else 'needsAction'
        }
        create_task(service, task_list_id, task_body)

    flash('Tasks successfully synced with Google Tasks.', 'success')
    return redirect(url_for('tasks_routes.tasks_dashboard')) 