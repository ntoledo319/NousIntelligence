"""
Mental Health Chat API Integration

This module integrates the enhanced mental health chat handler with the
existing chat API endpoints for seamless crisis support and resource discovery.

@module api.mental_health_chat
@ai_prompt Use this for mental health support in chat conversations
"""

import logging
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Optional
from datetime import datetime

from utils.mental_health_chat_handler import get_mental_health_handler
from utils.chat_feature_integration import ChatFeatureIntegration
from services.mental_health_resources_service import MentalHealthResourcesService

logger = logging.getLogger(__name__)

# Create mental health chat blueprint
mental_health_chat_bp = Blueprint('mental_health_chat', __name__, url_prefix='/api/mental-health')

# Initialize services
mental_health_handler = get_mental_health_handler()
chat_integration = ChatFeatureIntegration()
resources_service = MentalHealthResourcesService()


@mental_health_chat_bp.route('/chat', methods=['POST'])
def mental_health_chat():
    """
    Dedicated mental health chat endpoint with enhanced crisis detection
    
    This endpoint provides specialized handling for mental health conversations
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user context
        user_id = session.get('user_id', session.get('google_id', 'guest'))
        
        # Build comprehensive context
        context = {
            'location': data.get('location', {}),
            'conversation_history': data.get('history', []),
            'user_mood': data.get('mood'),
            'timestamp': datetime.now().isoformat(),
            'session_id': session.get('session_id', f"session_{user_id}"),
            'previous_mental_health_discussion': _check_previous_discussions(user_id)
        }
        
        # Process message through mental health handler
        response_data = mental_health_handler.process_message(user_id, message, context)
        
        if response_data:
            # Format response for chat
            formatted_message = mental_health_handler.format_chat_response(response_data)
            
            # Track engagement for gamification
            if response_data['type'] == 'crisis_support':
                chat_integration.reward_chat_engagement(user_id, 'crisis_support')
            elif response_data['type'] == 'resource_discovery':
                chat_integration.reward_chat_engagement(user_id, 'therapy_discussion')
            else:
                chat_integration.reward_chat_engagement(user_id, 'support_seeking')
            
            # Build API response
            api_response = {
                'success': True,
                'message': formatted_message,
                'type': response_data['type'],
                'requires_immediate_display': response_data.get('requires_immediate_display', False),
                'structured_data': response_data,
                'timestamp': datetime.now().isoformat()
            }
            
            # Add location request if needed
            if response_data.get('needs_location'):
                api_response['needs_location'] = True
                api_response['location_prompt'] = "Please share your location to find nearby resources"
            
            # Log interaction for analytics
            _log_mental_health_interaction(user_id, response_data['type'], 
                                         response_data.get('severity', 0))
            
            return jsonify(api_response)
        
        else:
            # No mental health content detected - provide general support
            return jsonify({
                'success': True,
                'message': "I'm here to help with mental health support. You can ask me about finding therapists, crisis resources, or just talk about what's on your mind.",
                'type': 'general_support',
                'suggestions': [
                    "Find a therapist near me",
                    "Show crisis support numbers",
                    "I'm feeling anxious",
                    "Free mental health resources"
                ]
            })
    
    except Exception as e:
        logger.error(f"Error in mental health chat: {str(e)}")
        return jsonify({
            'error': 'Failed to process message',
            'message': 'An error occurred, but crisis resources are always available at /resources/crisis'
        }), 500


@mental_health_chat_bp.route('/check-in', methods=['POST'])
def mental_health_checkin():
    """
    Mental health check-in endpoint for scheduled or user-initiated check-ins
    """
    try:
        user_id = session.get('user_id', session.get('google_id', 'guest'))
        data = request.get_json() or {}
        
        checkin_type = data.get('type', 'user_initiated')
        mood_rating = data.get('mood_rating')  # 1-10 scale
        
        # Build check-in response
        response = {
            'success': True,
            'type': 'checkin',
            'timestamp': datetime.now().isoformat()
        }
        
        if mood_rating and mood_rating <= 3:
            # Low mood - provide immediate support
            response['message'] = "I notice you're having a tough time. I'm here to help."
            response['support_options'] = [
                {
                    'label': '🆘 Crisis support (24/7)',
                    'action': 'show_crisis_resources'
                },
                {
                    'label': '🏥 Find a therapist',
                    'action': 'search_therapy'
                },
                {
                    'label': '💬 Talk about what\'s going on',
                    'action': 'supportive_chat'
                }
            ]
            
            # Get crisis resources
            resources = resources_service.get_crisis_resources('US')[:2]
            response['crisis_resources'] = [
                {
                    'name': r.name,
                    'phone': r.phone_number,
                    'text': r.text_number
                }
                for r in resources
            ]
            
        elif mood_rating and mood_rating >= 7:
            # Good mood - celebrate and encourage
            response['message'] = "It's wonderful to hear you're doing well! Keep up the great work."
            response['encouragement'] = True
            
            # Award points for positive check-in
            chat_integration.reward_chat_engagement(user_id, 'wellness_checkin')
            
        else:
            # Neutral mood - offer support options
            response['message'] = "Thanks for checking in. How can I support you today?"
            response['support_options'] = [
                {
                    'label': '📝 Journal about my day',
                    'action': 'journal_prompt'
                },
                {
                    'label': '🎯 Review my goals',
                    'action': 'show_goals'
                },
                {
                    'label': '🤝 Connect with support groups',
                    'action': 'show_groups'
                }
            ]
        
        # Store check-in data
        _store_checkin_data(user_id, mood_rating, checkin_type)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in mental health check-in: {str(e)}")
        return jsonify({
            'error': 'Check-in failed',
            'message': 'Unable to process check-in, but support is always available'
        }), 500


@mental_health_chat_bp.route('/resources/search', methods=['POST'])
def search_mental_health_resources():
    """
    Search for mental health resources based on location and filters
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No search criteria provided'}), 400
        
        user_id = session.get('user_id', session.get('google_id', 'guest'))
        
        # Extract search parameters
        resource_type = data.get('type', 'therapy')  # therapy, psychiatry, crisis
        location = data.get('location', {})
        filters = data.get('filters', {})
        
        # Validate location
        if resource_type in ['therapy', 'psychiatry'] and not location:
            return jsonify({
                'error': 'Location required',
                'message': 'Please provide a location to search for providers'
            }), 400
        
        results = {
            'success': True,
            'type': resource_type,
            'results': []
        }
        
        if resource_type == 'crisis':
            # Get crisis resources
            country = location.get('country_code', 'US')
            resources = resources_service.get_crisis_resources(country)
            results['results'] = [
                {
                    'name': r.name,
                    'phone': r.phone_number,
                    'text': r.text_number,
                    'description': r.description,
                    'available': '24/7' if r.is_24_7 else 'Limited hours',
                    'type': 'crisis'
                }
                for r in resources
            ]
            
        elif resource_type == 'therapy':
            # Search for therapists
            city = location.get('city')
            state = location.get('state')
            
            if filters.get('affordable_only'):
                providers = resources_service.get_affordable_therapy_options(city, state)
            else:
                providers = resources_service.search_therapy_providers(
                    latitude=location.get('latitude'),
                    longitude=location.get('longitude'),
                    radius_miles=filters.get('radius', 25),
                    specializations=filters.get('specializations', []),
                    accepts_insurance=filters.get('accepts_insurance'),
                    has_sliding_scale=filters.get('sliding_scale'),
                    is_online=filters.get('online_only')
                )
            
            results['results'] = [
                {
                    'name': p.name,
                    'specialties': p.specializations[:3] if p.specializations else [],
                    'sliding_scale': p.has_sliding_scale,
                    'online': p.is_online,
                    'accepting_patients': p.is_accepting_patients,
                    'contact': {
                        'phone': p.phone,
                        'email': p.email,
                        'website': p.website
                    },
                    'type': 'therapy'
                }
                for p in providers[:10]  # Limit to 10 results
            ]
            
        elif resource_type == 'psychiatry':
            # Search for psychiatrists
            providers = resources_service.search_psychiatry_providers(
                latitude=location.get('latitude'),
                longitude=location.get('longitude'),
                radius_miles=filters.get('radius', 25),
                accepts_medicare=filters.get('accepts_medicare'),
                accepts_medicaid=filters.get('accepts_medicaid'),
                is_telehealth=filters.get('telehealth_only')
            )
            
            results['results'] = [
                {
                    'name': p.name,
                    'board_certified': p.is_board_certified,
                    'telehealth': p.is_telehealth,
                    'medicare': p.accepts_medicare,
                    'medicaid': p.accepts_medicaid,
                    'contact': {
                        'phone': p.phone,
                        'website': p.website
                    },
                    'type': 'psychiatry'
                }
                for p in providers[:10]
            ]
        
        # Add general resources if no specific results
        if not results['results']:
            results['fallback_resources'] = _get_fallback_resources(resource_type)
            results['message'] = "No specific providers found in your area, but here are some online and national resources:"
        
        return jsonify(results)
        
    except Exception as e:
        logger.error(f"Error searching mental health resources: {str(e)}")
        return jsonify({
            'error': 'Search failed',
            'message': 'Unable to search resources, but you can always access crisis support at /resources/crisis'
        }), 500


