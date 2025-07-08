"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Chat Meet Commands Routes
Chat Meet Commands functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

chat_meet_commands_bp = Blueprint('chat_meet_commands', __name__)


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

Chat Command Handlers for Google Meet Features
==============================================

This module contains handlers for Google Meet-related chat commands.
It enables conversational access to the Google Meet features through the NOUS Assistant.

Usage:
    User: "Schedule a therapy session with Dr. Smith tomorrow at 3pm"
    Assistant: [Creates the meeting and responds with the details]
"""

import datetime
import re
import logging
from typing import Dict, List, Any, Optional, Tuple

from utils.meet_helper import (
    get_meet_service, create_meeting, get_meeting, update_meeting,
    delete_meeting, list_upcoming_meetings, create_therapy_session,
    create_recovery_group_meeting, create_mindfulness_session,
    create_sponsor_meeting, generate_meeting_agenda, analyze_meeting_notes
)
from utils.google_api_manager import get_user_connection
from utils.nlp_helper import extract_datetime, extract_duration, extract_emails

# Command patterns for Google Meet functionality
COMMAND_PATTERNS = {
    'create_meeting': [
        r'(?i)create (?:a )?(?:new )?meeting',
        r'(?i)schedule (?:a )?meeting',
        r'(?i)set up (?:a )?meeting',
        r'(?i)new meeting'
    ],
    'therapy_session': [
        r'(?i)create (?:a )?therapy session',
        r'(?i)schedule (?:a )?therapy session',
        r'(?i)new therapy session'
    ],
    'recovery_group': [
        r'(?i)create (?:a )?recovery (?:group )?meeting',
        r'(?i)schedule (?:a )?(?:new )?recovery group',
        r'(?i)new recovery group'
    ],
    'sponsor_meeting': [
        r'(?i)create (?:a )?sponsor meeting',
        r'(?i)schedule (?:a )?meeting with (?:my )?sponsor',
        r'(?i)new sponsor meeting'
    ],
    'mindfulness_session': [
        r'(?i)create (?:a )?mindfulness session',
        r'(?i)schedule (?:a )?mindfulness (?:session|practice)',
        r'(?i)new mindfulness session'
    ],
    'list_meetings': [
        r'(?i)list (?:my )?meetings',
        r'(?i)show (?:my )?meetings',
        r'(?i)upcoming meetings',
        r'(?i)what meetings do I have'
    ],
    'generate_agenda': [
        r'(?i)generate (?:an )?agenda',
        r'(?i)create (?:an )?agenda',
        r'(?i)make (?:an )?agenda'
    ],
    'analyze_notes': [
        r'(?i)analyze (?:meeting )?notes',
        r'(?i)process (?:meeting )?notes',
        r'(?i)extract (?:action items|key points) from (?:my )?notes'
    ]
}

def handle_meet_command(user_id: int, command: str) -> Dict[str, Any]:
    """
    Process a chat command related to Google Meet functionality

    Args:
        user_id: ID of the current user
        command: The chat command text from the user

    Returns:
        Response object with result and optional meeting details
    """
    # Identify the command type
    command_type = identify_command_type(command)

    if not command_type:
        return {
            'success': False,
            'message': "I'm not sure what kind of meeting you want to create. Please try again with more details."
        }

    # Get the user's Google Meet service connection
    connection = get_user_connection(user_id, 'google')
    if not connection:
        return {
            'success': False,
            'message': "You need to connect your Google account first. Go to Settings > Integrations to connect."
        }

    calendar_service = get_meet_service(connection)
    if not calendar_service:
        return {
            'success': False,
            'message': "There was an issue connecting to Google Calendar. Please try again later."
        }

    # Handle the specific command type
    if command_type == 'list_meetings':
        return handle_list_meetings(calendar_service, command)
    elif command_type == 'generate_agenda':
        return handle_generate_agenda(calendar_service, command)
    elif command_type == 'analyze_notes':
        return handle_analyze_notes(command)
    else:
        # For meeting creation commands
        return handle_create_meeting(calendar_service, command_type, command)

def identify_command_type(command: str) -> Optional[str]:
    """
    Identify the type of Google Meet command from the user's message

    Args:
        command: User's chat command text

    Returns:
        Command type identifier or None if not recognized
    """
    for cmd_type, patterns in COMMAND_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return cmd_type
    return None

def handle_create_meeting(calendar_service, command_type: str, command: str) -> Dict[str, Any]:
    """
    Handle commands to create different types of meetings

    Args:
        calendar_service: Google Calendar service object
        command_type: Type of meeting command
        command: Full user command text

    Returns:
        Response with meeting details
    """
    # Extract common meeting parameters from the command
    title, description = extract_title_description(command)
    start_time = extract_datetime(command)
    duration = extract_duration(command)
    attendees = extract_emails(command)

    # If no start time specified, default to tomorrow at current time
    if not start_time:
        start_time = datetime.datetime.now() + datetime.timedelta(days=1)
        start_time = start_time.replace(microsecond=0)

    # Create different meeting types
    if command_type == 'create_meeting':
        # For standard meetings
        if not title:
            title = "New Meeting"

        end_time = start_time + datetime.timedelta(minutes=duration or 60)
        result = create_meeting(
            calendar_service,
            title,
            description,
            start_time,
            end_time,
            attendees
        )

    elif command_type == 'therapy_session':
        # Extract therapy type
        session_type = extract_session_type(command)
        result = create_therapy_session(
            calendar_service,
            session_type or 'individual',
            attendees[0] if attendees else None,
            start_time,
            duration or 60
        )

    elif command_type == 'recovery_group':
        # Extract group type
        group_type = extract_group_type(command)
        is_recurring = 'weekly' in command.lower() or 'recurring' in command.lower()
        weekly_day = extract_weekly_day(command) if is_recurring else None

        result = create_recovery_group_meeting(
            calendar_service,
            group_type or 'aa',
            attendees,
            start_time,
            duration or 90,
            is_recurring,
            weekly_day
        )

    elif command_type == 'sponsor_meeting':
        # For sponsor meetings
        sponsor_email = attendees[0] if attendees else extract_sponsor_email(command)
        if not sponsor_email:
            return {
                'success': False,
                'message': "Please specify your sponsor's email address."
            }

        result = create_sponsor_meeting(
            calendar_service,
            sponsor_email,
            start_time,
            duration or 45
        )

    elif command_type == 'mindfulness_session':
        # Extract mindfulness type
        session_type = extract_mindfulness_type(command)
        result = create_mindfulness_session(
            calendar_service,
            session_type or 'meditation',
            attendees,
            start_time,
            duration or 30
        )

    # Handle result
    if 'error' in result:
        return {
            'success': False,
            'message': f"Sorry, I couldn't create the meeting: {result['error']}"
        }

    # Format a natural language response
    meeting_time = format_datetime(result['start_time'])

    return {
        'success': True,
        'message': f"I've created your {command_type.replace('_', ' ')} for {meeting_time}. You can join using the Meet link below.",
        'meeting': {
            'id': result['meeting_id'],
            'title': result['title'],
            'time': meeting_time,
            'link': result['meet_link']
        }
    }

def handle_list_meetings(calendar_service, command: str) -> Dict[str, Any]:
    """
    Handle commands to list upcoming meetings

    Args:
        calendar_service: Google Calendar service object
        command: Full user command text

    Returns:
        Response with list of meetings
    """
    # Determine how many meetings to show
    max_results = 5  # Default
    match = re.search(r'(?i)show (\d+)', command)
    if match:
        max_results = int(match.group(1))

    result = list_upcoming_meetings(calendar_service, max_results)

    if isinstance(result, dict) and 'error' in result:
        return {
            'success': False,
            'message': f"Sorry, I couldn't retrieve your meetings: {result['error']}"
        }

    if not result:
        return {
            'success': True,
            'message': "You don't have any upcoming meetings."
        }

    # Format meetings for display
    meetings_text = []
    for i, meeting in enumerate(result):
        meeting_time = format_datetime(meeting['start_time'])
        meetings_text.append(f"{i+1}. {meeting['title']} - {meeting_time}")

    return {
        'success': True,
        'message': "Here are your upcoming meetings:\n" + "\n".join(meetings_text),
        'meetings': result
    }

def handle_generate_agenda(calendar_service, command: str) -> Dict[str, Any]:
    """
    Handle commands to generate a meeting agenda

    Args:
        calendar_service: Google Calendar service object
        command: Full user command text

    Returns:
        Response with generated agenda
    """
    # Extract meeting_id if specified
    meeting_id = extract_meeting_id(command)

    # Extract meeting type and topic
    meeting_type = extract_meeting_type(command)
    topic = extract_topic(command)

    result = generate_meeting_agenda(
        calendar_service,
        meeting_id,
        meeting_type or 'general',
        topic
    )

    if 'error' in result:
        return {
            'success': False,
            'message': f"Sorry, I couldn't generate an agenda: {result['error']}"
        }

    return {
        'success': True,
        'message': f"I've generated an agenda for your {meeting_type or 'general'} meeting.",
        'agenda': result['agenda'],
        'meeting_info': result.get('meeting_info', {})
    }

def handle_analyze_notes(command: str) -> Dict[str, Any]:
    """
    Handle commands to analyze meeting notes

    Args:
        command: Full user command text

    Returns:
        Response with analysis results
    """
    # Extract notes text - for this functionality, usually the notes
    # would follow after the command, or be sent as a separate message
    notes_text = extract_notes_text(command)
    if not notes_text:
        return {
            'success': False,
            'message': "Please provide the meeting notes you want to analyze."
        }

    # Extract meeting type
    meeting_type = extract_meeting_type(command)

    result = analyze_meeting_notes(notes_text, meeting_type or 'general')

    if 'error' in result:
        return {
            'success': False,
            'message': f"Sorry, I couldn't analyze the notes: {result['error']}"
        }

    return {
        'success': True,
        'message': "I've analyzed your meeting notes. Here's what I found:",
        'analysis': result['analysis'],
        'meeting_type': result['meeting_type']
    }

# Helper functions to extract information from commands

def extract_title_description(command: str) -> Tuple[Optional[str], Optional[str]]:
    """Extract meeting title and description from command"""
    title = None
    description = None

    # Try to find "called X" or "titled X" patterns for title
    title_match = re.search(r'(?i)(?:called|titled|about|for|on)\s+["\']([^"\']+)["\']', command)
    if title_match:
        title = title_match.group(1)

    # If that fails, look for "about X" or similar patterns
    if not title:
        title_match = re.search(r'(?i)(?:called|titled|about|for|on)\s+([^,.]+)', command)
        if title_match:
            title = title_match.group(1).strip()

    # Check for description with "with description" pattern
    desc_match = re.search(r'(?i)with description ["\']([^"\']+)["\']', command)
    if desc_match:
        description = desc_match.group(1)

    return title, description

def extract_session_type(command: str) -> Optional[str]:
    """Extract therapy session type from command"""
    session_types = {
        'individual': ['individual', 'one-on-one', 'one on one', '1 on 1', '1-on-1'],
        'group': ['group', 'group therapy'],
        'cbt': ['cbt', 'cognitive behavioral', 'cognitive behaviour'],
        'dbt': ['dbt', 'dialectical', 'dialectic'],
        'trauma': ['trauma', 'trauma-focused', 'trauma focused'],
        'family': ['family', 'family therapy'],
        'assessment': ['assessment', 'evaluation', 'initial']
    }

    for session_type, patterns in session_types.items():
        for pattern in patterns:
            if pattern in command.lower():
                return session_type

    return None

def extract_group_type(command: str) -> Optional[str]:
    """Extract recovery group type from command"""
    group_types = {
        'aa': ['aa', 'alcoholics anonymous', 'alcohol'],
        'na': ['na', 'narcotics anonymous', 'narcotics'],
        'dbt': ['dbt', 'dialectical', 'dialectic'],
        'smart': ['smart', 'smart recovery'],
        'aca': ['aca', 'adult children', 'adult children of alcoholics'],
        'alanon': ['alanon', 'al-anon', 'al anon'],
        'oa': ['oa', 'overeaters', 'overeaters anonymous'],
        'ga': ['ga', 'gamblers', 'gamblers anonymous']
    }

    for group_type, patterns in group_types.items():
        for pattern in patterns:
            if pattern in command.lower():
                return group_type

    return None

def extract_mindfulness_type(command: str) -> Optional[str]:
    """Extract mindfulness session type from command"""
    mindfulness_types = {
        'meditation': ['meditation', 'guided meditation'],
        'breathing': ['breathing', 'breath', 'breathing exercise'],
        'yoga': ['yoga', 'gentle yoga'],
        'bodyScanning': ['body scan', 'body scanning'],
        'stressReduction': ['stress reduction', 'stress', 'mbsr'],
        'compassion': ['compassion', 'self-compassion', 'self compassion'],
        'awareness': ['awareness', 'mindful awareness']
    }

    for mindfulness_type, patterns in mindfulness_types.items():
        for pattern in patterns:
            if pattern in command.lower():
                return mindfulness_type

    return None

def extract_weekly_day(command: str) -> Optional[int]:
    """Extract day of week for recurring meetings"""
    days = {
        'monday': 0, 'mon': 0,
        'tuesday': 1, 'tue': 1, 'tues': 1,
        'wednesday': 2, 'wed': 2, 'weds': 2,
        'thursday': 3, 'thu': 3, 'thur': 3, 'thurs': 3,
        'friday': 4, 'fri': 4,
        'saturday': 5, 'sat': 5,
        'sunday': 6, 'sun': 6
    }

    for day_name, day_value in days.items():
        if day_name in command.lower():
            return day_value

    return None

def extract_sponsor_email(command: str) -> Optional[str]:
    """Extract sponsor email from command text"""
    # This is a simplified version, in reality you'd want to
    # check if the user has a sponsor in their profile
    email_match = re.search(r'[\w\.-]+@[\w\.-]+', command)
    if email_match:
        return email_match.group(0)
    return None

def extract_meeting_id(command: str) -> Optional[str]:
    """Extract meeting ID from command"""
    # This is simplified - in a real application, you might
    # ask the user to specify a meeting number from a list
    meeting_match = re.search(r'(?i)meeting (\d+)', command)
    if meeting_match:
        return meeting_match.group(1)
    return None

def extract_meeting_type(command: str) -> Optional[str]:
    """Extract meeting type from command"""
    meeting_types = {
        'general': ['general', 'regular', 'standard'],
        'therapy': ['therapy', 'therapeutic', 'clinical'],
        'recovery': ['recovery', 'aa', 'na', 'support group'],
        'sponsor': ['sponsor', 'sponsee'],
        'mindfulness': ['mindfulness', 'meditation', 'yoga']
    }

    for meeting_type, patterns in meeting_types.items():
        for pattern in patterns:
            if pattern in command.lower():
                return meeting_type

    return None

def extract_topic(command: str) -> Optional[str]:
    """Extract meeting topic from command"""
    topic_match = re.search(r'(?i)topic\s+["\']([^"\']+)["\']', command)
    if topic_match:
        return topic_match.group(1)

    topic_match = re.search(r'(?i)topic\s+([^,.]+)', command)
    if topic_match:
        return topic_match.group(1).strip()

    return None

def extract_notes_text(command: str) -> Optional[str]:
    """Extract notes text from command"""
    # In a real application, this would likely come from a separate message
    # or from a specific section of the command
    notes_match = re.search(r'(?i)notes:\s*(.+)', command, re.DOTALL)
    if notes_match:
        return notes_match.group(1).strip()
    return None

def format_datetime(dt_str: str) -> str:
    """Format a datetime string for display in chat"""
    try:
        dt = datetime.datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%A, %B %d at %I:%M %p')
    except (ValueError, TypeError):
        return dt_str