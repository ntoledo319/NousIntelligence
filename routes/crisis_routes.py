"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated
    
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

Crisis management routes
All routes are prefixed with /crisis
"""

import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session

# Import database from database module to avoid circular imports
from database import db
from models import User

# Import DBT crisis helper functions
from utils.dbt_crisis_helper import (
    get_crisis_resources, add_crisis_resource, update_crisis_resource,
    delete_crisis_resource, generate_crisis_plan, get_grounding_exercise,
    get_crisis_de_escalation
)

crisis_bp = Blueprint('crisis', __name__, url_prefix='/crisis')

# Helper to get user_id from session.get('user')
def get_user_id():
    return str(session.get('user', {}).get('id', 'demo_user')) if ('user' in session and session['user']) else None

@crisis_bp.route('/')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def index():
    """Crisis management dashboard"""
    user_id = get_user_id()

    # Get user's crisis resources
    resources = get_crisis_resources(user_id)

    # Generate a crisis plan if one doesn't exist
    crisis_plan = generate_crisis_plan(user_id)

    return render_template(
        'crisis/index.html',
        resources=resources,
        crisis_plan=crisis_plan
    )

@crisis_bp.route('/mobile')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def mobile_interface():
    """Mobile-optimized crisis interface"""
    user_id = get_user_id()

    # Get grounding exercise
    grounding = get_grounding_exercise(user_id)

    # Get de-escalation techniques with default intensity 2 (medium)
    de_escalation = get_crisis_de_escalation(user_id, 2)

    # Get crisis resources (key contacts)
    resources = get_crisis_resources(user_id)

    return render_template(
        'crisis/mobile.html',
        grounding=grounding,
        de_escalation=de_escalation,
        resources=resources
    )

@crisis_bp.route('/grounding')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def grounding():
    """Grounding exercises page"""
    user_id = get_user_id()

    # Get a grounding exercise
    exercise = get_grounding_exercise(user_id)

    return render_template(
        'crisis/grounding.html',
        exercise=exercise
    )

@crisis_bp.route('/de-escalation')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def de_escalation():
    """De-escalation techniques page"""
    user_id = get_user_id()

    # Get de-escalation techniques with default intensity 2 (medium)
    techniques = get_crisis_de_escalation(user_id, 2)

    return render_template(
        'crisis/de_escalation.html',
        techniques=techniques
    )

@crisis_bp.route('/resources')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def resources():
    """Crisis resources page"""
    user_id = get_user_id()

    # Get crisis resources
    resources_list = get_crisis_resources(user_id)

    return render_template(
        'crisis/resources.html',
        resources=resources_list
    )

@crisis_bp.route('/add-resource', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def add_resource():
    """Add a new crisis resource"""
    user_id = get_user_id()

    # Get form data
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    description = request.form.get('description', '').strip()
    type_category = request.form.get('type', 'personal').strip()

    if not name:
        flash("Resource name is required", "error")
        return redirect(url_for('crisis.resources'))

    # Add the resource
    result = add_crisis_resource(user_id, name, phone, description, type_category)

    if result.get('success'):
        flash("Crisis resource added successfully", "success")
    else:
        flash(f"Error adding resource: {result.get('error', 'Unknown error')}", "error")

    return redirect(url_for('crisis.resources'))

@crisis_bp.route('/update-resource/<int:resource_id>', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def update_resource(resource_id):
    """Update a crisis resource"""
    user_id = get_user_id()

    # Get form data
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    description = request.form.get('description', '').strip()
    type_category = request.form.get('type', 'personal').strip()

    if not name:
        flash("Resource name is required", "error")
        return redirect(url_for('crisis.resources'))

    # Update the resource
    result = update_crisis_resource(user_id, resource_id, name, phone, description, type_category)

    if result.get('success'):
        flash("Crisis resource updated successfully", "success")
    else:
        flash(f"Error updating resource: {result.get('error', 'Unknown error')}", "error")

    return redirect(url_for('crisis.resources'))

@crisis_bp.route('/delete-resource/<int:resource_id>', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def delete_resource(resource_id):
    """Delete a crisis resource"""
    user_id = get_user_id()

    # Delete the resource
    result = delete_crisis_resource(user_id, resource_id)

    if result.get('success'):
        flash("Crisis resource deleted successfully", "success")
    else:
        flash(f"Error deleting resource: {result.get('error', 'Unknown error')}", "error")

    return redirect(url_for('crisis.resources'))

@crisis_bp.route('/mobile')

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def mobile_crisis():
    """Mobile-optimized crisis support page - accessible without login"""
    return render_template('crisis/mobile.html')