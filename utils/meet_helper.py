"""
Google Meet Integration Helper Module
====================================

This module provides utilities for integrating with Google Meet and Google Calendar APIs.
It enables creating, managing, and analyzing various types of meetings specifically tailored
for recovery and support purposes.

Key Features:
- Creating standard Google Meet meetings with all necessary parameters
- Specialized meeting creation for therapy sessions, recovery groups, sponsor meetings, and mindfulness sessions
- Meeting management (viewing, updating, deleting)
- AI-powered meeting agenda generation based on meeting type
- Meeting notes analysis for extracting key points and action items
- Utility functions for working with Google Calendar API

Usage Examples:
```python
# Create a standard meeting
result = create_meeting(
    calendar_service,
    "Weekly Check-in",
    "Regular team check-in meeting",
    start_datetime,
    end_datetime,
    ["participant@example.com"]
)

# Create a specialized therapy session
result = create_therapy_session(
    calendar_service,
    "client@example.com",
    session_type="cbt",
    start_time=tomorrow_6pm,
    duration_minutes=50
)

# Generate an AI-powered agenda
agenda = generate_meeting_agenda(
    calendar_service,
    meeting_id="abc123",
    meeting_type="recovery"
)

# Analyze meeting notes
analysis = analyze_meeting_notes(
    notes_text="Meeting notes content...",
    meeting_type="sponsor"
)
```

This module is part of the NOUS Assistant, supporting recovery and mental health
through integrated technology solutions.

@ai_prompt: "Create a function to integrate Google Meet with [therapy|recovery|mindfulness] sessions"
"""

import os
import logging
import uuid
import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from utils.ai_helper import generate_ai_text, analyze_document_content

def get_meet_service(user_connection):
    """
    Build and return a Google Calendar service for Meet operations

    Args:
        user_connection: User connection object with OAuth credentials

    Returns:
        Calendar service object or None
    """
    try:
        # Create credentials from stored tokens
        creds = Credentials(
            token=user_connection.token,
            refresh_token=user_connection.refresh_token,
            token_uri=user_connection.token_uri,
            client_id=user_connection.client_id,
            client_secret=user_connection.client_secret,
            scopes=user_connection.scopes.split(",") if user_connection.scopes else []
        )

        # Build the Calendar service (used for Meet operations)
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building Meet service: {str(e)}")
        return None

