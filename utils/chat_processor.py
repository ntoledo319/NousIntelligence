"""
Chat Processor Module

This module processes user chat messages and handles integration with various services,
including Spotify music services.

@module utils.chat_processor
@description Process chat messages and handle service integrations
"""

import logging
import json
import os
import requests
import re
from typing import Dict, List, Any, Optional, Tuple
from flask import current_app, url_for, request

from utils.ai_helper import get_ai_helper
from utils.spotify_helper import get_spotify_client
from utils.spotify_ai_integration import get_spotify_ai
from utils.db_helpers import get_user_by_id

logger = logging.getLogger(__name__)

class ChatProcessor:
    """
    Process chat messages and handle integrations with various services
    """
    
    def __init__(self):
        """Initialize the chat processor"""
        self.logger = logging.getLogger(__name__)
        self.ai_helper = get_ai_helper()
        self.logger.info("Chat processor initialized")
    
    def process_message(self, message: str, user_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user message and generate a response with any actions
        
        Args:
            message: The user's message
            user_id: The user's ID
            session: The user's session data
            
        Returns:
            Dict containing the response and any additional data
        """
        self.logger.info(f"Processing message: {message[:50]}...")
        
        # Get user context
        context = self._get_user_context(user_id, session)
        
        # Process the message with AI helper
        ai_response = self.ai_helper.process_user_input(message, context)
        
        # Handle any actions
        action_results = self._process_actions(ai_response.get('actions', []), user_id, session)
        
        # Build the final response
        response = {
            'text': ai_response['text'],
            'intent': ai_response['detected_intent'],
            'action_results': action_results
        }
        
        # Update context with this interaction
        self._update_context(user_id, message, response)
        
        return response
    
    def _get_user_context(self, user_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get context for the current user
        
        Args:
            user_id: The user's ID
            session: The user's session data
            
        Returns:
            Dict containing user context
        """
        # Get Spotify connection status
        spotify_connected = 'spotify_token' in session
        
        # Build context
        context = {
            'user_id': user_id,
            'spotify_connected': spotify_connected
        }
        
        # Add Spotify context if connected
        if spotify_connected:
            spotify, _ = get_spotify_client(
                session, 
                os.environ.get("SPOTIFY_CLIENT_ID"),
                os.environ.get("SPOTIFY_CLIENT_SECRET"),
                os.environ.get("SPOTIFY_REDIRECT_URI"),
                user_id
            )
            
            if spotify:
                try:
                    # Get current playback state
                    playback = spotify.current_playback()
                    if playback and playback.get('item'):
                        context['spotify_current_track'] = {
                            'name': playback['item']['name'],
                            'artist': playback['item']['artists'][0]['name'],
                            'album': playback['item']['album']['name'],
                            'is_playing': playback['is_playing']
                        }
                except Exception as e:
                    self.logger.error(f"Error getting Spotify context: {str(e)}")
        
        return context
    
    def _process_actions(self, actions: List[Dict[str, Any]], user_id: str, session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process actions detected by the AI helper
        
        Args:
            actions: List of actions to process
            user_id: The user's ID
            session: The user's session data
            
        Returns:
            List of action results
        """
        results = []
        
        for action in actions:
            result = {
                'type': action['type'],
                'success': False,
                'message': "Action not processed"
            }
            
            # Handle Spotify-related actions
            if action['type'].startswith('spotify_'):
                result = self._process_spotify_action(action, user_id, session)
            
            # Handle Google Docs-related actions
            elif action['type'].startswith('google_docs_'):
                result = self._process_google_docs_action(action, user_id, session)
            
            # Handle Gmail-related actions
            elif action['type'].startswith('gmail_'):
                result = self._process_gmail_action(action, user_id, session)
            
            # Handle Google Calendar-related actions
            elif action['type'].startswith('calendar_'):
                result = self._process_calendar_action(action, user_id, session)
            
            # Handle Google Sheets-related actions
            elif action['type'].startswith('sheets_'):
                result = self._process_sheets_action(action, user_id, session)
            
            results.append(result)
        
        return results
    
    def _process_spotify_action(self, action: Dict[str, Any], user_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Spotify-related actions
        
        Args:
            action: The Spotify action to process
            user_id: The user's ID
            session: The user's session data
            
        Returns:
            Dict containing the result of the action
        """
        # Check if Spotify is connected
        if 'spotify_token' not in session:
            return {
                'type': action['type'],
                'success': False,
                'message': "Spotify is not connected. Please connect your Spotify account.",
                'connect_url': url_for('authorize_spotify')
            }
        
        # Get Spotify client
        spotify, _ = get_spotify_client(
            session, 
            os.environ.get("SPOTIFY_CLIENT_ID"),
            os.environ.get("SPOTIFY_CLIENT_SECRET"),
            os.environ.get("SPOTIFY_REDIRECT_URI"),
            user_id
        )
        
        if not spotify:
            return {
                'type': action['type'],
                'success': False,
                'message': "Could not establish Spotify connection."
            }
        
        # Execute the command through the API endpoint
        try:
            api_url = f"{request.host_url.rstrip('/')}/api/spotify/command/execute"
            headers = {'Content-Type': 'application/json'}
            response = requests.post(api_url, json=action, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                result['type'] = action['type']  # Ensure type is preserved
                return result
            else:
                error_msg = response.json().get('error', 'Unknown error')
                return {
                    'type': action['type'],
                    'success': False,
                    'message': f"Error executing Spotify command: {error_msg}"
                }
        except Exception as e:
            self.logger.error(f"Error processing Spotify action: {str(e)}")
            return {
                'type': action['type'],
                'success': False,
                'message': f"Error processing Spotify action: {str(e)}"
            }
    
    def _process_google_docs_action(self, action: Dict[str, Any], user_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Google Docs actions
        
        Args:
            action: The action to process
            user_id: The user's ID
            session: The user's session data
            
        Returns:
            Action result
        """
        from utils.google_api_manager import GoogleApiManager
        
        try:
            # Get user connection for Google API
            user = get_user_by_id(user_id)
            if not user or not user.google_connection:
                return {
                    'type': action['type'],
                    'success': False,
                    'message': "Google account not connected. Please connect your Google account first."
                }
                
            # Create API manager
            api_manager = GoogleApiManager(user.google_connection)
            docs_service = api_manager.get_service('docs')
            
            if not docs_service:
                return {
                    'type': action['type'],
                    'success': False,
                    'message': "Could not access Google Docs. Please check your Google account connection."
                }
            
            # Process different action types
            action_type = action['type']
            
            if action_type == 'google_docs_create':
                # Create a new document
                title = action.get('title', 'Untitled Document')
                document = api_manager.create_document(title)
                
                if 'error' in document:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error creating document: {document['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Created document '{title}'",
                    'document_id': document['document_id'],
                    'url': document['url']
                }
                
            elif action_type == 'google_docs_create_template':
                # Create a document from a template
                template = action.get('template', 'generic')
                
                if template == 'recovery_journal':
                    document = api_manager.create_recovery_journal_document()
                elif template == 'therapy_worksheet':
                    worksheet_type = action.get('worksheet_type', 'thought_record')
                    document = api_manager.create_therapy_worksheet(worksheet_type)
                elif template == 'meeting_notes':
                    meeting_type = action.get('meeting_type', 'support_group')
                    document = api_manager.create_meeting_notes_template(meeting_type)
                elif template == 'progress_tracking':
                    document = api_manager.create_progress_tracking_document()
                else:
                    # Default to blank document
                    document = api_manager.create_document(f"{template.capitalize()} Document")
                
                if 'error' in document:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error creating document template: {document['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Created {template.replace('_', ' ')} document",
                    'document_id': document['document_id'],
                    'url': document['url']
                }
                
            elif action_type == 'google_docs_edit':
                # Edit a document
                document_name = action.get('document_name', '')
                edit_request = action.get('edit_request', '')
                
                # Find the document by name
                documents = api_manager.list_documents(query=document_name)
                
                if not documents or 'error' in documents:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Could not find document '{document_name}'"
                    }
                    
                document_id = documents[0]['id']
                
                # Edit the document
                edit_result = api_manager.edit_document(document_id, edit_request)
                
                if 'error' in edit_result:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error editing document: {edit_result['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Edited document '{document_name}'",
                    'document_id': document_id
                }
                
            elif action_type == 'google_docs_summarize':
                # Summarize a document
                document_name = action.get('document_name', '')
                
                # Find the document by name
                documents = api_manager.list_documents(query=document_name)
                
                if not documents or 'error' in documents:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Could not find document '{document_name}'"
                    }
                    
                document_id = documents[0]['id']
                
                # Summarize the document
                summary_result = api_manager.summarize_document(document_id)
                
                if 'error' in summary_result:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error summarizing document: {summary_result['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': "Document summarized",
                    'summary': summary_result['summary']
                }
                
            elif action_type == 'google_docs_analyze':
                # Analyze a document
                document_name = action.get('document_name', '')
                
                # Find the document by name
                documents = api_manager.list_documents(query=document_name)
                
                if not documents or 'error' in documents:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Could not find document '{document_name}'"
                    }
                    
                document_id = documents[0]['id']
                
                # Analyze the document
                analysis_result = api_manager.analyze_document_sentiment(document_id)
                
                if 'error' in analysis_result:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error analyzing document: {analysis_result['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': "Document analyzed",
                    'analysis': analysis_result['sentiment_analysis']
                }
                
            elif action_type == 'google_docs_view':
                # View a document
                document_name = action.get('document_name', '')
                
                # Find the document by name
                documents = api_manager.list_documents(query=document_name)
                
                if not documents or 'error' in documents:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Could not find document '{document_name}'"
                    }
                    
                document_id = documents[0]['id']
                
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Opening document '{document_name}'",
                    'document_id': document_id,
                    'url': f"https://docs.google.com/document/d/{document_id}/edit"
                }
                
            else:
                return {
                    'type': action_type,
                    'success': False,
                    'message': f"Unknown Google Docs action: {action_type}"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing Google Docs action: {str(e)}")
            return {
                'type': action['type'],
                'success': False,
                'message': f"Error processing Google Docs action: {str(e)}"
            }
    
    def _process_gmail_action(self, action: Dict[str, Any], user_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Gmail actions
        
        Args:
            action: The action to process
            user_id: The user's ID
            session: The user's session data
            
        Returns:
            Action result
        """
        from utils.google_api_manager import GoogleApiManager
        
        try:
            # Get user connection for Google API
            user = get_user_by_id(user_id)
            if not user or not user.google_connection:
                return {
                    'type': action['type'],
                    'success': False,
                    'message': "Google account not connected. Please connect your Google account first."
                }
                
            # Create API manager
            api_manager = GoogleApiManager(user.google_connection)
            gmail_service = api_manager.get_service('gmail')
            
            if not gmail_service:
                return {
                    'type': action['type'],
                    'success': False,
                    'message': "Could not access Gmail. Please check your Google account connection."
                }
            
            # Process different action types
            action_type = action['type']
            
            if action_type == 'gmail_search':
                # Search for emails
                query = action.get('query', '')
                max_results = action.get('max_results', 10)
                
                emails = api_manager.search_emails(query, max_results)
                
                if 'error' in emails:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error searching emails: {emails['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Found {len(emails)} emails matching '{query}'",
                    'emails': emails
                }
                
            elif action_type == 'gmail_list_recent':
                # List recent emails
                emails = api_manager.search_emails("", 10)
                
                if 'error' in emails:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error retrieving recent emails: {emails['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Retrieved {len(emails)} recent emails",
                    'emails': emails
                }
                
            elif action_type == 'gmail_compose':
                # Compose an email
                recipient = action.get('recipient', '')
                subject = action.get('subject', '')
                
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Preparing email to {recipient}",
                    'compose_data': {
                        'to': recipient,
                        'subject': subject
                    }
                }
                
            elif action_type == 'gmail_reply':
                # Reply to an email
                email_id = action.get('email_id', '')
                
                if not email_id:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': "No email specified for reply"
                    }
                    
                # Generate AI reply
                reply = api_manager.generate_email_reply(email_id)
                
                if 'error' in reply:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error generating reply: {reply['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': "Generated email reply",
                    'reply_content': reply['reply_content'],
                    'email_id': email_id
                }
                
            elif action_type == 'gmail_categorize':
                # Categorize emails
                emails = api_manager.search_emails("", 20, include_content=True)
                
                if 'error' in emails:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error retrieving emails: {emails['error']}"
                    }
                    
                categorized_emails = api_manager.categorize_emails(emails)
                
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Categorized {len(categorized_emails)} emails",
                    'emails': categorized_emails
                }
                
            elif action_type == 'gmail_analyze':
                # Analyze emails
                emails = api_manager.search_emails("", 10, include_content=True)
                
                if 'error' in emails:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error retrieving emails: {emails['error']}"
                    }
                    
                analysis = api_manager.analyze_emails(emails)
                
                return {
                    'type': action_type,
                    'success': True,
                    'message': "Analyzed email content",
                    'analysis': analysis
                }
                
            elif action_type == 'gmail_filter_recovery':
                # Filter emails for recovery content
                days = action.get('days', 7)
                
                recovery_emails = api_manager.filter_recovery_emails(days)
                
                if 'error' in recovery_emails:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error filtering emails: {recovery_emails['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Found {len(recovery_emails)} recovery-relevant emails",
                    'emails': recovery_emails
                }
                
            elif action_type == 'gmail_create_template':
                # Create email template
                template = action.get('template', 'sponsor_check_in')
                
                templates = api_manager.create_support_network_templates()
                
                if 'error' in templates:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error creating templates: {templates['error']}"
                    }
                    
                if template not in templates['templates']:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Template '{template}' not found"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Created {template.replace('_', ' ')} template",
                    'template': templates['templates'][template]
                }
                
            else:
                return {
                    'type': action_type,
                    'success': False,
                    'message': f"Unknown Gmail action: {action_type}"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing Gmail action: {str(e)}")
            return {
                'type': action['type'],
                'success': False,
                'message': f"Error processing Gmail action: {str(e)}"
            }
    
    def _process_calendar_action(self, action: Dict[str, Any], user_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Google Calendar actions
        
        Args:
            action: The action to process
            user_id: The user's ID
            session: The user's session data
            
        Returns:
            Action result
        """
        from utils.google_api_manager import GoogleApiManager
        
        try:
            # Get user connection for Google API
            user = get_user_by_id(user_id)
            if not user or not user.google_connection:
                return {
                    'type': action['type'],
                    'success': False,
                    'message': "Google account not connected. Please connect your Google account first."
                }
                
            # Create API manager
            api_manager = GoogleApiManager(user.google_connection)
            calendar_service = api_manager.get_service('calendar')
            
            if not calendar_service:
                return {
                    'type': action['type'],
                    'success': False,
                    'message': "Could not access Google Calendar. Please check your Google account connection."
                }
            
            # Process different action types
            action_type = action['type']
            
            if action_type == 'calendar_view':
                # View calendar events
                period = action.get('period', 'today')
                
                events = api_manager.get_calendar_events(period)
                
                if 'error' in events:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error retrieving events: {events['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Retrieved {len(events)} events for {period}",
                    'events': events
                }
                
            elif action_type == 'calendar_create_event':
                # Create calendar event
                event_name = action.get('event_name', 'New Event')
                date = action.get('date', '')
                time = action.get('time', '')
                
                # Convert natural language date/time to datetime
                event_time = api_manager.parse_datetime(date, time)
                
                if 'error' in event_time:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error parsing date/time: {event_time['error']}"
                    }
                    
                # Create the event
                event = api_manager.create_calendar_event(event_name, event_time)
                
                if 'error' in event:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error creating event: {event['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Created event '{event_name}'",
                    'event_id': event['id'],
                    'event_link': event['htmlLink']
                }
                
            elif action_type == 'calendar_cancel_event':
                # Cancel/delete calendar event
                event_name = action.get('event_name', '')
                
                # Find the event by name
                events = api_manager.find_calendar_events(event_name)
                
                if 'error' in events:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error finding event: {events['error']}"
                    }
                    
                if not events:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Could not find event '{event_name}'"
                    }
                    
                # Cancel the event
                result = api_manager.delete_calendar_event(events[0]['id'])
                
                if 'error' in result:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error canceling event: {result['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Canceled event '{event_name}'"
                }
                
            else:
                return {
                    'type': action_type,
                    'success': False,
                    'message': f"Unknown Calendar action: {action_type}"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing Calendar action: {str(e)}")
            return {
                'type': action['type'],
                'success': False,
                'message': f"Error processing Calendar action: {str(e)}"
            }
    
    def _process_sheets_action(self, action: Dict[str, Any], user_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process Google Sheets actions
        
        Args:
            action: The action to process
            user_id: The user's ID
            session: The user's session data
            
        Returns:
            Action result
        """
        from utils.google_api_manager import GoogleApiManager
        
        try:
            # Get user connection for Google API
            user = get_user_by_id(user_id)
            if not user or not user.google_connection:
                return {
                    'type': action['type'],
                    'success': False,
                    'message': "Google account not connected. Please connect your Google account first."
                }
                
            # Create API manager
            api_manager = GoogleApiManager(user.google_connection)
            sheets_service = api_manager.get_service('sheets')
            
            if not sheets_service:
                return {
                    'type': action['type'],
                    'success': False,
                    'message': "Could not access Google Sheets. Please check your Google account connection."
                }
            
            # Process different action types
            action_type = action['type']
            
            if action_type == 'sheets_create':
                # Create a new spreadsheet
                title = action.get('title', 'Untitled Spreadsheet')
                
                spreadsheet = api_manager.create_spreadsheet(title)
                
                if 'error' in spreadsheet:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error creating spreadsheet: {spreadsheet['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Created spreadsheet '{title}'",
                    'spreadsheet_id': spreadsheet['spreadsheet_id'],
                    'url': spreadsheet['url']
                }
                
            elif action_type == 'sheets_create_template':
                # Create a spreadsheet from a template
                template = action.get('template', 'generic')
                
                if template == 'medication_tracker':
                    spreadsheet = api_manager.create_medication_tracker_spreadsheet()
                elif template == 'recovery_metrics':
                    spreadsheet = api_manager.create_recovery_metrics_dashboard()
                elif template == 'budget':
                    spreadsheet = api_manager.create_budget_spreadsheet()
                else:
                    # Default to blank spreadsheet
                    spreadsheet = api_manager.create_spreadsheet(f"{template.capitalize()} Spreadsheet")
                
                if 'error' in spreadsheet:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error creating spreadsheet template: {spreadsheet['error']}"
                    }
                    
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Created {template.replace('_', ' ')} spreadsheet",
                    'spreadsheet_id': spreadsheet['spreadsheet_id'],
                    'url': spreadsheet['url']
                }
                
            elif action_type == 'sheets_edit':
                # Open a spreadsheet for editing
                spreadsheet_name = action.get('spreadsheet_name', '')
                
                # Find the spreadsheet by name
                spreadsheets = api_manager.list_spreadsheets(query=spreadsheet_name)
                
                if not spreadsheets or 'error' in spreadsheets:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Could not find spreadsheet '{spreadsheet_name}'"
                    }
                    
                spreadsheet_id = spreadsheets[0]['id']
                
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Opening spreadsheet '{spreadsheet_name}' for editing",
                    'spreadsheet_id': spreadsheet_id,
                    'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
                }
                
            elif action_type == 'sheets_analyze':
                # Analyze a spreadsheet
                spreadsheet_name = action.get('spreadsheet_name', '')
                
                # Find the spreadsheet by name
                spreadsheets = api_manager.list_spreadsheets(query=spreadsheet_name)
                
                if not spreadsheets or 'error' in spreadsheets:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Could not find spreadsheet '{spreadsheet_name}'"
                    }
                    
                spreadsheet_id = spreadsheets[0]['id']
                
                # Get spreadsheet data
                spreadsheet_data = api_manager.get_spreadsheet_data(spreadsheet_id)
                
                if 'error' in spreadsheet_data:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Error getting spreadsheet data: {spreadsheet_data['error']}"
                    }
                    
                # Analyze the data
                analysis = api_manager.analyze_spreadsheet_data(spreadsheet_data)
                
                return {
                    'type': action_type,
                    'success': True,
                    'message': "Analyzed spreadsheet data",
                    'analysis': analysis
                }
                
            elif action_type == 'sheets_view':
                # View a spreadsheet
                spreadsheet_name = action.get('spreadsheet_name', '')
                
                # Find the spreadsheet by name
                spreadsheets = api_manager.list_spreadsheets(query=spreadsheet_name)
                
                if not spreadsheets or 'error' in spreadsheets:
                    return {
                        'type': action_type,
                        'success': False,
                        'message': f"Could not find spreadsheet '{spreadsheet_name}'"
                    }
                    
                spreadsheet_id = spreadsheets[0]['id']
                
                return {
                    'type': action_type,
                    'success': True,
                    'message': f"Opening spreadsheet '{spreadsheet_name}'",
                    'spreadsheet_id': spreadsheet_id,
                    'url': f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"
                }
                
            else:
                return {
                    'type': action_type,
                    'success': False,
                    'message': f"Unknown Sheets action: {action_type}"
                }
                
        except Exception as e:
            self.logger.error(f"Error processing Sheets action: {str(e)}")
            return {
                'type': action['type'],
                'success': False,
                'message': f"Error processing Sheets action: {str(e)}"
            }
    
    def _update_context(self, user_id: str, message: str, response: Dict[str, Any]) -> None:
        """
        Update user context with the current interaction
        
        Args:
            user_id: The user's ID
            message: The user's message
            response: The system's response
        """
        # This could store conversation history, update user preferences, etc.
        pass

# Create a singleton instance
chat_processor = ChatProcessor()

def get_chat_processor() -> ChatProcessor:
    """Get the singleton instance of ChatProcessor"""
    return chat_processor 