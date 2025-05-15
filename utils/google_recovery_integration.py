"""
Google integration for recovery tools

This module provides integration between recovery features (AA, DBT, mindfulness)
and Google services like Calendar, Keep, and Tasks.
"""

import os
import logging
import json
import datetime
from datetime import datetime, timedelta

# Helper functions for Google integrations

def add_recovery_meeting_to_calendar(service, meeting_info):
    """
    Add an AA meeting to Google Calendar
    
    Args:
        service: Authorized Google Calendar service
        meeting_info: Dictionary with meeting details
            - name: Meeting name
            - location: Meeting location/address
            - start_time: Start time (datetime)
            - end_time: End time (datetime) or None
            - description: Additional notes/description
    
    Returns:
        Dictionary with event ID and link
    """
    try:
        if not service:
            return {"error": "Calendar service not available"}
            
        # If no end time is provided, assume 1 hour duration
        if not meeting_info.get('end_time') and meeting_info.get('start_time'):
            meeting_info['end_time'] = meeting_info['start_time'] + timedelta(hours=1)
            
        # Format event
        event = {
            'summary': meeting_info.get('name', 'Recovery Meeting'),
            'location': meeting_info.get('location', ''),
            'description': meeting_info.get('description', ''),
            'start': {
                'dateTime': meeting_info['start_time'].isoformat(),
                'timeZone': 'America/Los_Angeles',  # Default, could be made configurable
            },
            'end': {
                'dateTime': meeting_info['end_time'].isoformat(),
                'timeZone': 'America/Los_Angeles',  # Default, could be made configurable
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 30},
                    {'method': 'popup', 'minutes': 10},
                ],
            },
            'colorId': '9',  # Blue color for recovery events
        }
        
        # Insert event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            'id': created_event['id'],
            'link': created_event['htmlLink'],
            'success': True
        }
        
    except Exception as e:
        logging.error(f"Error adding meeting to calendar: {str(e)}")
        return {"error": str(e)}

def add_recovery_task(service, task_info):
    """
    Add a recovery-related task to Google Tasks
    
    Args:
        service: Authorized Google Tasks service
        task_info: Dictionary with task details
            - title: Task title
            - notes: Additional notes
            - due_date: Due date (datetime) or None
            - list_id: ID of the task list to add to (or None for default)
    
    Returns:
        Dictionary with task ID and success flag
    """
    try:
        if not service:
            return {"error": "Tasks service not available"}
            
        # Get the task list ID
        list_id = task_info.get('list_id')
        if not list_id:
            # Use the default task list
            task_lists = service.tasklists().list().execute()
            list_id = task_lists['items'][0]['id']  # Get first list
            
        # Format task
        task = {
            'title': task_info.get('title', 'Recovery Task'),
            'notes': task_info.get('notes', ''),
        }
        
        # Add due date if provided
        if task_info.get('due_date'):
            # Format as RFC 3339 timestamp
            due_date = task_info['due_date'].strftime('%Y-%m-%dT00:00:00Z')
            task['due'] = due_date
            
        # Insert task
        created_task = service.tasks().insert(tasklist=list_id, body=task).execute()
        
        return {
            'id': created_task['id'],
            'success': True
        }
        
    except Exception as e:
        logging.error(f"Error adding task: {str(e)}")
        return {"error": str(e)}

def create_recovery_journal_note(service, note_info):
    """
    Create a recovery journal entry in Google Keep
    
    Args:
        service: Authorized Google Keep service (gkeepapi instance)
        note_info: Dictionary with note details
            - title: Note title
            - text: Note text content
            - labels: List of labels to apply
            - color: Note color
    
    Returns:
        Dictionary with note ID and success flag
    """
    try:
        if not service:
            return {"error": "Keep service not available"}
            
        # Create a new note
        note = service.createNote(note_info.get('title', 'Recovery Journal Entry'))
        note.text = note_info.get('text', '')
        
        # Set color if provided
        if note_info.get('color'):
            note.color = note_info.get('color')
            
        # Add labels
        for label_name in note_info.get('labels', []):
            # Create label if it doesn't exist
            label = service.findLabel(label_name)
            if not label:
                label = service.createLabel(label_name)
            note.labels.add(label)
            
        # Save changes
        service.sync()
        
        return {
            'id': note.id,
            'success': True
        }
        
    except Exception as e:
        logging.error(f"Error creating Keep note: {str(e)}")
        return {"error": str(e)}