@mental_health_chat_bp.route('/resources/save', methods=['POST'])
def save_mental_health_resource():
    """
    Save a mental health resource for quick access
    """
    try:
        user_id = session.get('user_id', session.get('google_id'))
        if not user_id or user_id == 'guest':
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.get_json()
        resource_data = data.get('resource')
        
        if not resource_data:
            return jsonify({'error': 'Resource data required'}), 400
        
        # Save the resource
        saved = resources_service.save_user_resource(
            user_id=user_id,
            resource_type=resource_data.get('type', 'general'),
            resource_data=resource_data,
            is_primary=data.get('is_primary', False)
        )
        
        if saved:
            # Award points for taking proactive steps
            chat_integration.reward_chat_engagement(user_id, 'resource_saved')
            
            return jsonify({
                'success': True,
                'message': 'Resource saved successfully',
                'resource_id': saved.get('id')
            })
        else:
            return jsonify({
                'error': 'Failed to save resource'
            }), 500
            
    except Exception as e:
        logger.error(f"Error saving resource: {str(e)}")
        return jsonify({
            'error': 'Save failed',
            'message': str(e)
        }), 500


# Helper functions

def _check_previous_discussions(user_id: str) -> bool:
    """Check if user has had previous mental health discussions"""
    # This would check conversation history in your database
    # For now, return False
    return False


