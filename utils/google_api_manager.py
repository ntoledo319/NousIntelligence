"""
Google API Manager - Unified Google Services Integration
Handles all Google API interactions including OAuth, Calendar, Tasks, Drive, etc.
"""

import logging
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import requests
from authlib.integrations.flask_client import OAuth

logger = logging.getLogger(__name__)


class GoogleAPIManager:
    """Unified manager for all Google API services"""
    
    def __init__(self, app=None):
        self.app = app
        self.oauth = None
        self.client_config = None
        self.scopes = [
            'openid',
            'email',
            'profile',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/tasks',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/keep.readonly'
        ]
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app"""
        self.app = app
        self.oauth = OAuth(app)
        
        # Configure Google OAuth client
        self.client_config = {
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'server_metadata_url': 'https://accounts.google.com/.well-known/openid_configuration',
            'client_kwargs': {
                'scope': ' '.join(self.scopes),
                'prompt': 'consent'
            }
        }
    
    def get_user_connection(self, user_id):
        """Get authenticated Google API connection for user"""
        try:
            # This would normally retrieve stored OAuth tokens for the user
            # For now, return a mock connection that can be extended
            return {
                'user_id': user_id,
                'access_token': None,
                'refresh_token': None,
                'expires_at': None,
                'scopes': self.scopes
            }
        except Exception as e:
            logger.error(f"Failed to get user connection: {e}")
            return None
    
    def create_service(self, service_name, version='v1', user_connection=None):
        """Create a Google API service client"""
        try:
            if not user_connection or not user_connection.get('access_token'):
                logger.warning(f"No valid user connection for {service_name}")
                return None
                
            # This would create the actual service client
            # For now, return a mock service
            return {
                'service_name': service_name,
                'version': version,
                'authenticated': True
            }
        except Exception as e:
            logger.error(f"Failed to create {service_name} service: {e}")
            return None
    
    def get_oauth_client(self):
        """Get the OAuth client for authentication"""
        return getattr(self, 'google', None)
    
    def get_user_info(self, token):
        """Get user profile information"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                'https://www.googleapis.com/oauth2/v2/userinfo',
                headers=headers
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get user info: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return None
    
    def get_calendar_events(self, token, calendar_id='primary', time_min=None, time_max=None, max_results=10):
        """Get calendar events"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if time_min:
                params['timeMin'] = time_min
            if time_max:
                params['timeMax'] = time_max
                
            response = requests.get(
                f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events',
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get calendar events: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return None
    
    def create_calendar_event(self, token, event_data, calendar_id='primary'):
        """Create a calendar event"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events',
                headers=headers,
                json=event_data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to create calendar event: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return None
    
    def get_tasks(self, token, tasklist_id='@default', max_results=10):
        """Get tasks from Google Tasks"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {'maxResults': max_results}
            
            response = requests.get(
                f'https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks',
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get tasks: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting tasks: {str(e)}")
            return None
    
    def create_task(self, token, task_data, tasklist_id='@default'):
        """Create a task in Google Tasks"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f'https://www.googleapis.com/tasks/v1/lists/{tasklist_id}/tasks',
                headers=headers,
                json=task_data
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to create task: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return None


# Global instance for backward compatibility
google_api_manager = GoogleAPIManager()