def add_medication_reminder_to_calendar(service, medication_info):
    """
    Add a medication reminder to Google Calendar
    
    Args:
        service: Authorized Google Calendar service
        medication_info: Dictionary with medication details
            - name: Medication name
            - dosage: Dosage information
            - time: Time to take (datetime)
            - frequency: How often to take ('daily', 'weekly', etc.)
            - end_date: When to stop reminders (datetime) or None
    
    Returns:
        Dictionary with event ID and link
    """
    try:
        if not service:
            return {"error": "Calendar service not available"}
            
        # Event time (default 15 min duration)
        start_time = medication_info.get('time')
        end_time = start_time + timedelta(minutes=15)
        
        # Format recurrence rule based on frequency
        recurrence = None
        if medication_info.get('frequency') == 'daily':
            # Daily recurrence
            recurrence = ['RRULE:FREQ=DAILY']
            
            # Add end date if provided
            if medication_info.get('end_date'):
                end_date_str = medication_info['end_date'].strftime('%Y%m%d')
                recurrence = [f'RRULE:FREQ=DAILY;UNTIL={end_date_str}']
                
        elif medication_info.get('frequency') == 'weekly':
            # Weekly recurrence on the same day of week
            day_of_week = start_time.strftime('%A')[:2].upper()
            recurrence = [f'RRULE:FREQ=WEEKLY;BYDAY={day_of_week}']
            
            # Add end date if provided
            if medication_info.get('end_date'):
                end_date_str = medication_info['end_date'].strftime('%Y%m%d')
                recurrence = [f'RRULE:FREQ=WEEKLY;BYDAY={day_of_week};UNTIL={end_date_str}']
                
        # Format event
        event = {
            'summary': f"Medication: {medication_info.get('name', 'Unknown')}",
            'description': (
                f"Dosage: {medication_info.get('dosage', 'As prescribed')}\n\n"
                "This is an automated medication reminder."
            ),
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'America/Los_Angeles',  # Default, could be made configurable
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'America/Los_Angeles',  # Default, could be made configurable
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 5},
                ],
            },
            'colorId': '10',  # Green color for medication events
        }
        
        # Add recurrence rule if applicable
        if recurrence:
            event['recurrence'] = recurrence
            
        # Insert event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            'id': created_event['id'],
            'link': created_event['htmlLink'],
            'success': True
        }
        
    except Exception as e:
        logging.error(f"Error adding medication reminder: {str(e)}")
        return {"error": str(e)}

