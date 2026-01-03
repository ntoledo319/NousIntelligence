"""
Google Suite Client - Unified Google Services Integration
Consolidates Calendar, Tasks, Meet, and Gmail access
"""
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    logger.warning("Google client libraries not available")


class GoogleSuiteClient:
    """
    Unified client for all Google Suite services.
    Handles authentication, token refresh, and API calls.
    """
    
    def __init__(self, credentials: Optional[Dict[str, Any]] = None):
        """
        Initialize Google Suite client with user credentials.
        
        Args:
            credentials: OAuth2 credentials dict with token, refresh_token, etc.
        """
        if not GOOGLE_AVAILABLE:
            raise ImportError("Google client libraries required. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        
        self.credentials = None
        if credentials:
            self.credentials = Credentials(
                token=credentials.get('access_token'),
                refresh_token=credentials.get('refresh_token'),
                token_uri='https://oauth2.googleapis.com/token',
                client_id=credentials.get('client_id'),
                client_secret=credentials.get('client_secret')
            )
        
        self._calendar_service = None
        self._tasks_service = None
        self._gmail_service = None
    
    @property
    def calendar(self):
        """Get or create Calendar service"""
        if not self._calendar_service and self.credentials:
            self._calendar_service = build('calendar', 'v3', credentials=self.credentials)
        return self._calendar_service
    
    @property
    def tasks(self):
        """Get or create Tasks service"""
        if not self._tasks_service and self.credentials:
            self._tasks_service = build('tasks', 'v1', credentials=self.credentials)
        return self._tasks_service
    
    @property
    def gmail(self):
        """Get or create Gmail service"""
        if not self._gmail_service and self.credentials:
            self._gmail_service = build('gmail', 'v1', credentials=self.credentials)
        return self._gmail_service
    
    # ===== CALENDAR METHODS =====
    
    def list_calendars(self) -> List[Dict]:
        """List all calendars for the user"""
        try:
            calendar_list = self.calendar.calendarList().list().execute()
            return calendar_list.get('items', [])
        except HttpError as e:
            logger.error(f"Error listing calendars: {e}")
            return []
    
    def list_events(self, calendar_id: str = 'primary', 
                   time_min: Optional[datetime] = None,
                   time_max: Optional[datetime] = None,
                   max_results: int = 10) -> List[Dict]:
        """
        List events from a calendar.
        
        Args:
            calendar_id: Calendar ID (default: 'primary')
            time_min: Start time filter
            time_max: End time filter
            max_results: Maximum number of events
        """
        try:
            if not time_min:
                time_min = datetime.utcnow()
            
            events_result = self.calendar.events().list(
                calendarId=calendar_id,
                timeMin=time_min.isoformat() + 'Z',
                timeMax=time_max.isoformat() + 'Z' if time_max else None,
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            return events_result.get('items', [])
        except HttpError as e:
            logger.error(f"Error listing events: {e}")
            return []
    
    def create_event(self, summary: str, start_time: datetime, 
                    end_time: datetime, description: str = '',
                    calendar_id: str = 'primary') -> Optional[Dict]:
        """
        Create a calendar event.
        
        Args:
            summary: Event title
            start_time: Event start
            end_time: Event end
            description: Event description
            calendar_id: Calendar ID
        """
        try:
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
            }
            
            event = self.calendar.events().insert(
                calendarId=calendar_id,
                body=event
            ).execute()
            
            logger.info(f"Created event: {event.get('id')}")
            return event
        except HttpError as e:
            logger.error(f"Error creating event: {e}")
            return None
    
    def update_event(self, event_id: str, updates: Dict,
                    calendar_id: str = 'primary') -> Optional[Dict]:
        """Update an existing event"""
        try:
            # Get existing event
            event = self.calendar.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Apply updates
            event.update(updates)
            
            # Update event
            updated_event = self.calendar.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            return updated_event
        except HttpError as e:
            logger.error(f"Error updating event: {e}")
            return None
    
    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> bool:
        """Delete a calendar event"""
        try:
            self.calendar.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            logger.info(f"Deleted event: {event_id}")
            return True
        except HttpError as e:
            logger.error(f"Error deleting event: {e}")
            return False
    
    # ===== TASKS METHODS =====
    
    def list_task_lists(self) -> List[Dict]:
        """List all task lists"""
        try:
            results = self.tasks.tasklists().list().execute()
            return results.get('items', [])
        except HttpError as e:
            logger.error(f"Error listing task lists: {e}")
            return []
    
    def list_tasks(self, task_list_id: str = '@default') -> List[Dict]:
        """List tasks in a task list"""
        try:
            results = self.tasks.tasks().list(tasklist=task_list_id).execute()
            return results.get('items', [])
        except HttpError as e:
            logger.error(f"Error listing tasks: {e}")
            return []
    
    def create_task(self, title: str, notes: str = '',
                   due: Optional[datetime] = None,
                   task_list_id: str = '@default') -> Optional[Dict]:
        """Create a new task"""
        try:
            task = {
                'title': title,
                'notes': notes
            }
            
            if due:
                task['due'] = due.isoformat() + 'Z'
            
            result = self.tasks.tasks().insert(
                tasklist=task_list_id,
                body=task
            ).execute()
            
            logger.info(f"Created task: {result.get('id')}")
            return result
        except HttpError as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def update_task(self, task_id: str, updates: Dict,
                   task_list_id: str = '@default') -> Optional[Dict]:
        """Update an existing task"""
        try:
            # Get existing task
            task = self.tasks.tasks().get(
                tasklist=task_list_id,
                task=task_id
            ).execute()
            
            # Apply updates
            task.update(updates)
            
            # Update task
            result = self.tasks.tasks().update(
                tasklist=task_list_id,
                task=task_id,
                body=task
            ).execute()
            
            return result
        except HttpError as e:
            logger.error(f"Error updating task: {e}")
            return None
    
    def complete_task(self, task_id: str, task_list_id: str = '@default') -> bool:
        """Mark a task as completed"""
        try:
            updates = {'status': 'completed'}
            result = self.update_task(task_id, updates, task_list_id)
            return result is not None
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            return False
    
    def delete_task(self, task_id: str, task_list_id: str = '@default') -> bool:
        """Delete a task"""
        try:
            self.tasks.tasks().delete(
                tasklist=task_list_id,
                task=task_id
            ).execute()
            logger.info(f"Deleted task: {task_id}")
            return True
        except HttpError as e:
            logger.error(f"Error deleting task: {e}")
            return False
    
    # ===== MEET METHODS =====
    
    def create_meet_link(self, summary: str, start_time: datetime,
                        end_time: datetime) -> Optional[str]:
        """
        Create a Google Meet link by creating a calendar event with conference.
        
        Returns:
            Meet link URL or None
        """
        try:
            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"meet-{int(datetime.utcnow().timestamp())}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                }
            }
            
            event = self.calendar.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1
            ).execute()
            
            meet_link = event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri')
            return meet_link
        except HttpError as e:
            logger.error(f"Error creating Meet link: {e}")
            return None
    
    # ===== GMAIL METHODS (Optional) =====
    
    def send_email(self, to: str, subject: str, body: str) -> bool:
        """Send an email via Gmail API"""
        try:
            import base64
            from email.mime.text import MIMEText
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            
            self.gmail.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()
            
            logger.info(f"Sent email to {to}")
            return True
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
