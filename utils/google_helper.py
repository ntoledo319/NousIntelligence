from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
import gkeepapi
import logging

def get_google_flow(client_secrets_file, redirect_uri):
    """Create and return a Google OAuth flow"""
    scopes = [
        "https://www.googleapis.com/auth/calendar.events",
        "https://www.googleapis.com/auth/tasks",
        "https://www.googleapis.com/auth/keep"
    ]
    
    try:
        return Flow.from_client_secrets_file(
            client_secrets_file,
            scopes=scopes,
            redirect_uri=redirect_uri
        )
    except Exception as e:
        logging.error(f"Error creating Google flow: {str(e)}")
        raise Exception(f"Could not create Google auth flow: {str(e)}")

def build_google_services(session):
    """Build Google API service clients"""
    try:
        creds = Credentials(**session['google_creds'])
        calendar = build("calendar", "v3", credentials=creds)
        tasks = build("tasks", "v1", credentials=creds)
        
        # For Google Keep
        keep = gkeepapi.Keep()
        keep.login(session['google_creds']['client_id'], session['google_creds']['token'])
        
        return calendar, tasks, keep
    except Exception as e:
        logging.error(f"Error building Google services: {str(e)}")
        raise Exception(f"Could not connect to Google services: {str(e)}")

def create_calendar_event(calendar, summary, start_time, end_time=None, description=None):
    """Create a Google Calendar event"""
    if not end_time:
        # Default to 1 hour event if end time not specified
        end_time = start_time + datetime.timedelta(hours=1)
        
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time.isoformat()},
        "end": {"dateTime": end_time.isoformat()}
    }
    
    return calendar.events().insert(calendarId="primary", body=event).execute()

def get_todays_events(calendar):
    """Get all events for today"""
    now = datetime.date.today()
    time_min = f"{now.isoformat()}T00:00:00Z"
    time_max = f"{now.isoformat()}T23:59:59Z"
    
    events_result = calendar.events().list(
        calendarId="primary", 
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    
    return events_result.get("items", [])

def add_task(tasks, title, notes=None, due=None):
    """Add a task to Google Tasks"""
    task = {
        "title": title,
        "notes": notes
    }
    
    if due:
        task["due"] = due.isoformat() + "Z"  # RFC 3339 timestamp
        
    return tasks.tasks().insert(tasklist="@default", body=task).execute()

def add_note(keep, title, text):
    """Add a note to Google Keep"""
    gnote = keep.createNote(title, text)
    keep.sync()
    return gnote
