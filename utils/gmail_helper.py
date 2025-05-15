import os
import logging
import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these SCOPES, delete your previously saved credentials
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service(user_connection):
    """Build and return a Gmail API service object from user connection data"""
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
        
        # Build the Gmail service
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        logging.error(f"Error building Gmail service: {str(e)}")
        return None

def get_gmail_messages(service, query="", max_results=20):
    """Get Gmail messages based on a query"""
    try:
        # List messages that match the query
        results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return []
            
        full_messages = []
        
        # Get each message's content
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            full_messages.append(msg)
            
        return full_messages
    except HttpError as error:
        logging.error(f"Gmail API error: {error}")
        return []
    except Exception as e:
        logging.error(f"Error retrieving Gmail messages: {str(e)}")
        return []

def get_message_content(message):
    """Extract the body content from a Gmail message"""
    try:
        payload = message.get('payload', {})
        parts = payload.get('parts', [])
        
        # If the message is multipart
        if parts:
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        return base64.urlsafe_b64decode(data).decode('utf-8')
                elif part.get('mimeType') == 'text/html':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        # Return HTML content if plain text not found
                        return base64.urlsafe_b64decode(data).decode('utf-8')
        
        # If the message is not multipart or no text parts found
        data = payload.get('body', {}).get('data', '')
        if data:
            return base64.urlsafe_b64decode(data).decode('utf-8')
            
        return "No readable content found in this message."
        
    except Exception as e:
        logging.error(f"Error extracting message content: {str(e)}")
        return f"Error retrieving message content: {str(e)}"

def get_message_headers(message):
    """Extract headers (From, To, Subject, Date) from a Gmail message"""
    headers = {}
    try:
        for header in message.get('payload', {}).get('headers', []):
            name = header.get('name', '').lower()
            if name in ['from', 'to', 'subject', 'date']:
                headers[name] = header.get('value', '')
        return headers
    except Exception as e:
        logging.error(f"Error extracting message headers: {str(e)}")
        return {}

def get_gmail_threads(service, query="", max_results=10, include_content=True):
    """Get Gmail threads based on a query, optionally with full message content"""
    try:
        # List threads that match the query
        results = service.users().threads().list(userId='me', q=query, maxResults=max_results).execute()
        threads = results.get('threads', [])
        
        if not threads:
            return []
            
        full_threads = []
        
        # Get each thread with its messages
        for thread in threads:
            thread_data = service.users().threads().get(userId='me', id=thread['id']).execute()
            
            # Process the thread into a more usable format
            processed_thread = {
                'id': thread_data['id'],
                'subject': '',  # Will be filled from first message
                'messages': [],
                'snippet': thread_data.get('snippet', ''),
                'history_id': thread_data.get('historyId', ''),
                'message_count': len(thread_data.get('messages', []))
            }
            
            # Process each message in the thread
            for message in thread_data.get('messages', []):
                headers = {}
                for header in message.get('payload', {}).get('headers', []):
                    name = header.get('name', '').lower()
                    if name in ['from', 'to', 'subject', 'date']:
                        headers[name] = header.get('value', '')
                
                # Set the thread subject from the first message if not already set
                if not processed_thread['subject'] and 'subject' in headers:
                    processed_thread['subject'] = headers['subject']
                
                msg_data = {
                    'id': message['id'],
                    'thread_id': message['threadId'],
                    'label_ids': message.get('labelIds', []),
                    'from': headers.get('from', ''),
                    'to': headers.get('to', ''),
                    'subject': headers.get('subject', ''),
                    'date': headers.get('date', ''),
                    'snippet': message.get('snippet', '')
                }
                
                # Include full message content if requested
                if include_content:
                    msg_data['content'] = get_message_content(message)
                
                processed_thread['messages'].append(msg_data)
            
            full_threads.append(processed_thread)
            
        return full_threads
        
    except HttpError as error:
        logging.error(f"Gmail API error: {error}")
        return []
    except Exception as e:
        logging.error(f"Error retrieving Gmail threads: {str(e)}")
        return []

def search_gmail(service, query, max_results=20):
    """Search Gmail with a specific query and return formatted results"""
    try:
        messages = get_gmail_messages(service, query, max_results)
        
        results = []
        for message in messages:
            headers = get_message_headers(message)
            content = get_message_content(message)
            
            results.append({
                'id': message['id'],
                'thread_id': message.get('threadId', ''),
                'from': headers.get('from', ''),
                'to': headers.get('to', ''),
                'subject': headers.get('subject', ''),
                'date': headers.get('date', ''),
                'snippet': message.get('snippet', ''),
                'content': content[:500] + '...' if len(content) > 500 else content  # Truncate long content
            })
            
        return results
    except Exception as e:
        logging.error(f"Error searching Gmail: {str(e)}")
        return []

def get_recent_emails(service, days=7, max_results=20):
    """Get emails from the past specified number of days"""
    try:
        # Calculate date for query
        date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        query = f"after:{date}"
        
        return search_gmail(service, query, max_results)
    except Exception as e:
        logging.error(f"Error getting recent emails: {str(e)}")
        return []

def get_unread_emails(service, max_results=20):
    """Get unread emails"""
    try:
        query = "is:unread"
        return search_gmail(service, query, max_results)
    except Exception as e:
        logging.error(f"Error getting unread emails: {str(e)}")
        return []

def get_important_emails(service, max_results=20):
    """Get important emails"""
    try:
        query = "is:important"
        return search_gmail(service, query, max_results)
    except Exception as e:
        logging.error(f"Error getting important emails: {str(e)}")
        return []

def analyze_email_volume(service, days=30):
    """Analyze email volume over a period"""
    try:
        # Calculate start date for analysis
        start_date = (datetime.now() - timedelta(days=days))
        
        # Get emails within the period
        date_string = start_date.strftime('%Y/%m/%d')
        query = f"after:{date_string}"
        
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        
        # If no messages found
        if not messages:
            return {
                'total_count': 0,
                'daily_average': 0,
                'by_weekday': {
                    'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 
                    'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0
                },
                'by_hour': {str(i): 0 for i in range(24)}
            }
        
        # Analyze timestamps of messages
        weekday_counts = {
            'Monday': 0, 'Tuesday': 0, 'Wednesday': 0, 
            'Thursday': 0, 'Friday': 0, 'Saturday': 0, 'Sunday': 0
        }
        hour_counts = {str(i): 0 for i in range(24)}
        
        for message_ref in messages[:100]:  # Limit to 100 messages for performance
            try:
                message = service.users().messages().get(userId='me', id=message_ref['id'], format='metadata').execute()
                
                # Get internal date (epoch ms) and convert to datetime
                internal_date = int(message.get('internalDate', 0)) / 1000  # Convert ms to seconds
                date = datetime.fromtimestamp(internal_date)
                
                # Count by weekday
                weekday = date.strftime('%A')
                weekday_counts[weekday] += 1
                
                # Count by hour
                hour = str(date.hour)
                hour_counts[hour] += 1
                
            except Exception as e:
                logging.warning(f"Error processing message in volume analysis: {str(e)}")
                continue
        
        # Calculate daily average
        daily_average = len(messages) / days
        
        return {
            'total_count': len(messages),
            'daily_average': round(daily_average, 1),
            'by_weekday': weekday_counts,
            'by_hour': hour_counts
        }
        
    except Exception as e:
        logging.error(f"Error analyzing email volume: {str(e)}")
        return {
            'error': str(e),
            'total_count': 0,
            'daily_average': 0
        }