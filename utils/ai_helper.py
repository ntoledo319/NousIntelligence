"""
AI Helper Utility

This module provides AI functionality for the NOUS personal assistant.
It handles natural language processing, command parsing, and AI-powered responses.

@module utils.ai_helper
@description Core AI functionality for the personal assistant
"""

import logging
import re
import os
from typing import Dict, List, Any, Optional, Tuple
import json
import time
import openai
from utils.settings import get_setting

logger = logging.getLogger(__name__)

# Configure OpenAI API key from settings
OPENAI_KEY = get_setting("openai_api_key", "")
if not OPENAI_KEY:
    OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "")

# Initialize OpenAI client if key is available
openai_client = None
if OPENAI_KEY:
    # Just set the API key but don't create client yet - will be created on demand
    openai.api_key = OPENAI_KEY
    try:
        # Create OpenAI client without proxies argument
        openai_client = openai.OpenAI(api_key=OPENAI_KEY)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        # Fallback to older API if needed
        try:
            openai_client = None
            # Just use the API key for legacy client
        except Exception as e2:
            logger.error(f"Failed to initialize fallback OpenAI client: {e2}")


def get_ai_response(prompt: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Get AI-generated response for the user's prompt
    
    Args:
        prompt: The user's text prompt
        conversation_history: Optional list of previous messages for context
        
    Returns:
        AI-generated response text
    """
    # For now, we'll use a simple rule-based approach 
    # to ensure the app runs without OpenAI API dependencies
    
    # If no conversation history provided, create a new one
    if conversation_history is None:
        conversation_history = []
    
    # Basic responses for common queries
    responses = {
        "hello": "Hello! I'm NOUS, your personal assistant. How can I help you today?",
        "hi": "Hi there! How can I assist you?",
        "how are you": "I'm functioning well, thank you for asking! How can I help you?",
        "what can you do": "I can help with tasks like setting reminders, checking weather, playing music, and more. I can also assist with voice commands once the interface is fully set up.",
        "help": "I'm NOUS, your personal assistant. I can help with tasks, answer questions, and provide assistance through both text and voice interfaces.",
    }
    
    # Check for voice-related queries
    voice_keywords = ["voice", "speak", "talk", "listen", "whisper", "speech", "audio"]
    for keyword in voice_keywords:
        if keyword in prompt.lower():
            return "I'm equipped with a voice interface that uses Whisper for speech recognition and can respond using text-to-speech. You can speak commands, ask questions, or have me read text aloud."
    
    # Look for exact matches in our basic responses
    prompt_lower = prompt.lower()
    for key, response in responses.items():
        if key in prompt_lower:
            return response
    
    # Default response if no patterns match
    return "I'm here to assist you. You can ask me questions or give me tasks to help with. I'm also equipped with voice recognition capabilities for hands-free interaction."

# Rate limiting tracker
class RateLimitTracker:
    def __init__(self):
        self.requests = []
        self.max_requests_per_minute = 20  # Adjust based on your tier
        self.window_seconds = 60
        
    def can_make_request(self):
        """Check if we can make a request within rate limits"""
        now = time.time()
        # Remove requests older than our window
        self.requests = [t for t in self.requests if now - t < self.window_seconds]
        
        return len(self.requests) < self.max_requests_per_minute
        
    def add_request(self):
        """Record a request"""
        self.requests.append(time.time())

# Create a rate limit tracker instance
rate_limiter = RateLimitTracker()

class AIHelper:
    """
    Provides AI functionality for the NOUS personal assistant
    """
    
    def __init__(self):
        """Initialize the AI helper"""
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing AI Helper")
        
        # Intent patterns for more accurate detection
        self.intent_patterns = {
            'music': [
                # General music commands
                r'\b(?:play|listen to|hear|find|search for)\b.+\b(?:song|track|music|artist|album|playlist)\b',
                r'\b(?:pause|stop|resume|skip|next|previous)\b.+\b(?:music|song|track|playback)\b',
                # Spotify-specific commands
                r'\bspotify\b',
                r'\bconnect.+spotify\b',
                r'\bplay.+on spotify\b',
                r'\b(?:recommendation|recommend).+(?:song|track|artist|album|playlist)\b',
                r'\bcreate.+playlist\b',
                r'\b(?:what|who).+(?:playing|listening to)\b',
                # Mood-based music commands
                r'\b(?:play|find|recommend).+(?:music|songs|tracks).+(?:for|when|while|during).+(?:feeling|mood|activity)\b',
                r'\b(?:happy|sad|relaxed|energetic|workout|study|focus|party|chill).+music\b',
                # Music discovery
                r'\bfind.+(?:new|similar).+(?:music|artists|songs)\b',
                r'\bdiscover.+music\b',
                # Music analysis
                r'\banalyze.+(?:music|song|track|listening)\b',
                r'\bmusic taste\b',
                r'\bwhat.+(?:genre|mood|bpm|key)\b'
            ],
            'weather': [
                r'\b(?:weather|temperature|forecast|rain|snow|humidity|wind|storm)\b',
                r'\bhow.+(?:weather|temperature)\b',
                r'\bweather.+(?:today|tomorrow|this week)\b'
            ],
            'task': [
                r'\b(?:task|todo|reminder|note|list)\b',
                r'\b(?:add|create|make|set).+(?:task|todo|reminder|note)\b',
                r'\b(?:remind me|remember)\b'
            ],
            'appointment': [
                r'\b(?:appointment|schedule|calendar|meeting|event)\b',
                r'\b(?:book|schedule|set up).+(?:appointment|meeting|call|event)\b',
                r'\bwhen.+(?:appointment|meeting|event)\b'
            ],
            'google_docs': [
                r'\b(?:google\s+doc|document|gdoc)\b',
                r'\b(?:create|edit|open|show|view|summarize).+(?:document|doc|gdoc)\b',
                r'\b(?:document|doc|gdoc).+(?:content|summary|analysis)\b',
                r'\b(?:recovery journal|therapy worksheet|meeting notes).+(?:template|doc|document)\b',
                r'\b(?:journal|worksheet|progress\s+tracking)\b'
            ],
            'google_sheets': [
                r'\b(?:google\s+sheet|spreadsheet|gsheet)\b',
                r'\b(?:create|edit|open|show|view|analyze).+(?:spreadsheet|sheet|gsheet)\b',
                r'\b(?:spreadsheet|sheet|gsheet).+(?:content|summary|analysis)\b',
                r'\b(?:budget|medication|tracker|tracking)\b',
                r'\b(?:recovery metrics|metrics dashboard)\b'
            ],
            'gmail': [
                r'\b(?:gmail|email|mail)\b',
                r'\b(?:check|read|show|view|search).+(?:email|mail|gmail)\b',
                r'\b(?:send|compose|draft|reply).+(?:email|mail|gmail)\b',
                r'\b(?:email|mail|gmail).+(?:digest|summary|analysis)\b',
                r'\b(?:recovery email|support network email)\b',
                r'\b(?:email template|email recovery)\b'
            ],
            'google_calendar': [
                r'\b(?:google\s+calendar|gcal|calendar)\b',
                r'\b(?:create|add|schedule|book).+(?:event|appointment|meeting|calendar)\b',
                r'\b(?:show|view|check|what).+(?:calendar|schedule|upcoming|events)\b',
                r'\b(?:when|time).+(?:event|appointment|meeting)\b',
                r'\b(?:recovery meeting|support group meeting|therapy appointment)\b'
            ]
        }
        
        # Spotify-specific entity extractors
        self.spotify_entity_patterns = {
            'track': [
                r'(?:play|find|recommend).+(?:song|track) ["\']?([^"\']+)["\']?',
                r'(?:play|find|recommend) ["\']?([^"\']+)["\']? (?:song|track)'
            ],
            'artist': [
                r'(?:play|find|recommend).+(?:artist|band|musician) ["\']?([^"\']+)["\']?',
                r'(?:play|find|recommend).+(?:songs|music|tracks) (?:by|from) ["\']?([^"\']+)["\']?'
            ],
            'album': [
                r'(?:play|find|recommend).+album ["\']?([^"\']+)["\']?',
                r'(?:play|find|recommend) ["\']?([^"\']+)["\']? album'
            ],
            'playlist': [
                r'(?:play|find|recommend).+playlist ["\']?([^"\']+)["\']?',
                r'(?:play|find|recommend) ["\']?([^"\']+)["\']? playlist',
                r'(?:create|make).+playlist (?:called|named) ["\']?([^"\']+)["\']?'
            ],
            'mood': [
                r'(?:play|find|recommend).+(?:music|songs|tracks) (?:for|when|while) (?:feeling|mood) ["\']?([^"\']+)["\']?',
                r'(?:play|find|recommend) ["\']?([^"\']+)["\']? (?:music|songs|tracks)',
                r'(?:I\'m feeling|I feel) ([a-zA-Z]+)'
            ],
            'activity': [
                r'(?:play|find|recommend).+(?:music|songs|tracks) (?:for|during|while) ([^"\']+)',
                r'(?:music|songs|tracks) (?:for|during|while) ([^"\']+)'
            ],
            'command': [
                r'^(play|pause|resume|stop|skip|next|previous|volume|shuffle|repeat)$'
            ]
        }
        
        # Google Docs entity extractors
        self.google_docs_entity_patterns = {
            'document_name': [
                r'(?:create|edit|open|find|show).+(?:document|doc|gdoc) ["\']?([^"\']+)["\']?',
                r'(?:document|doc|gdoc) (?:called|named|titled) ["\']?([^"\']+)["\']?'
            ],
            'document_id': [
                r'document (?:id|ID) ["\']?([^"\']+)["\']?',
                r'doc (?:id|ID) ["\']?([^"\']+)["\']?'
            ],
            'edit_request': [
                r'(?:edit|update|change|modify) .+(?:to|with) ["\']?([^"\']+)["\']?'
            ],
            'template_type': [
                r'(?:journal|therapy worksheet|meeting notes|recovery) (?:template|document) (?:for|about|on) ["\']?([^"\']+)["\']?',
                r'(?:create|make) (?:a|an) ([^"\']+) (?:template|document|worksheet)'
            ],
            'action': [
                r'(create|edit|summarize|analyze|share|delete) (?:the|a|my)? (?:document|doc)'
            ]
        }
        
        # Gmail entity extractors
        self.gmail_entity_patterns = {
            'query': [
                r'(?:search|find|show|get).+emails? (?:about|with|for|from|containing) ["\']?([^"\']+)["\']?',
                r'emails? (?:about|with|for|from|containing) ["\']?([^"\']+)["\']?'
            ],
            'email_id': [
                r'email (?:id|ID) ["\']?([^"\']+)["\']?'
            ],
            'recipient': [
                r'(?:send|compose|write|draft).+email to ["\']?([^"\']+)["\']?'
            ],
            'subject': [
                r'(?:subject|about) ["\']?([^"\']+)["\']?'
            ],
            'template_type': [
                r'(?:use|create|find) (?:a|an|the) ([^"\']+) (?:template|email template)'
            ],
            'action': [
                r'(check|read|send|reply|forward|categorize|analyze|filter) (?:my|the)? emails?'
            ],
            'time_period': [
                r'(?:in|during|from|last|past) (?:the|this|these)? ([^"\']+) (?:days?|weeks?|months?)'
            ]
        }
        
        # Google Calendar entity extractors
        self.calendar_entity_patterns = {
            'event_name': [
                r'(?:create|add|schedule|book).+(?:event|appointment|meeting) (?:called|named|titled) ["\']?([^"\']+)["\']?',
                r'(?:create|add|schedule|book) ["\']?([^"\']+)["\']? (?:event|appointment|meeting)'
            ],
            'date': [
                r'(?:on|for) (?:the)? ([^"\']+)(?:st|nd|rd|th)?',
                r'(?:on|for) ([a-zA-Z]+ \d{1,2}(?:st|nd|rd|th)?)',
                r'(?:on|for) (?:the)? (\d{1,2}(?:st|nd|rd|th)? (?:of)? [a-zA-Z]+)'
            ],
            'time': [
                r'(?:at|from) (\d{1,2}(?::\d{2})? ?(?:am|pm)?)',
                r'(\d{1,2}(?::\d{2})? ?(?:am|pm)?) (?:to|until) (\d{1,2}(?::\d{2})? ?(?:am|pm)?)'
            ],
            'action': [
                r'(check|view|show|list|create|schedule|cancel|delete) (?:my|the)? (?:calendar|events|meetings|appointments)'
            ],
            'period': [
                r'(?:today|tomorrow|this week|next week|this month|next month)'
            ]
        }
        
        # Google Sheets entity extractors
        self.sheets_entity_patterns = {
            'spreadsheet_name': [
                r'(?:create|edit|open|find|show).+(?:spreadsheet|sheet|gsheet) ["\']?([^"\']+)["\']?',
                r'(?:spreadsheet|sheet|gsheet) (?:called|named|titled) ["\']?([^"\']+)["\']?'
            ],
            'sheet_type': [
                r'(?:create|make) (?:a|an) ([^"\']+) (?:spreadsheet|sheet|tracker)'
            ],
            'action': [
                r'(create|edit|update|analyze|share|delete) (?:my|the)? (?:spreadsheet|sheet)'
            ]
        }
    
    def process_user_input(self, user_input: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process user input and generate a response
        
        Args:
            user_input: The raw input from the user
            context: Additional context about the conversation
            
        Returns:
            Dict containing response and any actions to take
        """
        if not context:
            context = {}
            
        # Detect intent
        intent = self._detect_intent(user_input)
        
        # Extract entities based on intent
        entities = self._extract_entities(user_input, intent)
        
        # Generate response
        response_text = self.generate_response(intent, entities)
        
        # Determine actions to take
        actions = self._determine_actions(intent, entities, context)
        
        response = {
            'text': response_text,
            'actions': actions,
            'detected_intent': intent,
            'entities': entities
        }
        
        return response
    
    def _detect_intent(self, text: str) -> str:
        """
        Detect the intent of the user's message using pattern matching
        
        Args:
            text: The user's message
            
        Returns:
            The detected intent
        """
        # Convert to lowercase for consistent matching
        text_lower = text.lower()
        
        # Check each intent's patterns
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return intent
        
        # Default to general if no patterns match
        return 'general'
    
    def _extract_entities(self, text: str, intent: str) -> Dict[str, Any]:
        """
        Extract entities from the user's message based on intent
        
        Args:
            text: The user's message
            intent: The detected intent
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        # Only process entity extraction for specific intents
        if intent == 'music':
            # Extract Spotify-specific entities
            for entity_type, patterns in self.spotify_entity_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text.lower())
                    if match and match.group(1):
                        # Store the entity value
                        entities[entity_type] = match.group(1).strip()
                        break
                        
            # Detect playback commands
            if re.match(r'^(play|pause|resume|stop|skip|next|previous|shuffle|repeat)$', text.lower()):
                entities['command'] = text.lower()
        
        elif intent == 'google_docs':
            # Extract Google Docs entities
            for entity_type, patterns in self.google_docs_entity_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text.lower())
                    if match and match.group(1):
                        # Store the entity value
                        entities[entity_type] = match.group(1).strip()
                        break
        
        elif intent == 'gmail':
            # Extract Gmail entities
            for entity_type, patterns in self.gmail_entity_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text.lower())
                    if match and match.group(1):
                        # Store the entity value
                        entities[entity_type] = match.group(1).strip()
                        break
        
        elif intent == 'google_calendar':
            # Extract Google Calendar entities
            for entity_type, patterns in self.calendar_entity_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text.lower())
                    if match and match.group(1):
                        # Store the entity value
                        entities[entity_type] = match.group(1).strip()
                        break
        
        elif intent == 'google_sheets':
            # Extract Google Sheets entities
            for entity_type, patterns in self.sheets_entity_patterns.items():
                for pattern in patterns:
                    match = re.search(pattern, text.lower())
                    if match and match.group(1):
                        # Store the entity value
                        entities[entity_type] = match.group(1).strip()
                        break
        
        return entities
    
    def _determine_actions(self, intent: str, entities: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Determine actions to take based on intent and entities
        
        Args:
            intent: The detected intent
            entities: Extracted entities
            context: Conversation context
            
        Returns:
            List of action objects
        """
        actions = []
        
        if intent == 'music':
            # Handle Spotify commands
            if 'command' in entities:
                actions.append({
                    'type': 'spotify_playback',
                    'command': entities['command']
                })
            elif 'track' in entities:
                actions.append({
                    'type': 'spotify_play',
                    'content_type': 'track',
                    'query': entities['track']
                })
            elif 'artist' in entities:
                actions.append({
                    'type': 'spotify_play',
                    'content_type': 'artist',
                    'query': entities['artist']
                })
            elif 'album' in entities:
                actions.append({
                    'type': 'spotify_play',
                    'content_type': 'album',
                    'query': entities['album']
                })
            elif 'playlist' in entities:
                if re.search(r'create|make', context.get('raw_text', '')):
                    actions.append({
                        'type': 'spotify_create_playlist',
                        'name': entities['playlist']
                    })
                else:
                    actions.append({
                        'type': 'spotify_play',
                        'content_type': 'playlist',
                        'query': entities['playlist']
                    })
            elif 'mood' in entities:
                actions.append({
                    'type': 'spotify_mood',
                    'mood': entities['mood']
                })
            elif 'activity' in entities:
                actions.append({
                    'type': 'spotify_activity',
                    'activity': entities['activity']
                })
        
        elif intent == 'google_docs':
            # Handle Google Docs actions
            if 'action' in entities:
                action = entities['action']
                
                if action == 'create':
                    # Handle document creation
                    if 'template_type' in entities:
                        # Create from template
                        template_type = entities['template_type']
                        
                        if re.search(r'journal|recovery journal', template_type):
                            actions.append({
                                'type': 'google_docs_create_template',
                                'template': 'recovery_journal'
                            })
                        elif re.search(r'therapy|worksheet', template_type):
                            actions.append({
                                'type': 'google_docs_create_template',
                                'template': 'therapy_worksheet',
                                'worksheet_type': 'thought_record' if 'thought' in template_type else 'dbt_diary_card'
                            })
                        elif re.search(r'meeting|notes', template_type):
                            actions.append({
                                'type': 'google_docs_create_template',
                                'template': 'meeting_notes',
                                'meeting_type': 'support_group' if 'support' in template_type else 'therapy'
                            })
                        elif re.search(r'progress|tracking', template_type):
                            actions.append({
                                'type': 'google_docs_create_template',
                                'template': 'progress_tracking'
                            })
                        else:
                            # Generic document creation
                            actions.append({
                                'type': 'google_docs_create',
                                'title': entities.get('document_name', 'Untitled Document')
                            })
                    elif 'document_name' in entities:
                        # Create named document
                        actions.append({
                            'type': 'google_docs_create',
                            'title': entities['document_name']
                        })
                    else:
                        # Create generic document
                        actions.append({
                            'type': 'google_docs_create',
                            'title': 'Untitled Document'
                        })
                
                elif action == 'edit' and 'document_name' in entities:
                    # Handle document editing
                    actions.append({
                        'type': 'google_docs_edit',
                        'document_name': entities['document_name'],
                        'edit_request': entities.get('edit_request', '')
                    })
                
                elif action == 'summarize' and 'document_name' in entities:
                    # Handle document summarization
                    actions.append({
                        'type': 'google_docs_summarize',
                        'document_name': entities['document_name']
                    })
                
                elif action == 'analyze' and 'document_name' in entities:
                    # Handle document analysis
                    actions.append({
                        'type': 'google_docs_analyze',
                        'document_name': entities['document_name']
                    })
            elif 'document_name' in entities:
                # Default to viewing the document
                actions.append({
                    'type': 'google_docs_view',
                    'document_name': entities['document_name']
                })
        
        elif intent == 'gmail':
            # Handle Gmail actions
            if 'action' in entities:
                action = entities['action']
                
                if action in ['check', 'read', 'show']:
                    # Handle email retrieval
                    if 'query' in entities:
                        actions.append({
                            'type': 'gmail_search',
                            'query': entities['query']
                        })
                    else:
                        actions.append({
                            'type': 'gmail_list_recent'
                        })
                
                elif action == 'send' and 'recipient' in entities:
                    # Handle email sending
                    actions.append({
                        'type': 'gmail_compose',
                        'recipient': entities['recipient'],
                        'subject': entities.get('subject', '')
                    })
                
                elif action == 'reply' and 'email_id' in entities:
                    # Handle email reply
                    actions.append({
                        'type': 'gmail_reply',
                        'email_id': entities['email_id']
                    })
                
                elif action == 'categorize':
                    # Handle email categorization
                    actions.append({
                        'type': 'gmail_categorize'
                    })
                
                elif action == 'analyze':
                    # Handle email analysis
                    actions.append({
                        'type': 'gmail_analyze'
                    })
                
                elif action == 'filter':
                    # Handle email filtering for recovery-relevant emails
                    days = 7
                    if 'time_period' in entities:
                        time_period = entities['time_period']
                        if re.search(r'\d+', time_period):
                            days = int(re.search(r'\d+', time_period).group())
                    
                    actions.append({
                        'type': 'gmail_filter_recovery',
                        'days': days
                    })
            
            elif 'template_type' in entities:
                # Handle email template creation
                template_type = entities['template_type']
                template = 'sponsor_check_in'
                
                if re.search(r'amend|apology', template_type):
                    template = 'making_amends'
                elif re.search(r'request|support', template_type):
                    template = 'request_support'
                elif re.search(r'decline|event', template_type):
                    template = 'decline_event'
                elif re.search(r'time|off|recovery', template_type):
                    template = 'recovery_time_request'
                
                actions.append({
                    'type': 'gmail_create_template',
                    'template': template
                })
            
            elif 'query' in entities:
                # Default to searching emails
                actions.append({
                    'type': 'gmail_search',
                    'query': entities['query']
                })
        
        elif intent == 'google_calendar':
            # Handle Google Calendar actions
            if 'action' in entities:
                action = entities['action']
                
                if action in ['check', 'view', 'show', 'list']:
                    # Handle calendar viewing
                    period = entities.get('period', 'today')
                    actions.append({
                        'type': 'calendar_view',
                        'period': period
                    })
                
                elif action in ['create', 'schedule']:
                    # Handle event creation
                    event_name = entities.get('event_name', 'New Event')
                    date = entities.get('date', '')
                    time = entities.get('time', '')
                    
                    actions.append({
                        'type': 'calendar_create_event',
                        'event_name': event_name,
                        'date': date,
                        'time': time
                    })
                
                elif action in ['cancel', 'delete'] and 'event_name' in entities:
                    # Handle event cancellation
                    actions.append({
                        'type': 'calendar_cancel_event',
                        'event_name': entities['event_name']
                    })
            
            elif 'event_name' in entities:
                # Default to creating an event
                date = entities.get('date', '')
                time = entities.get('time', '')
                
                actions.append({
                    'type': 'calendar_create_event',
                    'event_name': entities['event_name'],
                    'date': date,
                    'time': time
                })
            elif 'period' in entities:
                # Default to viewing calendar
                actions.append({
                    'type': 'calendar_view',
                    'period': entities['period']
                })
        
        elif intent == 'google_sheets':
            # Handle Google Sheets actions
            if 'action' in entities:
                action = entities['action']
                
                if action == 'create':
                    # Handle spreadsheet creation
                    if 'sheet_type' in entities:
                        # Create specific spreadsheet type
                        sheet_type = entities['sheet_type']
                        
                        if re.search(r'medication|med', sheet_type):
                            actions.append({
                                'type': 'sheets_create_template',
                                'template': 'medication_tracker'
                            })
                        elif re.search(r'recovery|metrics|dashboard', sheet_type):
                            actions.append({
                                'type': 'sheets_create_template',
                                'template': 'recovery_metrics'
                            })
                        elif re.search(r'budget|financial', sheet_type):
                            actions.append({
                                'type': 'sheets_create_template',
                                'template': 'budget'
                            })
                        else:
                            # Generic spreadsheet
                            actions.append({
                                'type': 'sheets_create',
                                'title': entities.get('spreadsheet_name', 'Untitled Spreadsheet')
                            })
                    elif 'spreadsheet_name' in entities:
                        # Create named spreadsheet
                        actions.append({
                            'type': 'sheets_create',
                            'title': entities['spreadsheet_name']
                        })
                    else:
                        # Create generic spreadsheet
                        actions.append({
                            'type': 'sheets_create',
                            'title': 'Untitled Spreadsheet'
                        })
                
                elif action in ['edit', 'update'] and 'spreadsheet_name' in entities:
                    # Handle spreadsheet editing
                    actions.append({
                        'type': 'sheets_edit',
                        'spreadsheet_name': entities['spreadsheet_name']
                    })
                
                elif action == 'analyze' and 'spreadsheet_name' in entities:
                    # Handle spreadsheet analysis
                    actions.append({
                        'type': 'sheets_analyze',
                        'spreadsheet_name': entities['spreadsheet_name']
                    })
            
            elif 'sheet_type' in entities:
                # Create specific spreadsheet type
                sheet_type = entities['sheet_type']
                template = 'generic'
                
                if re.search(r'medication|med', sheet_type):
                    template = 'medication_tracker'
                elif re.search(r'recovery|metrics|dashboard', sheet_type):
                    template = 'recovery_metrics'
                elif re.search(r'budget|financial', sheet_type):
                    template = 'budget'
                
                actions.append({
                    'type': 'sheets_create_template',
                    'template': template
                })
            
            elif 'spreadsheet_name' in entities:
                # Default to viewing the spreadsheet
                actions.append({
                    'type': 'sheets_view',
                    'spreadsheet_name': entities['spreadsheet_name']
                })
        
        return actions
    
    def generate_response(self, intent: str, entities: Dict[str, Any] = None) -> str:
        """
        Generate a response based on intent and entities
        
        Args:
            intent: The detected intent
            entities: Any entities extracted from the user's message
            
        Returns:
            A response string
        """
        if not entities:
            entities = {}
            
        # Generate response based on intent and entities
        if intent == 'music':
            if 'command' in entities:
                command = entities['command']
                if command in ['play', 'resume']:
                    return "I'll resume playback for you."
                elif command in ['pause', 'stop']:
                    return "I'll pause the music for you."
                elif command in ['skip', 'next']:
                    return "I'll skip to the next track."
                elif command == 'previous':
                    return "I'll go back to the previous track."
                elif command == 'shuffle':
                    return "I'll toggle shuffle mode for you."
                elif command == 'repeat':
                    return "I'll toggle repeat mode for you."
                else:
                    return "I'll handle the playback command for you."
            elif 'track' in entities:
                return f"I'll play the song '{entities['track']}' for you."
            elif 'artist' in entities:
                return f"I'll play music by {entities['artist']} for you."
            elif 'album' in entities:
                return f"I'll play the album '{entities['album']}' for you."
            elif 'playlist' in entities:
                if 'create' in entities.get('action', ''):
                    return f"I'll create a new playlist called '{entities['playlist']}' for you."
                else:
                    return f"I'll play the '{entities['playlist']}' playlist for you."
            elif 'mood' in entities:
                return f"I'll find some {entities['mood']} music for you."
            elif 'activity' in entities:
                return f"I'll play suitable music for {entities['activity']}."
            else:
                return "I can help you play music. What would you like to hear?"
        
        elif intent == 'google_docs':
            if 'action' in entities:
                action = entities['action']
                if action == 'create':
                    if 'template_type' in entities:
                        template_type = entities['template_type']
                        if re.search(r'journal|recovery journal', template_type):
                            return "I'll create a recovery journal document for you."
                        elif re.search(r'therapy|worksheet', template_type):
                            return "I'll create a therapy worksheet for you."
                        elif re.search(r'meeting|notes', template_type):
                            return "I'll create a meeting notes template for you."
                        elif re.search(r'progress|tracking', template_type):
                            return "I'll create a progress tracking document for you."
                        else:
                            return f"I'll create a document for {template_type} for you."
                    elif 'document_name' in entities:
                        return f"I'll create a new document called '{entities['document_name']}' for you."
                    else:
                        return "I'll create a new document for you."
                elif action == 'edit':
                    return f"I'll help you edit the document '{entities.get('document_name', 'requested document')}'."
                elif action == 'summarize':
                    return f"I'll summarize the document '{entities.get('document_name', 'requested document')}' for you."
                elif action == 'analyze':
                    return f"I'll analyze the content of '{entities.get('document_name', 'the document')}' for you."
                else:
                    return f"I'll {action} the document for you."
            elif 'document_name' in entities:
                return f"I'll open the document '{entities['document_name']}' for you."
            else:
                return "I can help you with Google Docs. What would you like to do?"
        
        elif intent == 'gmail':
            if 'action' in entities:
                action = entities['action']
                if action in ['check', 'read', 'show']:
                    if 'query' in entities:
                        return f"I'll find emails about '{entities['query']}' for you."
                    else:
                        return "I'll show you your recent emails."
                elif action == 'send':
                    recipient = entities.get('recipient', 'the recipient')
                    return f"I'll help you compose an email to {recipient}."
                elif action == 'reply':
                    return "I'll help you reply to that email."
                elif action == 'categorize':
                    return "I'll categorize your emails based on recovery relevance."
                elif action == 'analyze':
                    return "I'll analyze your emails for content and sentiment."
                elif action == 'filter':
                    days = 7
                    if 'time_period' in entities:
                        time_period = entities['time_period']
                        if re.search(r'\d+', time_period):
                            days = int(re.search(r'\d+', time_period).group())
                    return f"I'll filter your emails for recovery-relevant content from the past {days} days."
                else:
                    return f"I'll {action} your emails for you."
            elif 'template_type' in entities:
                template_type = entities['template_type']
                return f"I'll create a {template_type} email template for you."
            elif 'query' in entities:
                return f"I'll search for emails about '{entities['query']}' for you."
            else:
                return "I can help you with your emails. What would you like to do?"
        
        elif intent == 'google_calendar':
            if 'action' in entities:
                action = entities['action']
                if action in ['check', 'view', 'show', 'list']:
                    period = entities.get('period', 'today')
                    return f"I'll show you your calendar for {period}."
                elif action in ['create', 'schedule']:
                    event_name = entities.get('event_name', 'the event')
                    return f"I'll schedule {event_name} for you."
                elif action in ['cancel', 'delete']:
                    event_name = entities.get('event_name', 'the event')
                    return f"I'll cancel {event_name} from your calendar."
                else:
                    return f"I'll {action} your calendar events for you."
            elif 'event_name' in entities:
                return f"I'll schedule {entities['event_name']} for you."
            elif 'period' in entities:
                return f"I'll show you your calendar for {entities['period']}."
            else:
                return "I can help you manage your calendar. What would you like to do?"
        
        elif intent == 'google_sheets':
            if 'action' in entities:
                action = entities['action']
                if action == 'create':
                    if 'sheet_type' in entities:
                        sheet_type = entities['sheet_type']
                        if re.search(r'medication|med', sheet_type):
                            return "I'll create a medication tracking spreadsheet for you."
                        elif re.search(r'recovery|metrics|dashboard', sheet_type):
                            return "I'll create a recovery metrics dashboard for you."
                        elif re.search(r'budget|financial', sheet_type):
                            return "I'll create a budget management spreadsheet for you."
                        else:
                            return f"I'll create a {sheet_type} spreadsheet for you."
                    elif 'spreadsheet_name' in entities:
                        return f"I'll create a new spreadsheet called '{entities['spreadsheet_name']}' for you."
                    else:
                        return "I'll create a new spreadsheet for you."
                elif action in ['edit', 'update']:
                    return f"I'll help you edit the spreadsheet '{entities.get('spreadsheet_name', 'requested spreadsheet')}'."
                elif action == 'analyze' and 'spreadsheet_name' in entities:
                    return f"I'll analyze the data in '{entities.get('spreadsheet_name', 'the spreadsheet')}' for you."
                else:
                    return f"I'll {action} the spreadsheet for you."
            elif 'sheet_type' in entities:
                sheet_type = entities['sheet_type']
                if re.search(r'medication|med', sheet_type):
                    return "I'll create a medication tracking spreadsheet for you."
                elif re.search(r'recovery|metrics|dashboard', sheet_type):
                    return "I'll create a recovery metrics dashboard for you."
                elif re.search(r'budget|financial', sheet_type):
                    return "I'll create a budget management spreadsheet for you."
                else:
                    return f"I'll create a {sheet_type} spreadsheet for you."
            elif 'spreadsheet_name' in entities:
                return f"I'll open the spreadsheet '{entities['spreadsheet_name']}' for you."
            else:
                return "I can help you with Google Sheets. What would you like to do?"
        
        elif intent == 'weather':
            return "I can check the weather for you. Which location are you interested in?"
        elif intent == 'task':
            return "I can help you manage your tasks. Would you like to create a new task?"
        elif intent == 'appointment':
            return "I can help you with your schedule. Would you like to check or create an appointment?"
        else:
            return "How can I assist you today?"

# Create a singleton instance
ai_helper = AIHelper()

def get_ai_helper() -> AIHelper:
    """Get the singleton instance of AIHelper"""
    return ai_helper 

def generate_ai_text(prompt, model="gpt-3.5-turbo", max_tokens=1000, temperature=0.7):
    """
    Generate text using AI
    
    Args:
        prompt: Text prompt for generation
        model: AI model to use 
        max_tokens: Maximum tokens to generate
        temperature: Creativity factor (0.0-1.0)
        
    Returns:
        Generated text
    """
    if not openai_client:
        logging.warning("OpenAI client not initialized. Check your API key.")
        return "AI text generation not available. Please check system settings."
    
    # Check rate limits
    if not rate_limiter.can_make_request():
        logging.warning("Rate limit reached, waiting before making API request")
        time.sleep(5)  # Wait a bit and try again
        if not rate_limiter.can_make_request():
            return "AI service temporarily unavailable due to high demand. Please try again shortly."
    
    try:
        # Record this request
        rate_limiter.add_request()
        
        response = openai_client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a recovery-focused application."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract the generated text
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logging.error(f"Error generating AI text: {str(e)}")
        return f"Error generating text: {str(e)}"

def analyze_document_content(content, analysis_type="general", max_tokens=1000):
    """
    Analyze document content using AI
    
    Args:
        content: Text content to analyze
        analysis_type: Type of analysis to perform (general, sentiment, therapeutic)
        max_tokens: Maximum tokens for the response
        
    Returns:
        Analysis results as a dictionary
    """
    if not openai_client:
        logging.warning("OpenAI client not initialized. Check your API key.")
        return {"error": "AI analysis not available. Please check system settings."}
    
    # Check rate limits
    if not rate_limiter.can_make_request():
        logging.warning("Rate limit reached, waiting before making API request")
        time.sleep(5)  # Wait a bit and try again
        if not rate_limiter.can_make_request():
            return {"error": "AI service temporarily unavailable due to high demand. Please try again shortly."}
    
    try:
        # Select the appropriate prompt based on analysis type
        if analysis_type == "sentiment":
            system_prompt = "You are an emotional intelligence expert. Analyze the sentiment and emotional content of the provided text."
            user_prompt = "Provide a detailed analysis of the emotional content of this text. Identify the main emotions, their intensity, and overall sentiment. Format your response as JSON with keys for 'primary_emotion', 'secondary_emotions', 'sentiment_score' (-10 to 10), 'emotional_patterns', and 'recommendations'."
        elif analysis_type == "therapeutic":
            system_prompt = "You are a therapeutic writing analyst with expertise in recovery. Analyze the provided text for therapeutic insights."
            user_prompt = "Analyze this therapeutic writing for recovery insights. Identify themes, patterns, challenges, strengths, and areas for growth. Format your response as JSON with keys for 'themes', 'patterns', 'challenges', 'strengths', 'growth_areas', and 'therapeutic_recommendations'."
        else:  # general analysis
            system_prompt = "You are a document analysis assistant. Analyze the provided text and extract key information."
            user_prompt = "Analyze this document content and provide a comprehensive assessment. Format your response as JSON with keys for 'summary', 'key_topics', 'action_items', 'main_theme', and 'insights'."
        
        # Truncate content if too long
        if len(content) > 10000:
            content = content[:10000] + "...[content truncated]"
        
        # Record this request
        rate_limiter.add_request()
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
                {"role": "user", "content": content}
            ],
            max_tokens=max_tokens,
            temperature=0.5,
            response_format={"type": "json_object"}
        )
        
        # Extract and parse the JSON response
        analysis_text = response.choices[0].message.content.strip()
        analysis_json = json.loads(analysis_text)
        
        return analysis_json
        
    except json.JSONDecodeError:
        logging.error("Failed to decode JSON from AI response")
        return {"error": "Failed to parse AI analysis", "raw_response": analysis_text if 'analysis_text' in locals() else "No response"}
        
    except Exception as e:
        logging.error(f"Error analyzing content: {str(e)}")
        return {"error": f"Error analyzing content: {str(e)}"}

