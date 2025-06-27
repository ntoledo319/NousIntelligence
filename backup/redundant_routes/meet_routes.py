"""
Google Meet routes
All routes are prefixed with /meet
"""

import os
import json
import datetime
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, session, current_app, abort, Response
from flask_login import login_required, current_user

# Import database from app_factory instead of app to avoid circular imports
from app_factory import db

# Import Meet helper
from utils.meet_helper import (
    get_meet_service, create_meeting, get_meeting, update_meeting,
    delete_meeting, list_upcoming_meetings, create_therapy_session,
    create_recovery_group_meeting, create_mindfulness_session,
    create_sponsor_meeting, generate_meeting_agenda, analyze_meeting_notes
)

# Import Google API manager for connection handling
from utils.google_api_manager import get_user_connection

# Create blueprint
meet_bp = Blueprint('meet', __name__, url_prefix='/meet')

# Helper to get user connection
def get_user_meet_connection():
    """Get user's Meet service connection"""
    if not current_user.is_authenticated:
        return None

    # Get the connection
    connection = get_user_connection(current_user.id, 'google')

    if not connection:
        return None

    # Get the service
    return get_meet_service(connection)

# Dashboard - Main page for Google Meet
@meet_bp.route('/')
@login_required
def dashboard():
    """Google Meet dashboard showing upcoming meetings"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    # Get upcoming meetings
    result = list_upcoming_meetings(calendar_service)

    if isinstance(result, dict) and 'error' in result:
        flash(f'Error fetching meetings: {result["error"]}', 'error')
        meetings = []
    else:
        meetings = result

    return render_template('meet/dashboard.html', meetings=meetings)

# Create standard meeting
@meet_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a standard Google Meet meeting"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        duration = int(request.form.get('duration', 60))
        attendees = request.form.get('attendees', '').split(',') if request.form.get('attendees') else None

        if not title:
            flash('Meeting title is required', 'error')
            return redirect(url_for('meet.create'))

        if not start_date or not start_time:
            flash('Meeting start date and time are required', 'error')
            return redirect(url_for('meet.create'))

        # Parse start date and time
        try:
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format', 'error')
            return redirect(url_for('meet.create'))

        # Calculate end time
        end_datetime = start_datetime + timedelta(minutes=duration)

        # Create the meeting
        result = create_meeting(
            calendar_service,
            title,
            description,
            start_datetime,
            end_datetime,
            attendees
        )

        if 'error' in result:
            flash(f'Error creating meeting: {result["error"]}', 'error')
            return redirect(url_for('meet.create'))

        flash('Meeting created successfully', 'success')
        return redirect(url_for('meet.view', meeting_id=result['meeting_id']))

    # GET request, render the form creation page
    return render_template('meet/create.html')

# View meeting details
@meet_bp.route('/view/<meeting_id>')
@login_required
def view(meeting_id):
    """View meeting details"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    # Get meeting details
    result = get_meeting(calendar_service, meeting_id)

    if 'error' in result:
        flash(f'Error fetching meeting: {result["error"]}', 'error')
        return redirect(url_for('meet.dashboard'))

    # Determine meeting type from title or description
    meeting_type = 'general'
    title_lower = result['title'].lower()
    description_lower = result.get('description', '').lower()

    if 'therapy' in title_lower or 'therapy' in description_lower:
        meeting_type = 'therapy'
    elif any(keyword in title_lower or keyword in description_lower for keyword in ['recovery', 'aa', 'na', 'support group']):
        meeting_type = 'recovery'
    elif 'sponsor' in title_lower or 'sponsor' in description_lower:
        meeting_type = 'sponsor'
    elif 'mindfulness' in title_lower or 'mindfulness' in description_lower:
        meeting_type = 'mindfulness'

    return render_template('meet/view.html', meeting=result, meeting_type=meeting_type)

