"""

def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Authentication required', 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for('login'))

def get_current_user():
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

Chat Routes and API Endpoints
============================

This module contains the routes and API endpoints for handling chat interactions,
integrating the chat command router to process user messages and generate
appropriate responses.
"""

import json
import logging
from flask import Blueprint, request, jsonify, session, current_app, render_template

from werkzeug.exceptions import BadRequest, Unauthorized

from routes.chat_router import process_chat_command
from utils.ai_helper import get_ai_response

# Create a blueprint for chat routes
chat_bp = Blueprint('chat', __name__, url_prefix='/chat')
chat_api_bp = Blueprint('chat_api', __name__, url_prefix='/api/chat')

logger = logging.getLogger(__name__)

@chat_bp.route('/', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def chat_interface():
    """Render the chat interface"""
    return render_template('chat/index.html')

@chat_api_bp.route('/message', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def chat_message():
    """
    Process a user's chat message and return the appropriate response

    This endpoint handles both command processing and general AI conversation.
    """
    try:
        data = request.get_json()

        if not data or 'message' not in data:
            logger.warning(f"Invalid chat message request: {request.data}")
            return jsonify({
                'success': False,
                'message': 'No message provided'
            }), 400

        user_message = data['message']

        # Validate message content
        if not isinstance(user_message, str) or len(user_message) > 5000:
            logger.warning(f"Invalid message format or length from user {session.get('user', {}).get('id', 'demo_user')}")
            return jsonify({
                'success': False,
                'message': 'Invalid message format or length'
            }), 400

        # Process as a potential command
        response = process_chat_command(session.get('user', {}).get('id', 'demo_user'), user_message)

        # If it wasn't a recognized command, use the AI for conversational response
        if not response.get('is_command', False) and response.get('success', False):
            # Get chat history
            chat_history = session.get('chat_history', [])

            # Add user message to history
            chat_history.append({
                'role': 'user',
                'content': user_message
            })

            # Get AI response
            ai_response = get_ai_response(
                user_message,
                chat_history,
                user_settings=session.get('user', {}).get('settings
            )

            # Update response with AI's message
            response = {
                'success': True,
                'message': ai_response,
                'is_command': False
            }

            # Add AI response to history
            chat_history.append({
                'role': 'assistant',
                'content': ai_response
            })

            # Limit history length
            if len(chat_history) > current_app.config.get('CHAT_HISTORY_LIMIT', 20):
                chat_history = chat_history[-current_app.config.get('CHAT_HISTORY_LIMIT', 20):]

            # Save updated history
            session['chat_history'] = chat_history

        return jsonify(response)
    except BadRequest as e:
        logger.warning(f"Bad request in chat message: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Invalid request format'
        }), 400
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred processing your message'
        }), 500

@chat_api_bp.route('/history', methods=['GET'])
def get_chat_history():
    """Get the current chat history for the user"""
    try:
        chat_history = session.get('chat_history', [])
        return jsonify({
            'success': True,
            'history': chat_history
        })
    except Exception as e:
        logger.error(f"Error retrieving chat history: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred retrieving chat history'
        }), 500

@chat_api_bp.route('/history', methods=['DELETE'])
def clear_chat_history():
    """Clear the chat history for the current user"""
    try:
        session['chat_history'] = []
        return jsonify({
            'success': True,
            'message': 'Chat history cleared'
        })
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred clearing chat history'
        }), 500

@chat_api_bp.route('/command_help', methods=['GET'])
def get_command_help():
    """Get help information about available chat commands"""
    commands = {
        'meet': {
            'create_meeting': 'Create a new Google Meet meeting (e.g., "Create a meeting tomorrow at 3pm")',
            'therapy_session': 'Create a therapy session (e.g., "Schedule a therapy session with Dr. Smith on Friday")',
            'recovery_group': 'Create a recovery group meeting (e.g., "Create an AA recovery group on Monday at 7pm")',
            'sponsor_meeting': 'Create a sponsor meeting (e.g., "Schedule a meeting with my sponsor tomorrow")',
            'mindfulness_session': 'Create a mindfulness session (e.g., "Set up a meditation session for Thursday morning")',
            'list_meetings': 'List your upcoming meetings (e.g., "Show my upcoming meetings")',
            'generate_agenda': 'Generate an agenda for a meeting (e.g., "Generate an agenda for my recovery meeting")',
            'analyze_notes': 'Analyze meeting notes (e.g., "Analyze these notes from my therapy session")'
        }
        # Add other command domains as they're implemented
    }

    return jsonify({
        'success': True,
        'commands': commands
    })