def create_meeting(calendar_service, title, description=None, start_time=None, end_time=None, attendees=None, is_recurring=False, recurrence_pattern=None):
    """
    Create a Google Meet meeting via Calendar API

    Args:
        calendar_service: Authorized Google Calendar service
        title: Meeting title
        description: Meeting description (optional)
        start_time: Meeting start time (datetime, default: now + 1 hour)
        end_time: Meeting end time (datetime, default: start_time + 1 hour)
        attendees: List of email addresses to invite (optional)
        is_recurring: Whether this is a recurring meeting (default: False)
        recurrence_pattern: Recurrence pattern for recurring meetings (optional)

    Returns:
        Meeting details including ID and join URL
    """
    try:
        # Set default start and end times if not provided
        if not start_time:
            start_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        if not end_time:
            end_time = start_time + datetime.timedelta(hours=1)

        # Format start/end times to RFC3339 format
        start_time_str = start_time.isoformat()
        end_time_str = end_time.isoformat()

        # Create event data
        event = {
            'summary': title,
            'description': description or '',
            'start': {
                'dateTime': start_time_str,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time_str,
                'timeZone': 'UTC',
            },
            'conferenceData': {
                'createRequest': {
                    'requestId': str(uuid.uuid4()),
                    'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                }
            }
        }

        # Add attendees if provided
        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        # Add recurrence if this is a recurring meeting
        if is_recurring and recurrence_pattern:
            event['recurrence'] = [recurrence_pattern]

        # Create the event with Google Meet details
        event = calendar_service.events().insert(
            calendarId='primary',
            body=event,
            conferenceDataVersion=1
        ).execute()

        # Extract meeting details
        meet_link = None
        for entry_point in event.get('conferenceData', {}).get('entryPoints', []):
            if entry_point.get('entryPointType') == 'video':
                meet_link = entry_point.get('uri')
                break

        return {
            'meeting_id': event['id'],
            'meet_link': meet_link,
            'title': event['summary'],
            'description': event.get('description', ''),
            'start_time': event['start']['dateTime'],
            'end_time': event['end']['dateTime'],
            'event': event
        }

    except Exception as e:
        logging.error(f"Error creating meeting: {str(e)}")
        return {'error': str(e)}

def get_meeting(calendar_service, event_id):
    """
    Get details of a Google Meet meeting by event ID

    Args:
        calendar_service: Authorized Google Calendar service
        event_id: Calendar event ID

    Returns:
        Meeting details
    """
    try:
        event = calendar_service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()

        # Extract meeting details
        meet_link = None
        for entry_point in event.get('conferenceData', {}).get('entryPoints', []):
            if entry_point.get('entryPointType') == 'video':
                meet_link = entry_point.get('uri')
                break

        return {
            'meeting_id': event['id'],
            'meet_link': meet_link,
            'title': event['summary'],
            'description': event.get('description', ''),
            'start_time': event['start']['dateTime'],
            'end_time': event['end']['dateTime'],
            'event': event
        }

    except Exception as e:
        logging.error(f"Error getting meeting: {str(e)}")
        return {'error': str(e)}

def update_meeting(calendar_service, event_id, title=None, description=None, start_time=None, end_time=None, attendees=None):
    """
    Update a Google Meet meeting

    Args:
        calendar_service: Authorized Google Calendar service
        event_id: Calendar event ID
        title: New meeting title (optional)
        description: New meeting description (optional)
        start_time: New meeting start time (datetime, optional)
        end_time: New meeting end time (datetime, optional)
        attendees: New list of email addresses to invite (optional)

    Returns:
        Updated meeting details
    """
    try:
        # Get the current event
        event = calendar_service.events().get(
            calendarId='primary',
            eventId=event_id
        ).execute()

        # Update fields if provided
        if title:
            event['summary'] = title

        if description:
            event['description'] = description

        if start_time:
            event['start']['dateTime'] = start_time.isoformat()

        if end_time:
            event['end']['dateTime'] = end_time.isoformat()

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]

        # Update the event
        updated_event = calendar_service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event,
            conferenceDataVersion=1
        ).execute()

        # Extract meeting details
        meet_link = None
        for entry_point in updated_event.get('conferenceData', {}).get('entryPoints', []):
            if entry_point.get('entryPointType') == 'video':
                meet_link = entry_point.get('uri')
                break

        return {
            'meeting_id': updated_event['id'],
            'meet_link': meet_link,
            'title': updated_event['summary'],
            'description': updated_event.get('description', ''),
            'start_time': updated_event['start']['dateTime'],
            'end_time': updated_event['end']['dateTime'],
            'event': updated_event
        }

    except Exception as e:
        logging.error(f"Error updating meeting: {str(e)}")
        return {'error': str(e)}

def delete_meeting(calendar_service, event_id):
    """
    Delete a Google Meet meeting

    Args:
        calendar_service: Authorized Google Calendar service
        event_id: Calendar event ID

    Returns:
        Success status
    """
    try:
        calendar_service.events().delete(
            calendarId='primary',
            eventId=event_id
        ).execute()

        return {'success': True}

    except Exception as e:
        logging.error(f"Error deleting meeting: {str(e)}")
        return {'error': str(e)}