# Edit meeting details
@meet_bp.route('/edit/<meeting_id>', methods=['GET', 'POST'])
@login_required
def edit(meeting_id):
    """Edit meeting details"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        duration = int(request.form.get('duration', 60))
        attendees = request.form.get('attendees', '').split(',') if request.form.get('attendees') else None

        if not title:
            flash('Meeting title is required', 'error')
            return redirect(url_for('meet.edit', meeting_id=meeting_id))

        if not start_date or not start_time:
            flash('Meeting start date and time are required', 'error')
            return redirect(url_for('meet.edit', meeting_id=meeting_id))

        # Parse start date and time
        try:
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format', 'error')
            return redirect(url_for('meet.edit', meeting_id=meeting_id))

        # Calculate end time
        end_datetime = start_datetime + timedelta(minutes=duration)

        # Update the meeting
        result = update_meeting(
            calendar_service,
            meeting_id,
            title,
            description,
            start_datetime,
            end_datetime,
            attendees
        )

        if 'error' in result:
            flash(f'Error updating meeting: {result["error"]}', 'error')
            return redirect(url_for('meet.edit', meeting_id=meeting_id))

        flash('Meeting updated successfully', 'success')
        return redirect(url_for('meet.view', meeting_id=meeting_id))

    # GET request, get meeting details and render form
    result = get_meeting(calendar_service, meeting_id)

    if 'error' in result:
        flash(f'Error fetching meeting: {result["error"]}', 'error')
        return redirect(url_for('meet.dashboard'))

    return render_template('meet/edit.html', meeting=result)

# Delete meeting
@meet_bp.route('/delete/<meeting_id>', methods=['POST'])
@login_required
def delete(meeting_id):
    """Delete a meeting"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    # Delete the meeting
    result = delete_meeting(calendar_service, meeting_id)

    if 'error' in result:
        flash(f'Error deleting meeting: {result["error"]}', 'error')
    else:
        flash('Meeting deleted successfully', 'success')

    return redirect(url_for('meet.dashboard'))

# Create therapy session
@meet_bp.route('/therapy-session', methods=['GET', 'POST'])
@login_required
def therapy_session():
    """Create a therapy session with Google Meet"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        session_type = request.form.get('session_type', 'individual')
        participant_email = request.form.get('participant_email')
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        duration = int(request.form.get('duration', 60))

        if not start_date or not start_time:
            flash('Session start date and time are required', 'error')
            return redirect(url_for('meet.therapy_session'))

        # Parse start date and time
        try:
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format', 'error')
            return redirect(url_for('meet.therapy_session'))

        # Create the therapy session
        result = create_therapy_session(
            calendar_service,
            session_type,
            participant_email,
            start_datetime,
            duration
        )

        if 'error' in result:
            flash(f'Error creating therapy session: {result["error"]}', 'error')
            return redirect(url_for('meet.therapy_session'))

        flash('Therapy session created successfully', 'success')
        return redirect(url_for('meet.view', meeting_id=result['meeting_id']))

    # GET request, render the form creation page
    return render_template('meet/therapy_session.html')

# Create recovery group meeting
@meet_bp.route('/recovery-group', methods=['GET', 'POST'])
@login_required
def recovery_group():
    """Create a recovery group meeting with Google Meet"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        group_type = request.form.get('group_type', 'aa')
        attendees = request.form.get('attendees', '').split(',') if request.form.get('attendees') else None
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        duration = int(request.form.get('duration', 90))
        is_recurring = 'is_recurring' in request.form
        weekly_day = int(request.form.get('weekly_day', 0)) if is_recurring else None

        if not start_date or not start_time:
            flash('Meeting start date and time are required', 'error')
            return redirect(url_for('meet.recovery_group'))

        # Parse start date and time
        try:
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format', 'error')
            return redirect(url_for('meet.recovery_group'))

        # Create the recovery group meeting
        result = create_recovery_group_meeting(
            calendar_service,
            group_type,
            attendees,
            start_datetime,
            duration,
            is_recurring,
            weekly_day
        )

        if 'error' in result:
            flash(f'Error creating recovery group meeting: {result["error"]}', 'error')
            return redirect(url_for('meet.recovery_group'))

        flash('Recovery group meeting created successfully', 'success')
        return redirect(url_for('meet.view', meeting_id=result['meeting_id']))

    # GET request, render the form creation page
    return render_template('meet/recovery_group.html')

