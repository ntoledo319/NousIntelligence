"""
Chat Routes and API Endpoints
============================

This module contains the routes and API endpoints for handling chat interactions,
integrating the chat command router to process user messages and generate
appropriate responses.
"""

import json
import logging
from flask import Blueprint, request, jsonify, session, current_app, render_template
from flask_login import login_required, current_user
from werkzeug.exceptions import BadRequest, Unauthorized

from routes.chat_router import process_chat_command
from utils.ai_helper import get_ai_response

# Create a blueprint for chat routes
chat_bp = Blueprint('chat', __name__, url_prefix='/chat')
chat_api_bp = Blueprint('chat_api', __name__, url_prefix='/api/chat')

logger = logging.getLogger(__name__)

@chat_bp.route('/', methods=['GET'])
@login_required
def chat_interface():
    """Render the chat interface"""
    return render_template('chat/index.html')

@chat_api_bp.route('/message', methods=['POST'])
@login_required
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
            logger.warning(f"Invalid message format or length from user {current_user.id}")
            return jsonify({
                'success': False,
                'message': 'Invalid message format or length'
            }), 400
        
        # Process as a potential command
        response = process_chat_command(current_user.id, user_message)
        
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
                user_settings=current_user.settings
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
@login_required
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
@login_required
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
@login_required
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