def list_upcoming_meetings(calendar_service, max_results=10):
    """
    List upcoming meetings with Google Meet links

    Args:
        calendar_service: Authorized Google Calendar service
        max_results: Maximum number of meetings to return

    Returns:
        List of upcoming meetings
    """
    try:
        # Get current time in RFC3339 format
        now = datetime.datetime.utcnow().isoformat() + 'Z'

        # Get upcoming events
        events_result = calendar_service.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        # Filter and extract meetings with Google Meet links
        meetings = []
        for event in events:
            # Check if event has conference data
            if 'conferenceData' in event:
                # Extract meeting details
                meet_link = None
                for entry_point in event.get('conferenceData', {}).get('entryPoints', []):
                    if entry_point.get('entryPointType') == 'video':
                        meet_link = entry_point.get('uri')
                        break

                if meet_link:
                    meetings.append({
                        'meeting_id': event['id'],
                        'meet_link': meet_link,
                        'title': event['summary'],
                        'description': event.get('description', ''),
                        'start_time': event['start'].get('dateTime', event['start'].get('date')),
                        'end_time': event['end'].get('dateTime', event['end'].get('date')),
                    })

        return meetings

    except Exception as e:
        logging.error(f"Error listing meetings: {str(e)}")
        return {'error': str(e)}

def create_therapy_session(calendar_service, session_type, participant_email=None, start_time=None, duration_minutes=60):
    """
    Create a therapy session with Google Meet

    Args:
        calendar_service: Authorized Google Calendar service
        session_type: Type of therapy session (e.g., individual, group, etc.)
        participant_email: Email of the participant/client (optional)
        start_time: Session start time (datetime, default: tomorrow at current time)
        duration_minutes: Session duration in minutes (default: 60)

    Returns:
        Session details including Meet link
    """
    try:
        # Set default start time if not provided (tomorrow at current time)
        if not start_time:
            now = datetime.datetime.utcnow()
            start_time = datetime.datetime(
                now.year, now.month, now.day, now.hour, 0, 0
            ) + datetime.timedelta(days=1)

        # Calculate end time based on duration
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)

        # Create title and description based on session type
        title = f"Therapy Session - {session_type.capitalize()}"
        description = f"""
        This is a {session_type} therapy session.

        Guidelines for the session:
        - Please join a few minutes early to ensure your device is working properly
        - Find a quiet, private space for the session
        - Have a notebook or journal ready
        - If you need to cancel or reschedule, please do so at least 24 hours in advance

        Join URL: [This will be generated when the meeting is created]
        """

        # Create attendees list if participant email is provided
        attendees = [participant_email] if participant_email else None

        # Create the meeting
        meeting = create_meeting(
            calendar_service,
            title,
            description,
            start_time,
            end_time,
            attendees
        )

        # Update the description with the actual Meet link
        if 'error' not in meeting and meeting.get('meet_link'):
            description = description.replace(
                "Join URL: [This will be generated when the meeting is created]",
                f"Join URL: {meeting['meet_link']}"
            )

            # Update the meeting with the new description
            meeting = update_meeting(
                calendar_service,
                meeting['meeting_id'],
                description=description
            )

        return meeting

    except Exception as e:
        logging.error(f"Error creating therapy session: {str(e)}")
        return {'error': str(e)}

def create_recovery_group_meeting(calendar_service, group_type, attendees=None, start_time=None, duration_minutes=90, is_recurring=False, weekly_day=None):
    """
    Create a recovery group meeting with Google Meet

    Args:
        calendar_service: Authorized Google Calendar service
        group_type: Type of recovery group (e.g., AA, DBT, etc.)
        attendees: List of participant emails (optional)
        start_time: Meeting start time (datetime, default: tomorrow at 7 PM)
        duration_minutes: Meeting duration in minutes (default: 90)
        is_recurring: Whether this is a recurring meeting (default: False)
        weekly_day: Day of the week for recurring meetings (0-6 for Monday-Sunday)

    Returns:
        Meeting details including Meet link
    """
    try:
        # Set default start time if not provided (tomorrow at 7 PM)
        if not start_time:
            now = datetime.datetime.utcnow()
            start_time = datetime.datetime(
                now.year, now.month, now.day, 19, 0, 0
            ) + datetime.timedelta(days=1)

        # Calculate end time based on duration
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)

        # Create title and description based on group type
        title = f"{group_type.upper()} Recovery Group Meeting"
        description = f"""
        This is a {group_type.upper()} recovery group meeting.

        Guidelines for participants:
        - Please join a few minutes early
        - Find a quiet, private space for the meeting
        - Respect the confidentiality of all participants
        - Keep your comments focused on recovery
        - Practice active listening when others are sharing

        Join URL: [This will be generated when the meeting is created]
        """

        # Set recurrence pattern if this is a recurring meeting
        recurrence_pattern = None
        if is_recurring and weekly_day is not None:
            # RRULE format for weekly recurrence on specified day
            recurrence_pattern = f"RRULE:FREQ=WEEKLY;BYDAY={['MO','TU','WE','TH','FR','SA','SU'][weekly_day]}"

        # Create the meeting
        meeting = create_meeting(
            calendar_service,
            title,
            description,
            start_time,
            end_time,
            attendees,
            is_recurring,
            recurrence_pattern
        )

        # Update the description with the actual Meet link
        if 'error' not in meeting and meeting.get('meet_link'):
            description = description.replace(
                "Join URL: [This will be generated when the meeting is created]",
                f"Join URL: {meeting['meet_link']}"
            )

            # Update the meeting with the new description
            meeting = update_meeting(
                calendar_service,
                meeting['meeting_id'],
                description=description
            )

        return meeting

    except Exception as e:
        logging.error(f"Error creating recovery group meeting: {str(e)}")
        return {'error': str(e)}

