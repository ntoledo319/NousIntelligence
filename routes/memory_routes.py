"""
Memory Routes Routes
Memory Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated

memory_routes_bp = Blueprint('memory_routes', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

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

Memory Routes

This module provides API routes for the memory system, allowing the application
to retrieve and manage user memory data for persistent learning.

@module routes.memory_routes
@description Memory system API routes
"""

import logging
from flask import Blueprint, request, jsonify, current_app

from typing import Dict, Any, List

from services.memory_service import get_memory_service
from utils.enhanced_memory import get_user_memory

logger = logging.getLogger(__name__)

# Create blueprint
memory_bp = Blueprint('memory', __name__, url_prefix='/api/memory')

@memory_bp.route('/summary', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def get_memory_summary():
    """
    Get a summary of the user's memory

    Returns:
        JSON response with memory summary
    """
    try:
        memory_service = get_memory_service()
        summary = memory_service.get_memory_summary(session.get('user', {}).get('id', 'demo_user'))

        return jsonify({
            'status': 'success',
            'data': summary
        }), 200
    except Exception as e:
        logger.error(f"Error getting memory summary: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not retrieve memory summary'
        }), 500

@memory_bp.route('/recent', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def get_recent_memories():
    """
    Get recent conversation memories

    Returns:
        JSON response with recent memories
    """
    try:
        count = request.args.get('count', 20, type=int)

        memory_service = get_memory_service()
        memories = memory_service.get_recent_messages(session.get('user', {}).get('id', 'demo_user'), count=count)

        return jsonify({
            'status': 'success',
            'data': memories
        }), 200
    except Exception as e:
        logger.error(f"Error getting recent memories: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not retrieve recent memories'
        }), 500

@memory_bp.route('/topics', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def get_topics():
    """
    Get user's topics of interest

    Returns:
        JSON response with topics
    """
    try:
        min_interest = request.args.get('min_interest', 0, type=int)

        memory_service = get_memory_service()
        topics = memory_service.get_topic_interests(session.get('user', {}).get('id', 'demo_user'), min_interest=min_interest)

        return jsonify({
            'status': 'success',
            'data': topics
        }), 200
    except Exception as e:
        logger.error(f"Error getting topics: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not retrieve topics'
        }), 500

@memory_bp.route('/entities', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def get_entities():
    """
    Get user's remembered entities

    Returns:
        JSON response with entities
    """
    try:
        entity_type = request.args.get('type')

        memory_service = get_memory_service()
        entities = memory_service.get_entity_memories(session.get('user', {}).get('id', 'demo_user'), entity_type=entity_type)

        return jsonify({
            'status': 'success',
            'data': entities
        }), 200
    except Exception as e:
        logger.error(f"Error getting entities: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not retrieve entities'
        }), 500

@memory_bp.route('/entities', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def add_entity():
    """
    Add or update an entity memory

    Returns:
        JSON response with status
    """
    try:
        data = request.get_json()

        if not data or not data.get('entity_name') or not data.get('entity_type'):
            return jsonify({
                'status': 'error',
                'message': 'Missing required entity information'
            }), 400

        entity_name = data.get('entity_name')
        entity_type = data.get('entity_type')
        attributes = data.get('attributes', {})
        importance = data.get('importance')

        memory_service = get_memory_service()
        success = memory_service.update_entity_memory(
            session.get('user', {}).get('id', 'demo_user'),
            entity_name,
            entity_type,
            attributes,
            importance
        )

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Entity memory updated'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update entity memory'
            }), 500
    except Exception as e:
        logger.error(f"Error updating entity: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not update entity memory'
        }), 500

@memory_bp.route('/topics', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def update_topic():
    """
    Update a topic interest

    Returns:
        JSON response with status
    """
    try:
        data = request.get_json()

        if not data or not data.get('topic_name'):
            return jsonify({
                'status': 'error',
                'message': 'Missing required topic information'
            }), 400

        topic_name = data.get('topic_name')
        interest_delta = data.get('interest_delta', 1)
        metadata = data.get('metadata')

        memory_service = get_memory_service()
        success = memory_service.update_topic_interest(
            session.get('user', {}).get('id', 'demo_user'),
            topic_name,
            interest_delta=interest_delta,
            metadata=metadata
        )

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Topic interest updated'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update topic interest'
            }), 500
    except Exception as e:
        logger.error(f"Error updating topic: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not update topic interest'
        }), 500

@memory_bp.route('/initialize', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def initialize_memory():
    """
    Initialize memory for the current user

    Returns:
        JSON response with status
    """
    try:
        memory_service = get_memory_service()
        success = memory_service.initialize_memory_for_user(session.get('user', {}).get('id', 'demo_user'))

        if success:
            return jsonify({
                'status': 'success',
                'message': 'Memory initialized'
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to initialize memory'
            }), 500
    except Exception as e:
        logger.error(f"Error initializing memory: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Could not initialize memory'
        }), 500

def register_memory_routes(app):
    """Register memory routes with the Flask app"""
    app.register_blueprint(memory_bp)
    logger.info("Memory routes registered")