# Create mindfulness session
@meet_bp.route('/mindfulness-session', methods=['GET', 'POST'])
@login_required
def mindfulness_session():
    """Create a mindfulness session with Google Meet"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        session_type = request.form.get('session_type', 'meditation')
        attendees = request.form.get('attendees', '').split(',') if request.form.get('attendees') else None
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        duration = int(request.form.get('duration', 30))

        if not start_date or not start_time:
            flash('Session start date and time are required', 'error')
            return redirect(url_for('meet.mindfulness_session'))

        # Parse start date and time
        try:
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format', 'error')
            return redirect(url_for('meet.mindfulness_session'))

        # Create the mindfulness session
        result = create_mindfulness_session(
            calendar_service,
            session_type,
            attendees,
            start_datetime,
            duration
        )

        if 'error' in result:
            flash(f'Error creating mindfulness session: {result["error"]}', 'error')
            return redirect(url_for('meet.mindfulness_session'))

        flash('Mindfulness session created successfully', 'success')
        return redirect(url_for('meet.view', meeting_id=result['meeting_id']))

    # GET request, render the form creation page
    return render_template('meet/mindfulness_session.html')

# Create sponsor meeting
@meet_bp.route('/sponsor-meeting', methods=['GET', 'POST'])
@login_required
def sponsor_meeting():
    """Create a sponsor meeting with Google Meet"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        sponsor_email = request.form.get('sponsor_email')
        start_date = request.form.get('start_date')
        start_time = request.form.get('start_time')
        duration = int(request.form.get('duration', 45))

        if not sponsor_email:
            flash('Sponsor email is required', 'error')
            return redirect(url_for('meet.sponsor_meeting'))

        if not start_date or not start_time:
            flash('Meeting start date and time are required', 'error')
            return redirect(url_for('meet.sponsor_meeting'))

        # Parse start date and time
        try:
            start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        except ValueError:
            flash('Invalid date or time format', 'error')
            return redirect(url_for('meet.sponsor_meeting'))

        # Create the sponsor meeting
        result = create_sponsor_meeting(
            calendar_service,
            sponsor_email,
            start_datetime,
            duration
        )

        if 'error' in result:
            flash(f'Error creating sponsor meeting: {result["error"]}', 'error')
            return redirect(url_for('meet.sponsor_meeting'))

        flash('Sponsor meeting created successfully', 'success')
        return redirect(url_for('meet.view', meeting_id=result['meeting_id']))

    # GET request, render the form creation page
    return render_template('meet/sponsor_meeting.html')

