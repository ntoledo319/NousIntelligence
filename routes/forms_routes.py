"""
Google Forms routes
All routes are prefixed with /forms
"""

import os
import json
import datetime
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app, abort, Response
from flask_login import login_required, current_user

# Import database from app to avoid circular imports
from app import db

# Import Forms helper
from utils.forms_helper import (
    get_forms_service, create_form, get_form, add_text_item,
    add_multiple_choice_item, get_form_responses, analyze_form_responses,
    create_recovery_assessment_form, create_anonymous_sharing_form,
    create_daily_check_in_form
)

# Import Google API manager for connection handling
from utils.google_api_manager import get_user_connection

# Create blueprint
forms_bp = Blueprint('forms', __name__, url_prefix='/forms')

# Helper to get user connection
def get_user_forms_connection():
    """Get user's Forms service connection"""
    if not current_user.is_authenticated:
        return None

    # Get the connection
    connection = get_user_connection(current_user.id, 'google')

    if not connection:
        return None

    # Get the service
    return get_forms_service(connection)

# Forms dashboard
@forms_bp.route('/')
@login_required
def dashboard():
    """Forms dashboard showing user's forms and options to create new ones"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        flash('Google Forms connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    # Render the template
    return render_template('forms/dashboard.html')

# Create form
@forms_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new form"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        flash('Google Forms connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')

        if not title:
            flash('Form title is required', 'error')
            return redirect(url_for('forms.create'))

        # Create the form
        result = create_form(forms_service, title, description)

        if 'error' in result:
            flash(f'Error creating form: {result["error"]}', 'error')
            return redirect(url_for('forms.create'))

        flash('Form created successfully', 'success')
        return redirect(url_for('forms.view', form_id=result['form_id']))

    # GET request, render the form creation page
    return render_template('forms/create.html')

# View form
@forms_bp.route('/view/<form_id>')
@login_required
def view(form_id):
    """View a form's details"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        flash('Google Forms connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    # Get the form
    form = get_form(forms_service, form_id)

    if 'error' in form:
        flash(f'Error viewing form: {form["error"]}', 'error')
        return redirect(url_for('forms.dashboard'))

    # Get form responses
    responses = get_form_responses(forms_service, form_id)

    # Render the form view page
    return render_template('forms/view.html', form=form, responses=responses)

# Create recovery assessment form
@forms_bp.route('/recovery-assessment', methods=['GET', 'POST'])
@login_required
def recovery_assessment():
    """Create a recovery assessment form"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        flash('Google Forms connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        assessment_type = request.form.get('assessment_type', 'general')

        # Create the form
        result = create_recovery_assessment_form(forms_service, assessment_type)

        if 'error' in result:
            flash(f'Error creating assessment form: {result["error"]}', 'error')
            return redirect(url_for('forms.recovery_assessment'))

        flash('Recovery assessment form created successfully', 'success')
        return redirect(url_for('forms.view', form_id=result['form_id']))

    # GET request, render the form creation page
    return render_template('forms/recovery_assessment.html')

# Create anonymous sharing form
@forms_bp.route('/anonymous-sharing', methods=['GET', 'POST'])
@login_required
def anonymous_sharing():
    """Create an anonymous sharing form for group therapy"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        flash('Google Forms connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        group_type = request.form.get('group_type', 'support')

        # Create the form
        result = create_anonymous_sharing_form(forms_service, group_type)

        if 'error' in result:
            flash(f'Error creating sharing form: {result["error"]}', 'error')
            return redirect(url_for('forms.anonymous_sharing'))

        flash('Anonymous sharing form created successfully', 'success')
        return redirect(url_for('forms.view', form_id=result['form_id']))

    # GET request, render the form creation page
    return render_template('forms/anonymous_sharing.html')

# Create daily check-in form
@forms_bp.route('/daily-check-in', methods=['GET', 'POST'])
@login_required
def daily_check_in():
    """Create a daily check-in form"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        flash('Google Forms connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        recovery_type = request.form.get('recovery_type', 'general')

        # Create the form
        result = create_daily_check_in_form(forms_service, recovery_type)

        if 'error' in result:
            flash(f'Error creating check-in form: {result["error"]}', 'error')
            return redirect(url_for('forms.daily_check_in'))

        flash('Daily check-in form created successfully', 'success')
        return redirect(url_for('forms.view', form_id=result['form_id']))

    # GET request, render the form creation page
    return render_template('forms/daily_check_in.html')

# Analyze form responses
@forms_bp.route('/analyze/<form_id>')
@login_required
def analyze(form_id):
    """Analyze responses for a form"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        flash('Google Forms connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    # Analyze the responses
    analysis = analyze_form_responses(forms_service, form_id)

    if 'error' in analysis:
        flash(f'Error analyzing responses: {analysis["error"]}', 'error')
        return redirect(url_for('forms.view', form_id=form_id))

    # Render the analysis page
    return render_template('forms/analysis.html', analysis=analysis, form_id=form_id)

# API routes for forms
@forms_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_form():
    """API endpoint to create a form"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        return jsonify({"success": False, "error": "Google Forms connection required"}), 400

    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({"success": False, "error": "Form title is required"}), 400

    # Create the form
    result = create_form(forms_service, title, description)

    if 'error' in result:
        return jsonify({"success": False, "error": result["error"]}), 500

    return jsonify({"success": True, "form_id": result["form_id"], "url": result["url"]}), 200

@forms_bp.route('/api/recovery-assessment', methods=['POST'])
@login_required
def api_recovery_assessment():
    """API endpoint to create a recovery assessment form"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        return jsonify({"success": False, "error": "Google Forms connection required"}), 400

    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    assessment_type = data.get('assessment_type', 'general')

    # Create the form
    result = create_recovery_assessment_form(forms_service, assessment_type)

    if 'error' in result:
        return jsonify({"success": False, "error": result["error"]}), 500

    return jsonify({"success": True, "form_id": result["form_id"], "url": result["url"]}), 200

@forms_bp.route('/api/anonymous-sharing', methods=['POST'])
@login_required
def api_anonymous_sharing():
    """API endpoint to create an anonymous sharing form"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        return jsonify({"success": False, "error": "Google Forms connection required"}), 400

    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    group_type = data.get('group_type', 'support')

    # Create the form
    result = create_anonymous_sharing_form(forms_service, group_type)

    if 'error' in result:
        return jsonify({"success": False, "error": result["error"]}), 500

    return jsonify({"success": True, "form_id": result["form_id"], "url": result["url"]}), 200

@forms_bp.route('/api/daily-check-in', methods=['POST'])
@login_required
def api_daily_check_in():
    """API endpoint to create a daily check-in form"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        return jsonify({"success": False, "error": "Google Forms connection required"}), 400

    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    recovery_type = data.get('recovery_type', 'general')

    # Create the form
    result = create_daily_check_in_form(forms_service, recovery_type)

    if 'error' in result:
        return jsonify({"success": False, "error": result["error"]}), 500

    return jsonify({"success": True, "form_id": result["form_id"], "url": result["url"]}), 200

@forms_bp.route('/api/analyze/<form_id>', methods=['GET'])
@login_required
def api_analyze(form_id):
    """API endpoint to analyze form responses"""
    forms_service = get_user_forms_connection()

    if not forms_service:
        return jsonify({"success": False, "error": "Google Forms connection required"}), 400

    # Analyze the responses
    analysis = analyze_form_responses(forms_service, form_id)

    if 'error' in analysis:
        return jsonify({"success": False, "error": analysis["error"]}), 500

    return jsonify({"success": True, "analysis": analysis}), 200