def create_recurring_check_in_events(service, check_in_info):
    """
    Create recurring check-in events in Google Calendar
    
    Args:
        service: Authorized Google Calendar service
        check_in_info: Dictionary with check-in details
            - title: Event title
            - description: Event description
            - start_date: First check-in date (datetime)
            - time: Time of day (hours, minutes)
            - frequency: How often to repeat ('daily', 'weekly', 'monthly')
            - duration_minutes: Duration of check-in (int)
            - end_date: When to stop recurring (datetime) or None
    
    Returns:
        Dictionary with event ID and link
    """
    try:
        if not service:
            return {"error": "Calendar service not available"}
            
        # Combine date and time
        start_date = check_in_info.get('start_date')
        hours = check_in_info.get('time', {}).get('hours', 9)  # Default to 9 AM
        minutes = check_in_info.get('time', {}).get('minutes', 0)
        
        start_datetime = datetime(
            start_date.year, 
            start_date.month, 
            start_date.day, 
            hours, 
            minutes
        )
        
        # Calculate end time
        duration = check_in_info.get('duration_minutes', 30)  # Default 30 min
        end_datetime = start_datetime + timedelta(minutes=duration)
        
        # Format recurrence rule based on frequency
        recurrence = None
        frequency = check_in_info.get('frequency', 'daily')
        
        if frequency == 'daily':
            recurrence = ['RRULE:FREQ=DAILY']
        elif frequency == 'weekly':
            day_of_week = start_datetime.strftime('%A')[:2].upper()
            recurrence = [f'RRULE:FREQ=WEEKLY;BYDAY={day_of_week}']
        elif frequency == 'monthly':
            day = start_datetime.day
            recurrence = [f'RRULE:FREQ=MONTHLY;BYMONTHDAY={day}']
            
        # Add end date if provided
        if check_in_info.get('end_date') and recurrence:
            end_date_str = check_in_info['end_date'].strftime('%Y%m%d')
            recurrence_parts = recurrence[0].split(';')
            recurrence = [f"{';'.join(recurrence_parts)};UNTIL={end_date_str}"]
            
        # Format event
        event = {
            'summary': check_in_info.get('title', 'Recovery Check-in'),
            'description': check_in_info.get('description', 'Regular recovery check-in'),
            'start': {
                'dateTime': start_datetime.isoformat(),
                'timeZone': 'America/Los_Angeles',  # Default, could be made configurable
            },
            'end': {
                'dateTime': end_datetime.isoformat(),
                'timeZone': 'America/Los_Angeles',  # Default, could be made configurable
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 60},
                    {'method': 'popup', 'minutes': 15},
                ],
            },
            'colorId': '9',  # Blue color for recovery events
        }
        
        # Add recurrence rule if applicable
        if recurrence:
            event['recurrence'] = recurrence
            
        # Insert event
        created_event = service.events().insert(calendarId='primary', body=event).execute()
        
        return {
            'id': created_event['id'],
            'link': created_event['htmlLink'],
            'success': True
        }
        
    except Exception as e:
        logging.error(f"Error creating check-in events: {str(e)}")
        return {"error": str(e)}

def add_skill_practice_to_tasks(service, skill_info):
    """
    Add DBT skill practice reminders to Google Tasks
    
    Args:
        service: Authorized Google Tasks service
        skill_info: Dictionary with skill details
            - name: Skill name
            - description: Description/instructions
            - category: Skill category (optional)
            - frequency: How often to practice ('daily', 'weekly', etc.)
            - start_date: When to start practicing (datetime) or None
    
    Returns:
        Dictionary with task ID and success flag
    """
    try:
        if not service:
            return {"error": "Tasks service not available"}
            
        # Get the task list ID (use the default)
        task_lists = service.tasklists().list().execute()
        list_id = task_lists['items'][0]['id']  # Get first list
            
        # Format task title with category if available
        task_title = skill_info.get('name', 'Practice DBT Skill')
        if skill_info.get('category'):
            task_title = f"{skill_info['category']} Skill: {task_title}"
            
        # Format task
        task = {
            'title': task_title,
            'notes': skill_info.get('description', ''),
        }
        
        # Add due date if start date is provided
        if skill_info.get('start_date'):
            # Format as RFC 3339 timestamp
            due_date = skill_info['start_date'].strftime('%Y-%m-%dT00:00:00Z')
            task['due'] = due_date
            
        # Insert task
        created_task = service.tasks().insert(tasklist=list_id, body=task).execute()
        
        # For recurring tasks, we need to create multiple instances
        # since Google Tasks doesn't natively support recurrence
        if skill_info.get('frequency') == 'daily' and skill_info.get('start_date'):
            # Create tasks for the next 7 days as an example
            start_date = skill_info['start_date']
            
            for i in range(1, 8):  # 7 additional days
                next_date = start_date + timedelta(days=i)
                
                # Clone the task with new due date
                task['due'] = next_date.strftime('%Y-%m-%dT00:00:00Z')
                service.tasks().insert(tasklist=list_id, body=task).execute()
        
        return {
            'id': created_task['id'],
            'success': True
        }
        
    except Exception as e:
        logging.error(f"Error adding skill practice to tasks: {str(e)}")
        return {"error": str(e)}