# Generate meeting agenda
@meet_bp.route('/generate-agenda', methods=['GET', 'POST'])
@login_required
def generate_agenda():
    """Generate an AI-powered agenda for a meeting"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    if request.method == 'POST':
        meeting_id = request.form.get('meeting_id')
        meeting_type = request.form.get('meeting_type', 'general')
        topic = request.form.get('topic')

        # Generate agenda
        result = generate_meeting_agenda(
            calendar_service,
            meeting_id,
            meeting_type,
            topic
        )

        if 'error' in result:
            flash(f'Error generating agenda: {result["error"]}', 'error')
            return redirect(url_for('meet.generate_agenda'))

        return render_template('meet/agenda_result.html', result=result)

    # GET request - show form
    # If meeting_id provided, pre-fill form
    meeting_id = request.args.get('meeting_id')
    meeting = None

    if meeting_id:
        result = get_meeting(calendar_service, meeting_id)
        if 'error' not in result:
            meeting = result

    # Get list of upcoming meetings for dropdown
    meetings = list_upcoming_meetings(calendar_service)
    if isinstance(meetings, dict) and 'error' in meetings:
        meetings = []

    return render_template('meet/generate_agenda.html', meeting=meeting, meetings=meetings)

# Analyze meeting notes
@meet_bp.route('/analyze-notes', methods=['GET', 'POST'])
@login_required
def analyze_notes():
    """Analyze meeting notes with AI"""
    if request.method == 'POST':
        notes_text = request.form.get('notes_text')
        meeting_type = request.form.get('meeting_type', 'general')

        if not notes_text:
            flash('Meeting notes are required', 'error')
            return redirect(url_for('meet.analyze_notes'))

        # Analyze notes
        result = analyze_meeting_notes(notes_text, meeting_type)

        if 'error' in result:
            flash(f'Error analyzing notes: {result["error"]}', 'error')
            return redirect(url_for('meet.analyze_notes'))

        return render_template('meet/analysis_result.html', result=result)

    # GET request - show form
    return render_template('meet/analyze_notes.html')

# Create notes for meeting
@meet_bp.route('/create-notes/<meeting_id>')
@login_required
def create_notes(meeting_id):
    """Create meeting notes template for a specific meeting"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    # Get meeting details
    result = get_meeting(calendar_service, meeting_id)

    if 'error' in result:
        flash(f'Error fetching meeting: {result["error"]}', 'error')
        return redirect(url_for('meet.dashboard'))

    # Determine meeting type from title or description
    meeting_type = 'general'
    title_lower = result['title'].lower()
    description_lower = result.get('description', '').lower()

    if 'therapy' in title_lower or 'therapy' in description_lower:
        meeting_type = 'therapy'
    elif any(keyword in title_lower or keyword in description_lower for keyword in ['recovery', 'aa', 'na', 'support group']):
        meeting_type = 'support_group'
    elif 'sponsor' in title_lower or 'sponsor' in description_lower:
        meeting_type = 'sponsor'

    # Get Google Docs service
    from utils.docs_sheets_helper import get_docs_service, create_meeting_notes_template
    docs_service = get_docs_service(get_user_connection(current_user.id, 'google'))

    if not docs_service:
        flash('Google Docs connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('meet.view', meeting_id=meeting_id))

    # Create meeting notes template
    notes_result = create_meeting_notes_template(docs_service, meeting_type)

    if isinstance(notes_result, dict) and 'error' in notes_result:
        flash(f'Error creating meeting notes: {notes_result["error"]}', 'error')
        return redirect(url_for('meet.view', meeting_id=meeting_id))

    flash('Meeting notes template created successfully', 'success')
    return redirect(notes_result['url'])

# Email participants
@meet_bp.route('/email-participants/<meeting_id>')
@login_required
def email_participants(meeting_id):
    """Send email to meeting participants"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        flash('Google Calendar connection required. Please connect your Google account first.', 'warning')
        return redirect(url_for('settings.index'))

    # Get meeting details
    result = get_meeting(calendar_service, meeting_id)

    if 'error' in result:
        flash(f'Error fetching meeting: {result["error"]}', 'error')
        return redirect(url_for('meet.dashboard'))

    # Redirect to Gmail compose with participants pre-filled
    attendees = []
    for attendee in result.get('event', {}).get('attendees', []):
        attendees.append(attendee.get('email'))

    if not attendees:
        flash('No participants found for this meeting', 'warning')
        return redirect(url_for('meet.view', meeting_id=meeting_id))

    to_emails = ','.join(attendees)
    subject = f"Regarding: {result['title']}"

    gmail_url = f"https://mail.google.com/mail/?view=cm&fs=1&to={to_emails}&su={subject}"

    return redirect(gmail_url)

# API routes for Meet
@meet_bp.route('/api/create', methods=['POST'])
@login_required
def api_create_meeting():
    """API endpoint to create a meeting"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        return jsonify({"success": False, "error": "Google Calendar connection required"}), 400

    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    title = data.get('title')
    description = data.get('description')

    if not title:
        return jsonify({"success": False, "error": "Meeting title is required"}), 400

    # Parse start and end times if provided
    start_time = None
    end_time = None

    if 'start_time' in data:
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid start time format"}), 400

    if 'end_time' in data:
        try:
            end_time = datetime.fromisoformat(data['end_time'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid end time format"}), 400

    # Get attendees if provided
    attendees = data.get('attendees')

    # Create the meeting
    result = create_meeting(calendar_service, title, description, start_time, end_time, attendees)

    if 'error' in result:
        return jsonify({"success": False, "error": result["error"]}), 500

    return jsonify({
        "success": True,
        "meeting_id": result["meeting_id"],
        "meet_link": result["meet_link"]
    }), 200

@meet_bp.route('/api/therapy-session', methods=['POST'])
@login_required
def api_therapy_session():
    """API endpoint to create a therapy session"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        return jsonify({"success": False, "error": "Google Calendar connection required"}), 400

    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    session_type = data.get('session_type', 'individual')
    participant_email = data.get('participant_email')

    # Parse start time if provided
    start_time = None
    if 'start_time' in data:
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid start time format"}), 400

    duration_minutes = data.get('duration_minutes', 60)

    # Create the therapy session
    result = create_therapy_session(
        calendar_service,
        session_type,
        participant_email,
        start_time,
        duration_minutes
    )

    if 'error' in result:
        return jsonify({"success": False, "error": result["error"]}), 500

    return jsonify({
        "success": True,
        "meeting_id": result["meeting_id"],
        "meet_link": result["meet_link"]
    }), 200

@meet_bp.route('/api/recovery-group', methods=['POST'])
@login_required
def api_recovery_group():
    """API endpoint to create a recovery group meeting"""
    calendar_service = get_user_meet_connection()

    if not calendar_service:
        return jsonify({"success": False, "error": "Google Calendar connection required"}), 400

    data = request.json
    if not data:
        return jsonify({"success": False, "error": "No data provided"}), 400

    group_type = data.get('group_type', 'aa')
    attendees = data.get('attendees')

    # Parse start time if provided
    start_time = None
    if 'start_time' in data:
        try:
            start_time = datetime.fromisoformat(data['start_time'].replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return jsonify({"success": False, "error": "Invalid start time format"}), 400

    duration_minutes = data.get('duration_minutes', 90)
    is_recurring = data.get('is_recurring', False)
    weekly_day = data.get('weekly_day') if is_recurring else None

    # Create the recovery group meeting
    result = create_recovery_group_meeting(
        calendar_service,
        group_type,
        attendees,
        start_time,
        duration_minutes,
        is_recurring,
        weekly_day
    )

    if 'error' in result:
        return jsonify({"success": False, "error": result["error"]}), 500

    return jsonify({
        "success": True,
        "meeting_id": result["meeting_id"],
        "meet_link": result["meet_link"]
    }), 200