def generate_recovery_content(topic, format_type="journal_prompt", recovery_program="general", max_tokens=500):
    """
    Generate recovery-specific content
    
    Args:
        topic: Recovery topic or theme
        format_type: Type of content to generate (journal_prompt, reflection, exercise)
        recovery_program: Recovery program context (aa, dbt, general)
        max_tokens: Maximum tokens for the response
        
    Returns:
        Generated recovery content
    """
    if not openai_client:
        logging.warning("OpenAI client not initialized. Check your API key.")
        return "Recovery content generation not available. Please check system settings."
    
    # Check rate limits
    if not rate_limiter.can_make_request():
        logging.warning("Rate limit reached, waiting before making API request")
        time.sleep(5)  # Wait a bit and try again
        if not rate_limiter.can_make_request():
            return "AI service temporarily unavailable due to high demand. Please try again shortly."
    
    try:
        # Create a context-appropriate prompt based on the recovery program
        if recovery_program.lower() == "aa":
            system_prompt = "You are an experienced AA sponsor with deep knowledge of 12-step recovery. Provide supportive, non-judgmental guidance focused on the principles of Alcoholics Anonymous."
        elif recovery_program.lower() == "dbt":
            system_prompt = "You are a DBT therapist assistant with expertise in dialectical behavior therapy. Provide balanced, skills-focused guidance that incorporates DBT principles and techniques."
        else:
            system_prompt = "You are a recovery support specialist with broad knowledge of recovery principles. Provide supportive, evidence-based guidance for people in recovery."
        
        # Create a format-appropriate prompt
        if format_type == "journal_prompt":
            user_prompt = f"Create a thoughtful journal prompt about {topic} that encourages deep reflection on recovery. The prompt should be specific, thought-provoking, and recovery-oriented."
        elif format_type == "reflection":
            user_prompt = f"Write a brief reflection on {topic} from a recovery perspective. Include insights about how this relates to the recovery journey and personal growth."
        elif format_type == "exercise":
            user_prompt = f"Design a practical exercise related to {topic} that someone in recovery can complete. Include clear steps, a purpose statement, and reflection questions."
        else:
            user_prompt = f"Create recovery-focused content about {topic}. Make it supportive, insightful, and practical for someone in recovery."
        
        # Record this request
        rate_limiter.add_request()
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        
        # Extract the generated text
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logging.error(f"Error generating recovery content: {str(e)}")
        return f"Error generating content: {str(e)}" 