def create_mindfulness_session(calendar_service, session_type, attendees=None, start_time=None, duration_minutes=30):
    """
    Create a mindfulness session with Google Meet

    Args:
        calendar_service: Authorized Google Calendar service
        session_type: Type of mindfulness session (e.g., meditation, breathing, etc.)
        attendees: List of participant emails (optional)
        start_time: Session start time (datetime, default: tomorrow at 8 AM)
        duration_minutes: Session duration in minutes (default: 30)

    Returns:
        Session details including Meet link
    """
    try:
        # Set default start time if not provided (tomorrow at 8 AM)
        if not start_time:
            now = datetime.datetime.utcnow()
            start_time = datetime.datetime(
                now.year, now.month, now.day, 8, 0, 0
            ) + datetime.timedelta(days=1)

        # Calculate end time based on duration
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)

        # Create title and description based on session type
        title = f"Mindfulness Session - {session_type.capitalize()}"
        description = f"""
        This is a guided {session_type} mindfulness session.

        Preparation tips:
        - Find a quiet, comfortable space
        - Wear comfortable clothing
        - Have a mat or cushion ready if needed
        - Turn off notifications during the session
        - Join a few minutes early to settle in

        Join URL: [This will be generated when the meeting is created]
        """

        # Create the meeting
        meeting = create_meeting(
            calendar_service,
            title,
            description,
            start_time,
            end_time,
            attendees
        )

        # Update the description with the actual Meet link
        if 'error' not in meeting and meeting.get('meet_link'):
            description = description.replace(
                "Join URL: [This will be generated when the meeting is created]",
                f"Join URL: {meeting['meet_link']}"
            )

            # Update the meeting with the new description
            meeting = update_meeting(
                calendar_service,
                meeting['meeting_id'],
                description=description
            )

        return meeting

    except Exception as e:
        logging.error(f"Error creating mindfulness session: {str(e)}")
        return {'error': str(e)}

