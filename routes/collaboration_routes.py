"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Collaboration Routes Routes
Collaboration Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

collaboration_routes_bp = Blueprint('collaboration_routes', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
    
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

def get_get_demo_user()():
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

Collaboration Routes - Team and Family Management Features
Shared tasks, family calendars, group activities, and collaborative planning
"""

import logging
from datetime import datetime, timezone, timedelta
from flask import Blueprint, request, jsonify, session, render_template
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

# Create blueprint
collaboration_bp = Blueprint('collaboration', __name__, url_prefix='/collaboration')

# Sample data for development
SAMPLE_FAMILIES = [
    {
        'id': 'fam_001',
        'name': 'The Johnson Family',
        'description': 'Our family organization hub',
        'members': [
            {'id': 'user_001', 'name': 'John Johnson', 'role': 'admin', 'avatar': '/static/images/avatar1.png'},
            {'id': 'user_002', 'name': 'Sarah Johnson', 'role': 'admin', 'avatar': '/static/images/avatar2.png'},
            {'id': 'user_003', 'name': 'Emma Johnson', 'role': 'member', 'avatar': '/static/images/avatar3.png'},
            {'id': 'user_004', 'name': 'Alex Johnson', 'role': 'member', 'avatar': '/static/images/avatar4.png'}
        ],
        'created_at': '2024-01-15T10:00:00Z',
        'settings': {
            'allow_member_invites': True,
            'require_admin_approval': False,
            'default_task_visibility': 'family'
        }
    }
]

SAMPLE_SHARED_TASKS = [
    {
        'id': 'task_001',
        'title': 'Weekly Grocery Shopping',
        'description': 'Buy groceries for the week',
        'assigned_to': 'user_001',
        'created_by': 'user_002',
        'family_id': 'fam_001',
        'status': 'pending',
        'priority': 'medium',
        'due_date': (datetime.now(timezone.utc) + timedelta(days=2)).isoformat(),
        'category': 'household',
        'recurring': 'weekly',
        'shared_with': ['user_001', 'user_002'],
        'comments': [
            {
                'id': 'comment_001',
                'user_id': 'user_002',
                'user_name': 'Sarah Johnson',
                'text': 'Don\'t forget the organic milk!',
                'created_at': datetime.now(timezone.utc).isoformat()
            }
        ]
    },
    {
        'id': 'task_002',
        'title': 'Plan Summer Vacation',
        'description': 'Research and book our family summer vacation',
        'assigned_to': 'user_002',
        'created_by': 'user_001',
        'family_id': 'fam_001',
        'status': 'in_progress',
        'priority': 'high',
        'due_date': (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
        'category': 'travel',
        'recurring': None,
        'shared_with': ['user_001', 'user_002', 'user_003', 'user_004'],
        'comments': []
    },
    {
        'id': 'task_003',
        'title': 'Emma\'s Soccer Practice Pickup',
        'description': 'Pick up Emma from soccer practice',
        'assigned_to': 'user_001',
        'created_by': 'user_002',
        'family_id': 'fam_001',
        'status': 'completed',
        'priority': 'high',
        'due_date': (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
        'category': 'kids',
        'recurring': 'twice_weekly',
        'shared_with': ['user_001', 'user_002'],
        'comments': []
    }
]

SAMPLE_SHARED_EVENTS = [
    {
        'id': 'event_001',
        'title': 'Family Game Night',
        'description': 'Weekly family game night with pizza',
        'start_time': (datetime.now(timezone.utc) + timedelta(days=5, hours=18)).isoformat(),
        'end_time': (datetime.now(timezone.utc) + timedelta(days=5, hours=21)).isoformat(),
        'location': 'Living Room',
        'family_id': 'fam_001',
        'created_by': 'user_002',
        'attendees': ['user_001', 'user_002', 'user_003', 'user_004'],
        'category': 'family_time',
        'recurring': 'weekly'
    },
    {
        'id': 'event_002',
        'title': 'Parent-Teacher Conference',
        'description': 'Emma\'s parent-teacher conference',
        'start_time': (datetime.now(timezone.utc) + timedelta(days=10, hours=15, minutes=30)).isoformat(),
        'end_time': (datetime.now(timezone.utc) + timedelta(days=10, hours=16)).isoformat(),
        'location': 'Emma\'s School',
        'family_id': 'fam_001',
        'created_by': 'user_001',
        'attendees': ['user_001', 'user_002'],
        'category': 'school',
        'recurring': None
    }
]

SAMPLE_SHOPPING_LISTS = [
    {
        'id': 'list_001',
        'name': 'Weekly Groceries',
        'family_id': 'fam_001',
        'created_by': 'user_002',
        'items': [
            {'id': 'item_001', 'name': 'Organic Milk', 'quantity': '1 gallon', 'completed': False, 'added_by': 'user_002'},
            {'id': 'item_002', 'name': 'Bread', 'quantity': '2 loaves', 'completed': True, 'added_by': 'user_001'},
            {'id': 'item_003', 'name': 'Bananas', 'quantity': '6', 'completed': False, 'added_by': 'user_003'},
            {'id': 'item_004', 'name': 'Chicken Breast', 'quantity': '2 lbs', 'completed': False, 'added_by': 'user_002'},
            {'id': 'item_005', 'name': 'Yogurt', 'quantity': '4 cups', 'completed': False, 'added_by': 'user_004'}
        ],
        'shared_with': ['user_001', 'user_002', 'user_003', 'user_004'],
        'last_updated': datetime.now(timezone.utc).isoformat()
    },
    {
        'id': 'list_002',
        'name': 'Vacation Packing',
        'family_id': 'fam_001',
        'created_by': 'user_001',
        'items': [
            {'id': 'item_006', 'name': 'Sunscreen', 'quantity': '2 bottles', 'completed': False, 'added_by': 'user_001'},
            {'id': 'item_007', 'name': 'Beach Towels', 'quantity': '4', 'completed': False, 'added_by': 'user_002'},
            {'id': 'item_008', 'name': 'Swimming Goggles', 'quantity': '2 pairs', 'completed': True, 'added_by': 'user_003'}
        ],
        'shared_with': ['user_001', 'user_002', 'user_003', 'user_004'],
        'last_updated': datetime.now(timezone.utc).isoformat()
    }
]

@collaboration_bp.route('/')
def collaboration_dashboard():
    """Main collaboration dashboard"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return render_template('collaboration/login_required.html'), 401
        
        # Get user's families
        user_families = [f for f in SAMPLE_FAMILIES if any(m['id'] == user_id for m in f['members'])]
        
        # Get recent shared tasks
        recent_tasks = sorted(SAMPLE_SHARED_TASKS, key=lambda x: x['due_date'], reverse=True)[:5]
        
        # Get upcoming events
        upcoming_events = [e for e in SAMPLE_SHARED_EVENTS 
                          if datetime.fromisoformat(e['start_time'].replace('Z', '+00:00')) > datetime.now(timezone.utc)]
        upcoming_events = sorted(upcoming_events, key=lambda x: x['start_time'])[:5]
        
        # Get active shopping lists
        active_lists = SAMPLE_SHOPPING_LISTS
        
        return render_template('collaboration/dashboard.html',
                             families=user_families,
                             recent_tasks=recent_tasks,
                             upcoming_events=upcoming_events,
                             shopping_lists=active_lists)
    
    except Exception as e:
        logger.error(f"Error loading collaboration dashboard: {str(e)}")
        return render_template('error.html', error="Failed to load collaboration dashboard"), 500

@collaboration_bp.route('/api/families')
def get_families():
    """Get user's families"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        # Filter families where user is a member
        user_families = [f for f in SAMPLE_FAMILIES if any(m['id'] == user_id for m in f['members'])]
        
        return jsonify({
            'success': True,
            'families': user_families,
            'total_count': len(user_families)
        })
    
    except Exception as e:
        logger.error(f"Error getting families: {str(e)}")
        return jsonify({'error': 'Failed to retrieve families'}), 500

@collaboration_bp.route('/api/families', methods=['POST'])
def create_family():
    """Create a new family group"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'error': 'Family name is required'}), 400
        
        # Create new family
        new_family = {
            'id': f"fam_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'name': data['name'],
            'description': data.get('description', ''),
            'members': [
                {
                    'id': user_id,
                    'name': session.get('user_name', 'User'),
                    'role': 'admin',
                    'avatar': '/static/images/default_avatar.png'
                }
            ],
            'created_at': datetime.now(timezone.utc).isoformat(),
            'settings': {
                'allow_member_invites': data.get('allow_member_invites', True),
                'require_admin_approval': data.get('require_admin_approval', False),
                'default_task_visibility': data.get('default_task_visibility', 'family')
            }
        }
        
        return jsonify({
            'success': True,
            'family': new_family
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating family: {str(e)}")
        return jsonify({'error': 'Failed to create family'}), 500

@collaboration_bp.route('/api/families/<family_id>/tasks')
def get_family_tasks(family_id):
    """Get tasks for a specific family"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        # Filter tasks for this family
        family_tasks = [t for t in SAMPLE_SHARED_TASKS if t['family_id'] == family_id]
        
        # Apply filters
        status_filter = request.args.get('status')
        assigned_to_filter = request.args.get('assigned_to')
        
        if status_filter:
            family_tasks = [t for t in family_tasks if t['status'] == status_filter]
        
        if assigned_to_filter:
            family_tasks = [t for t in family_tasks if t['assigned_to'] == assigned_to_filter]
        
        # Sort by due date
        family_tasks = sorted(family_tasks, key=lambda x: x['due_date'])
        
        return jsonify({
            'success': True,
            'tasks': family_tasks,
            'total_count': len(family_tasks)
        })
    
    except Exception as e:
        logger.error(f"Error getting family tasks: {str(e)}")
        return jsonify({'error': 'Failed to retrieve family tasks'}), 500

@collaboration_bp.route('/api/families/<family_id>/tasks', methods=['POST'])
def create_family_task(family_id):
    """Create a new shared task"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'assigned_to']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Create new task
        new_task = {
            'id': f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'title': data['title'],
            'description': data.get('description', ''),
            'assigned_to': data['assigned_to'],
            'created_by': user_id,
            'family_id': family_id,
            'status': 'pending',
            'priority': data.get('priority', 'medium'),
            'due_date': data.get('due_date'),
            'category': data.get('category', 'general'),
            'recurring': data.get('recurring'),
            'shared_with': data.get('shared_with', []),
            'comments': [],
            'created_at': datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify({
            'success': True,
            'task': new_task
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating family task: {str(e)}")
        return jsonify({'error': 'Failed to create task'}), 500

@collaboration_bp.route('/api/tasks/<task_id>/status', methods=['PUT'])
def update_task_status(task_id):
    """Update task status"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status not in ['pending', 'in_progress', 'completed', 'cancelled']:
            return jsonify({'error': 'Invalid status'}), 400
        
        # Find and update task
        for task in SAMPLE_SHARED_TASKS:
            if task['id'] == task_id:
                task['status'] = new_status
                if new_status == 'completed':
                    task['completed_at'] = datetime.now(timezone.utc).isoformat()
                
                return jsonify({
                    'success': True,
                    'task': task
                })
        
        return jsonify({'error': 'Task not found'}), 404
    
    except Exception as e:
        logger.error(f"Error updating task status: {str(e)}")
        return jsonify({'error': 'Failed to update task status'}), 500

@collaboration_bp.route('/api/families/<family_id>/events')
def get_family_events(family_id):
    """Get events for a specific family"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        # Filter events for this family
        family_events = [e for e in SAMPLE_SHARED_EVENTS if e['family_id'] == family_id]
        
        # Sort by start time
        family_events = sorted(family_events, key=lambda x: x['start_time'])
        
        return jsonify({
            'success': True,
            'events': family_events,
            'total_count': len(family_events)
        })
    
    except Exception as e:
        logger.error(f"Error getting family events: {str(e)}")
        return jsonify({'error': 'Failed to retrieve family events'}), 500

@collaboration_bp.route('/api/families/<family_id>/shopping-lists')
def get_shopping_lists(family_id):
    """Get shopping lists for a family"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        # Filter shopping lists for this family
        family_lists = [l for l in SAMPLE_SHOPPING_LISTS if l['family_id'] == family_id]
        
        return jsonify({
            'success': True,
            'shopping_lists': family_lists,
            'total_count': len(family_lists)
        })
    
    except Exception as e:
        logger.error(f"Error getting shopping lists: {str(e)}")
        return jsonify({'error': 'Failed to retrieve shopping lists'}), 500

@collaboration_bp.route('/api/shopping-lists/<list_id>/items', methods=['POST'])
def add_shopping_item(list_id):
    """Add item to shopping list"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        data = request.get_json()
        
        if not data.get('name'):
            return jsonify({'error': 'Item name is required'}), 400
        
        # Find shopping list and add item
        for shopping_list in SAMPLE_SHOPPING_LISTS:
            if shopping_list['id'] == list_id:
                new_item = {
                    'id': f"item_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    'name': data['name'],
                    'quantity': data.get('quantity', '1'),
                    'completed': False,
                    'added_by': user_id,
                    'added_at': datetime.now(timezone.utc).isoformat()
                }
                
                shopping_list['items'].append(new_item)
                shopping_list['last_updated'] = datetime.now(timezone.utc).isoformat()
                
                return jsonify({
                    'success': True,
                    'item': new_item,
                    'shopping_list': shopping_list
                })
        
        return jsonify({'error': 'Shopping list not found'}), 404
    
    except Exception as e:
        logger.error(f"Error adding shopping item: {str(e)}")
        return jsonify({'error': 'Failed to add item'}), 500

@collaboration_bp.route('/api/shopping-items/<item_id>/toggle', methods=['PUT'])
def toggle_shopping_item(item_id):
    """Toggle shopping item completion status"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': "Demo mode - limited access"}), 401
        
        # Find item across all shopping lists
        for shopping_list in SAMPLE_SHOPPING_LISTS:
            for item in shopping_list['items']:
                if item['id'] == item_id:
                    item['completed'] = not item['completed']
                    shopping_list['last_updated'] = datetime.now(timezone.utc).isoformat()
                    
                    return jsonify({
                        'success': True,
                        'item': item,
                        'shopping_list': shopping_list
                    })
        
        return jsonify({'error': 'Item not found'}), 404
    
    except Exception as e:
        logger.error(f"Error toggling shopping item: {str(e)}")
        return jsonify({'error': 'Failed to toggle item'}), 500

@collaboration_bp.route('/families')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def families_page():
    """Family management page"""
    return render_template('collaboration/families.html', families=SAMPLE_FAMILIES)

@collaboration_bp.route('/families/<family_id>')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def family_detail_page(family_id):
    """Individual family detail page"""
    family = next((f for f in SAMPLE_FAMILIES if f['id'] == family_id), None)
    if not family:
        return render_template('collaboration/family_not_found.html'), 404
    
    return render_template('collaboration/family_detail.html', family=family)

@collaboration_bp.route('/tasks')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def tasks_page():
    """Shared tasks page"""
    return render_template('collaboration/tasks.html', tasks=SAMPLE_SHARED_TASKS)

@collaboration_bp.route('/calendar')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def calendar_page():
    """Shared family calendar page"""
    return render_template('collaboration/calendar.html', events=SAMPLE_SHARED_EVENTS)

@collaboration_bp.route('/shopping')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def shopping_page():
    """Shared shopping lists page"""
    return render_template('collaboration/shopping.html', shopping_lists=SAMPLE_SHOPPING_LISTS)

# Error handlers
@collaboration_bp.errorhandler(404)
def collaboration_not_found(error):
    return render_template('collaboration/404.html'), 404

@collaboration_bp.errorhandler(500)
def collaboration_server_error(error):
    return render_template('collaboration/500.html'), 500

# Utility functions
def get_family_statistics(family_id):
    """Get statistics for a family"""
    family_tasks = [t for t in SAMPLE_SHARED_TASKS if t['family_id'] == family_id]
    family_events = [e for e in SAMPLE_SHARED_EVENTS if e['family_id'] == family_id]
    
    return {
        'total_tasks': len(family_tasks),
        'completed_tasks': len([t for t in family_tasks if t['status'] == 'completed']),
        'pending_tasks': len([t for t in family_tasks if t['status'] == 'pending']),
        'upcoming_events': len([e for e in family_events 
                               if datetime.fromisoformat(e['start_time'].replace('Z', '+00:00')) > datetime.now(timezone.utc)]),
        'total_events': len(family_events)
    }

def generate_family_insights(family_id):
    """Generate insights for family collaboration"""
    insights = []
    
    family_tasks = [t for t in SAMPLE_SHARED_TASKS if t['family_id'] == family_id]
    
    # Task completion analysis
    completed_tasks = [t for t in family_tasks if t['status'] == 'completed']
    if family_tasks:
        completion_rate = (len(completed_tasks) / len(family_tasks)) * 100
        insights.append({
            'type': 'info',
            'message': f"Your family has a {completion_rate:.1f}% task completion rate",
            'action': 'Keep up the great teamwork!' if completion_rate > 80 else 'Consider better task distribution'
        })
    
    # Overdue tasks
    overdue_tasks = [t for t in family_tasks 
                    if t['status'] != 'completed' and 
                    datetime.fromisoformat(t['due_date'].replace('Z', '+00:00')) < datetime.now(timezone.utc)]
    
    if overdue_tasks:
        insights.append({
            'type': 'warning',
            'message': f"You have {len(overdue_tasks)} overdue tasks",
            'action': 'Review and reassign or update due dates'
        })
    
    return insights