"""
Crisis management routes
All routes are prefixed with /crisis
"""

import os
import json
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user

# Import database from app_factory instead of app to avoid circular imports
from app_factory import db
from models import User

# Import DBT crisis helper functions
from utils.dbt_crisis_helper import (
    get_crisis_resources, add_crisis_resource, update_crisis_resource,
    delete_crisis_resource, generate_crisis_plan, get_grounding_exercise,
    get_crisis_de_escalation
)

crisis_bp = Blueprint('crisis', __name__, url_prefix='/crisis')

# Helper to get user_id from current_user
def get_user_id():
    return str(current_user.id) if current_user.is_authenticated else None

@crisis_bp.route('/')
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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
@login_required
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