def create_sponsor_meeting(calendar_service, sponsor_email, start_time=None, duration_minutes=45):
    """
    Create a sponsor meeting with Google Meet

    Args:
        calendar_service: Authorized Google Calendar service
        sponsor_email: Email of the sponsor/sponsee
        start_time: Meeting start time (datetime, default: tomorrow at current time)
        duration_minutes: Meeting duration in minutes (default: 45)

    Returns:
        Meeting details including Meet link
    """
    try:
        # Set default start time if not provided (tomorrow at current time)
        if not start_time:
            now = datetime.datetime.utcnow()
            start_time = datetime.datetime(
                now.year, now.month, now.day, now.hour, 0, 0
            ) + datetime.timedelta(days=1)

        # Calculate end time based on duration
        end_time = start_time + datetime.timedelta(minutes=duration_minutes)

        # Create title and description for sponsor meeting
        title = "Sponsor Meeting"
        description = f"""
        This is a sponsor meeting for recovery program support.

        Meeting Guidelines:
        - Please join a few minutes early to ensure your device is working properly
        - Find a quiet, private space for the meeting
        - Consider preparing specific topics or questions beforehand
        - Have your recovery materials ready for reference
        - Remember that this is a confidential conversation

        Join URL: [This will be generated when the meeting is created]
        """

        # Create attendees list with sponsor email
        attendees = [sponsor_email] if sponsor_email else None

        # Create the meeting
        meeting = create_meeting(
            calendar_service,
            title,
            description,
            start_time,
            end_time,
            attendees
        )

        # Update the description with the actual Meet link
        if 'error' not in meeting and meeting.get('meet_link'):
            description = description.replace(
                "Join URL: [This will be generated when the meeting is created]",
                f"Join URL: {meeting['meet_link']}"
            )

            # Update the meeting with the new description
            meeting = update_meeting(
                calendar_service,
                meeting['meeting_id'],
                description=description
            )

        return meeting

    except Exception as e:
        logging.error(f"Error creating sponsor meeting: {str(e)}")
        return {'error': str(e)}

def generate_meeting_agenda(calendar_service, meeting_id=None, meeting_type=None, topic=None):
    """
    Generate an AI-powered agenda for a meeting

    Args:
        calendar_service: Authorized Google Calendar service
        meeting_id: Calendar event ID (optional)
        meeting_type: Type of meeting (e.g., therapy, recovery, sponsor) if no meeting_id
        topic: General topic or focus of the meeting (optional)

    Returns:
        Generated agenda as formatted text
    """
    try:
        meeting_info = {}

        # If meeting_id is provided, get the meeting details
        if meeting_id:
            meeting_details = get_meeting(calendar_service, meeting_id)
            if 'error' in meeting_details:
                return {'error': meeting_details['error']}

            meeting_info = {
                'title': meeting_details.get('title', ''),
                'description': meeting_details.get('description', ''),
                'start_time': meeting_details.get('start_time', ''),
                'end_time': meeting_details.get('end_time', ''),
                'attendees': [a.get('email') for a in meeting_details.get('event', {}).get('attendees', [])]
            }

            # Try to determine meeting type from title
            if not meeting_type:
                title_lower = meeting_info['title'].lower()
                if 'therapy' in title_lower:
                    meeting_type = 'therapy'
                elif 'recovery' in title_lower or 'group' in title_lower:
                    meeting_type = 'recovery'
                elif 'sponsor' in title_lower:
                    meeting_type = 'sponsor'
                elif 'mindfulness' in title_lower:
                    meeting_type = 'mindfulness'
                else:
                    meeting_type = 'general'

        # Prepare context for AI prompt
        context = {
            'meeting_type': meeting_type or 'general',
            'topic': topic or '',
            'meeting_info': meeting_info
        }

        # Generate agenda based on meeting type
        agenda_prompt = f"""
        Generate a professional meeting agenda for a {context['meeting_type']} meeting
        """

        if context['topic']:
            agenda_prompt += f" focused on {context['topic']}"

        if context['meeting_info']:
            agenda_prompt += f"""
            Meeting title: {context['meeting_info'].get('title', 'N/A')}
            Start time: {context['meeting_info'].get('start_time', 'N/A')}
            Duration: {calculate_duration_minutes(context['meeting_info'].get('start_time'), context['meeting_info'].get('end_time'))} minutes
            """

        agenda_prompt += """
        The agenda should include:
        1. A welcome/introduction section
        2. Specific discussion topics
        3. Time allocations for each section
        4. Any necessary preparation notes
        5. Conclusion/next steps

        Format the agenda professionally with clear sections and formatting.
        """

        # Add specific guidance based on meeting type
        if meeting_type == 'therapy':
            agenda_prompt += """
            This is a therapy session, so include:
            - Check-in on current emotional state
            - Review of previous session's homework/goals
            - Main therapeutic discussion topics
            - Skills practice or intervention time
            - Homework/practice assignments
            - Scheduling next session
            """
        elif meeting_type == 'recovery':
            agenda_prompt += """
            This is a recovery group meeting, so include:
            - Opening readings or meditation
            - Check-ins from participants
            - Topic discussion related to recovery
            - Sharing time
            - Review of recovery principles
            - Closing remarks or readings
            """
        elif meeting_type == 'sponsor':
            agenda_prompt += """
            This is a sponsor meeting, so include:
            - Personal check-in (emotional, physical, spiritual state)
            - Recovery program work progress
            - Specific challenges or successes since last meeting
            - Questions or guidance needed
            - Action steps until next meeting
            """
        elif meeting_type == 'mindfulness':
            agenda_prompt += """
            This is a mindfulness session, so include:
            - Opening centering practice
            - Introduction to the mindfulness technique
            - Guided practice session
            - Reflection on experience
            - Discussion on incorporating practice into daily life
            - Closing practice
            """

        # Generate the agenda using AI
        agenda = generate_ai_text(agenda_prompt)

        return {
            'agenda': agenda,
            'meeting_type': meeting_type,
            'meeting_info': meeting_info
        }

    except Exception as e:
        logging.error(f"Error generating meeting agenda: {str(e)}")
        return {'error': str(e)}