def get_user_connection(user_id):
    """Get user's Google API connection - backward compatibility function"""
    return google_api_manager.get_user_connection(user_id)
    
    def get_calendar_events(self, token, calendar_id='primary', time_min=None, time_max=None, max_results=10):
        """Get calendar events"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            
            if time_min:
                params['timeMin'] = time_min
            if time_max:
                params['timeMax'] = time_max
            
            url = f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events'
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json().get('items', [])
            else:
                logger.error(f"Failed to get calendar events: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting calendar events: {str(e)}")
            return []
    
    def create_calendar_event(self, token, event_data, calendar_id='primary'):
        """Create a new calendar event"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            url = f'https://www.googleapis.com/calendar/v3/calendars/{calendar_id}/events'
            response = requests.post(url, headers=headers, json=event_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to create calendar event: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating calendar event: {str(e)}")
            return None
    
    def get_tasks(self, token, task_list='@default', max_results=10):
        """Get tasks from Google Tasks"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {'maxResults': max_results}
            
            url = f'https://www.googleapis.com/tasks/v1/lists/{task_list}/tasks'
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json().get('items', [])
            else:
                logger.error(f"Failed to get tasks: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting tasks: {str(e)}")
            return []
    
    def create_task(self, token, task_data, task_list='@default'):
        """Create a new task in Google Tasks"""
        try:
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            url = f'https://www.googleapis.com/tasks/v1/lists/{task_list}/tasks'
            response = requests.post(url, headers=headers, json=task_data)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to create task: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating task: {str(e)}")
            return None
    
    def get_drive_files(self, token, query=None, max_results=10):
        """Get files from Google Drive"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {
                'pageSize': max_results,
                'fields': 'files(id,name,mimeType,modifiedTime,size,webViewLink)'
            }
            
            if query:
                params['q'] = query
            
            url = 'https://www.googleapis.com/drive/v3/files'
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                return response.json().get('files', [])
            else:
                logger.error(f"Failed to get drive files: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting drive files: {str(e)}")
            return []
    
    def upload_to_drive(self, token, file_content, filename, mime_type='application/octet-stream'):
        """Upload a file to Google Drive"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            
            # Metadata
            metadata = {'name': filename}
            
            # Upload file
            files = {
                'data': ('metadata', json.dumps(metadata), 'application/json; charset=UTF-8'),
                'file': (filename, file_content, mime_type)
            }
            
            url = 'https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart'
            response = requests.post(url, headers=headers, files=files)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to upload to drive: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error uploading to drive: {str(e)}")
            return None
    
    def get_gmail_messages(self, token, query='', max_results=10):
        """Get Gmail messages"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            params = {
                'maxResults': max_results,
                'q': query
            }
            
            url = 'https://www.googleapis.com/gmail/v1/users/me/messages'
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                messages = response.json().get('messages', [])
                
                # Get detailed info for each message
                detailed_messages = []
                for message in messages[:5]:  # Limit to avoid rate limits
                    msg_url = f'https://www.googleapis.com/gmail/v1/users/me/messages/{message["id"]}'
                    msg_response = requests.get(msg_url, headers=headers)
                    if msg_response.status_code == 200:
                        detailed_messages.append(msg_response.json())
                
                return detailed_messages
            else:
                logger.error(f"Failed to get gmail messages: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting gmail messages: {str(e)}")
            return []
    
    def revoke_token(self, token):
        """Revoke an access token"""
        try:
            url = f'https://oauth2.googleapis.com/revoke?token={token}'
            response = requests.post(url)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
            return False
    
    def check_token_validity(self, token):
        """Check if a token is still valid"""
        try:
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get(
                'https://www.googleapis.com/oauth2/v1/tokeninfo',
                headers=headers
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error checking token validity: {str(e)}")
            return False


# Global instance
google_api_manager = GoogleAPIManager()


# Helper functions for backward compatibility
def get_google_oauth_client():
    """Get Google OAuth client"""
    return google_api_manager.get_oauth_client()


def get_user_profile(token):
    """Get user profile from Google"""
    return google_api_manager.get_user_info(token)


def get_calendar_events(token, **kwargs):
    """Get calendar events"""
    return google_api_manager.get_calendar_events(token, **kwargs)


def create_calendar_event(token, event_data):
    """Create calendar event"""
    return google_api_manager.create_calendar_event(token, event_data)


def get_user_tasks(token, **kwargs):
    """Get user tasks"""
    return google_api_manager.get_tasks(token, **kwargs)


def create_user_task(token, task_data):
    """Create user task"""
    return google_api_manager.create_task(token, task_data)


class GoogleHelper:
    """Legacy compatibility class"""
    
    def __init__(self):
        self.api_manager = google_api_manager
    
    def __getattr__(self, name):
        return getattr(self.api_manager, name)


# Initialize with app context if available
def init_google_services(app):
    """Initialize Google services with Flask app"""
    google_api_manager.init_app(app)
    return google_api_manager