def _log_mental_health_interaction(user_id: str, interaction_type: str, severity: int):
    """Log mental health interactions for analytics and follow-up"""
    try:
        logger.info(f"Mental health interaction - User: {user_id}, Type: {interaction_type}, Severity: {severity}")
        
        # In production, this would:
        # 1. Store in database for analytics
        # 2. Trigger follow-up scheduling if needed
        # 3. Update user's mental health profile
        
    except Exception as e:
        logger.error(f"Failed to log interaction: {e}")


def _store_checkin_data(user_id: str, mood_rating: Optional[int], checkin_type: str):
    """Store check-in data for tracking"""
    try:
        # This would store in your database
        logger.info(f"Check-in stored - User: {user_id}, Mood: {mood_rating}, Type: {checkin_type}")
        
    except Exception as e:
        logger.error(f"Failed to store check-in: {e}")


def _get_fallback_resources(resource_type: str) -> List[Dict[str, Any]]:
    """Get fallback resources when no local options found"""
    if resource_type == 'therapy':
        return [
            {
                'name': 'BetterHelp',
                'description': 'Online therapy platform with financial aid available',
                'website': 'https://www.betterhelp.com',
                'type': 'online_therapy'
            },
            {
                'name': '7 Cups',
                'description': 'Free emotional support and affordable online therapy',
                'website': 'https://www.7cups.com',
                'type': 'online_therapy'
            },
            {
                'name': 'Open Path Collective',
                'description': 'Affordable therapy sessions $30-$80',
                'website': 'https://openpathcollective.org',
                'type': 'affordable_therapy'
            }
        ]
    elif resource_type == 'psychiatry':
        return [
            {
                'name': 'SAMHSA Treatment Locator',
                'description': 'Find mental health treatment facilities and programs',
                'website': 'https://findtreatment.samhsa.gov',
                'type': 'resource_directory'
            },
            {
                'name': 'Psychology Today',
                'description': 'Search for psychiatrists with filters for insurance and telehealth',
                'website': 'https://www.psychologytoday.com/us/psychiatrists',
                'type': 'provider_directory'
            }
        ]
    else:
        return []


# Export blueprint
__all__ = ['mental_health_chat_bp']


# AI-GENERATED [2024-12-01]
# CRITICAL: Mental health support must be accessible and non-judgmental
# NON-NEGOTIABLES: Always provide crisis resources, never diagnose