def analyze_meeting_notes(notes_text, meeting_type=None):
    """
    Analyze meeting notes to extract key points, action items, and insights

    Args:
        notes_text: Text of the meeting notes to analyze
        meeting_type: Type of meeting (e.g., therapy, recovery, sponsor)

    Returns:
        Analysis results including key points, action items, and insights
    """
    try:
        # Prepare context for AI prompt
        context = {
            'meeting_type': meeting_type or 'general',
            'notes_text': notes_text
        }

        # Generate analysis prompt based on meeting type
        analysis_prompt = f"""
        Analyze the following {context['meeting_type']} meeting notes and extract:
        1. Key discussion points
        2. Action items and who is responsible
        3. Decisions made
        4. Important insights or takeaways
        5. Follow-up items for the next meeting

        Here are the notes:
        {context['notes_text']}

        Format your analysis with clear sections and bullet points.
        """

        # Add specific analysis guidance based on meeting type
        if meeting_type == 'therapy':
            analysis_prompt += """
            Also include:
            - Emotional themes identified
            - Therapeutic techniques used or discussed
            - Progress indicators
            - Areas for further exploration
            - Homework or practice assignments
            """
        elif meeting_type == 'recovery':
            analysis_prompt += """
            Also include:
            - Recovery principles discussed
            - Challenges identified by group members
            - Successful coping strategies shared
            - Resources mentioned
            - Group dynamics observations
            """
        elif meeting_type == 'sponsor':
            analysis_prompt += """
            Also include:
            - Recovery program steps discussed
            - Personal insights or revelations
            - Specific recovery challenges
            - Spiritual or emotional growth indicators
            - Commitments made
            """
        elif meeting_type == 'mindfulness':
            analysis_prompt += """
            Also include:
            - Mindfulness techniques practiced
            - Participant experiences and observations
            - Barriers to practice identified
            - Integration strategies discussed
            - Benefits noticed by participants
            """

        # Generate the analysis using AI
        analysis = generate_ai_text(analysis_prompt)

        return {
            'analysis': analysis,
            'meeting_type': meeting_type
        }

    except Exception as e:
        logging.error(f"Error analyzing meeting notes: {str(e)}")
        return {'error': str(e)}

def calculate_duration_minutes(start_time, end_time):
    """Helper function to calculate meeting duration in minutes"""
    if not start_time or not end_time:
        return 60  # Default duration

    try:
        # Parse ISO format strings to datetime objects
        if isinstance(start_time, str):
            start_dt = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        else:
            start_dt = start_time

        if isinstance(end_time, str):
            end_dt = datetime.datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            end_dt = end_time

        # Calculate duration in minutes
        duration = (end_dt - start_dt).total_seconds() / 60
        return int(duration)

    except Exception:
        return 60  # Default duration on error