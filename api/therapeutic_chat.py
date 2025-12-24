"""
Therapeutic Chat API
Emotion-aware chat interface that integrates DBT/CBT skills with adaptive responses
"""

import os
import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
from werkzeug.utils import secure_filename

# Import therapeutic assistant
from services.emotion_aware_therapeutic_assistant import therapeutic_assistant
from services.personalization_service import personalization_service

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
therapeutic_chat_bp = Blueprint('therapeutic_chat', __name__, url_prefix='/api/therapeutic')

def get_user_id():
    """Get current user ID"""
    return str(get_current_user().get("id") if get_current_user() else None) if is_authenticated() else session.get('guest_id', 'guest')

@therapeutic_chat_bp.route('/chat', methods=['POST'])
def therapeutic_chat():
    """
    Main therapeutic chat endpoint with emotion awareness and skill recommendations
    Supports both text and voice input
    """
    try:
        user_id = get_user_id()
        
        # Get request data
        if request.is_json:
            data = request.json
            message = data.get('message', '')
            context = data.get('context', {})
        else:
            message = request.form.get('message', '')
            context = {}
        
        if not message:
            return jsonify({
                'success': False,
                'error': 'No message provided'
            }), 400
        
        # Handle audio if provided
        audio_data = None
        if 'audio' in request.files:
            audio_file = request.files['audio']
            if audio_file and audio_file.filename:
                audio_data = audio_file.read()
        
        # Get therapeutic response
        therapeutic_response = therapeutic_assistant.get_therapeutic_response(
            user_input=message,
            user_id=user_id,
            audio_data=audio_data,
            context=context
        )
        
        return jsonify({
            'success': True,
            'response': therapeutic_response['response']['text'],
            'emotion_analysis': therapeutic_response['emotion_analysis'],
            'skills_recommended': therapeutic_response['skills_recommended'],
            'skill_suggestions': therapeutic_response['response'].get('skill_suggestions', []),
            'immediate_actions': therapeutic_response['response'].get('immediate_actions', []),
            'follow_up_suggestions': therapeutic_response.get('follow_up_suggestions', []),
            'therapeutic_approach': therapeutic_response['therapeutic_approach'],
            'tone': therapeutic_response['response']['tone'],
            'quick_replies': therapeutic_response['response'].get('quick_replies', []),
            'content_used': therapeutic_response['response'].get('content_used'),
            'content_title': therapeutic_response['response'].get('content_title'),
            'content_summary': therapeutic_response['response'].get('content_summary'),
            'content_steps': therapeutic_response['response'].get('content_steps', []),
            'content_safety': therapeutic_response['response'].get('content_safety', {}),
            'nlu_tags': therapeutic_response.get('nlu_tags', []),
            'dialogue_mode': therapeutic_response['response'].get('dialogue_mode'),
            'locale': therapeutic_response['response'].get('locale', 'en'),
            'timestamp': therapeutic_response['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Error in therapeutic chat: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Sorry, I encountered an issue processing your message. Please try again.',
            'fallback_response': "I'm here to support you. What's on your mind today?"
        }), 500

@therapeutic_chat_bp.route('/emotion-analysis', methods=['POST'])
def analyze_emotion():
    """
    Standalone emotion analysis endpoint for text and/or audio
    """
    try:
        user_id = get_user_id()
        
        # Get text input
        text_input = None
        if request.is_json:
            text_input = request.json.get('text')
        else:
            text_input = request.form.get('text')
        
        # Handle audio if provided
        audio_data = None
        if 'audio' in request.files:
            audio_file = request.files['audio']
            if audio_file and audio_file.filename:
                audio_data = audio_file.read()
        
        if not text_input and not audio_data:
            return jsonify({
                'success': False,
                'error': 'Either text or audio input is required'
            }), 400
        
        # Analyze emotional state
        emotion_analysis = therapeutic_assistant.analyze_emotional_state(
            text_input=text_input,
            audio_data=audio_data,
            user_id=user_id
        )
        
        return jsonify({
            'success': True,
            'emotion_analysis': emotion_analysis
        })
        
    except Exception as e:
        logger.error(f"Error analyzing emotion: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to analyze emotion at this time'
        }), 500

@therapeutic_chat_bp.route('/skill-recommendations', methods=['POST'])
def get_skill_recommendations():
    """
    Get personalized skill recommendations based on current emotional state
    """
    try:
        user_id = get_user_id()
        
        if request.is_json:
            data = request.json
            emotion = data.get('emotion', 'neutral')
            intensity = data.get('intensity', 'moderate')
            context_factors = data.get('context_factors', [])
        else:
            emotion = request.form.get('emotion', 'neutral')
            intensity = request.form.get('intensity', 'moderate')
            context_factors = request.form.getlist('context_factors')
        
        # Create emotion analysis dict
        emotion_analysis = {
            'primary_emotion': emotion,
            'emotional_intensity': intensity,
            'context_factors': context_factors
        }
        
        # Get user profile
        user_profile = therapeutic_assistant._get_user_therapeutic_profile(user_id)
        
        # Select therapeutic approach
        approach = therapeutic_assistant._select_therapeutic_approach(
            emotion_analysis, user_profile
        )
        
        # Get skill recommendations
        skill_recommendations = therapeutic_assistant._get_contextual_skill_recommendations(
            emotion, user_profile, approach
        )
        
        # Format suggestions
        skill_suggestions = therapeutic_assistant._format_skill_suggestions(skill_recommendations)
        
        return jsonify({
            'success': True,
            'recommendations': skill_recommendations,
            'skill_suggestions': skill_suggestions,
            'therapeutic_approach': approach,
            'immediate_actions': therapeutic_assistant._get_immediate_actions(emotion, intensity)
        })
        
    except Exception as e:
        logger.error(f"Error getting skill recommendations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to get skill recommendations at this time'
        }), 500

@therapeutic_chat_bp.route('/voice-therapeutic', methods=['POST'])
def voice_therapeutic_response():
    """
    Voice-focused therapeutic response with audio emotion analysis
    """
    try:
        user_id = get_user_id()
        
        # Check for audio file
        if 'audio' not in request.files:
            return jsonify({
                'success': False,
                'error': 'Audio file is required'
            }), 400
        
        audio_file = request.files['audio']
        if not audio_file or not audio_file.filename:
            return jsonify({
                'success': False,
                'error': 'Valid audio file is required'
            }), 400
        
        audio_data = audio_file.read()
        
        # Get any accompanying text
        text_input = request.form.get('text', '')
        locale = request.form.get('locale')
        
        # Get therapeutic response with focus on audio analysis
        therapeutic_response = therapeutic_assistant.get_therapeutic_response(
            user_input=text_input,
            user_id=user_id,
            audio_data=audio_data,
            context={'input_mode': 'voice', 'locale': locale} if locale else {'input_mode': 'voice'}
        )
        
        return jsonify({
            'success': True,
            'response': therapeutic_response['response']['text'],
            'emotion_analysis': therapeutic_response['emotion_analysis'],
            'voice_characteristics': therapeutic_response['emotion_analysis'].get('voice_characteristics', {}),
            'skills_recommended': therapeutic_response['skills_recommended'],
            'therapeutic_approach': therapeutic_response['therapeutic_approach'],
            'immediate_actions': therapeutic_response['response'].get('immediate_actions', []),
            'quick_replies': therapeutic_response['response'].get('quick_replies', []),
            'content_used': therapeutic_response['response'].get('content_used'),
            'content_title': therapeutic_response['response'].get('content_title'),
            'content_summary': therapeutic_response['response'].get('content_summary'),
            'content_steps': therapeutic_response['response'].get('content_steps', []),
            'content_safety': therapeutic_response['response'].get('content_safety', {}),
            'nlu_tags': therapeutic_response.get('nlu_tags', []),
            'dialogue_mode': therapeutic_response['response'].get('dialogue_mode'),
            'locale': therapeutic_response['response'].get('locale', 'en'),
            'timestamp': therapeutic_response['timestamp']
        })
        
    except Exception as e:
        logger.error(f"Error in voice therapeutic response: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to process voice input at this time'
        }), 500

@therapeutic_chat_bp.route('/user-profile', methods=['GET'])
def get_user_therapeutic_profile():
    """
    Get user's therapeutic profile and history
    """
    try:
        user_id = get_user_id()
        
        if user_id == 'guest':
            return jsonify({
                'success': True,
                'profile': {
                    'preferred_approach': 'balanced',
                    'skill_effectiveness': {},
                    'recent_emotions': [],
                    'note': 'Limited profile for guest user'
                }
            })
        
        profile = therapeutic_assistant._get_user_therapeutic_profile(user_id)
        
        return jsonify({
            'success': True,
            'profile': profile
        })
        
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to retrieve user profile'
        }), 500

@therapeutic_chat_bp.route('/context-suggestions', methods=['POST'])
def get_context_suggestions():
    """
    Get contextual suggestions based on time, emotion, and user history
    """
    try:
        user_id = get_user_id()
        
        if request.is_json:
            data = request.json
            current_emotion = data.get('emotion', 'neutral')
            time_context = data.get('time_context', {})
        else:
            current_emotion = request.form.get('emotion', 'neutral')
            time_context = {}
        
        # Get current hour
        current_hour = datetime.now().hour
        
        suggestions = []
        
        # Time-based suggestions
        if 6 <= current_hour < 9:
            suggestions.append("Start your day with a mindfulness check-in")
        elif 12 <= current_hour < 14:
            suggestions.append("Take a mindful lunch break")
        elif 17 <= current_hour < 20:
            suggestions.append("Reflect on your day and practice gratitude")
        elif 20 <= current_hour or current_hour < 6:
            suggestions.append("Wind down with relaxation techniques")
        
        # Emotion-based suggestions
        if current_emotion == 'anxious':
            suggestions.append("Try the 5-4-3-2-1 grounding technique")
        elif current_emotion == 'sad':
            suggestions.append("Consider a gentle self-care activity")
        elif current_emotion == 'angry':
            suggestions.append("Take a few deep breaths before responding")
        
        # General therapeutic suggestions
        suggestions.extend([
            "Log your current mood",
            "Practice a DBT or CBT skill",
            "Connect with your support network"
        ])
        
        return jsonify({
            'success': True,
            'suggestions': suggestions[:5],  # Limit to 5 suggestions
            'context': {
                'current_hour': current_hour,
                'emotion': current_emotion
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting context suggestions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Unable to generate suggestions at this time'
        }), 500

@therapeutic_chat_bp.route('/emergency-support', methods=['POST'])
def emergency_support():
    """
    Emergency support endpoint for crisis situations
    """
    try:
        user_id = get_user_id()
        
        if request.is_json:
            data = request.json
            message = data.get('message', '')
            crisis_type = data.get('crisis_type', 'general')
        else:
            message = request.form.get('message', '')
            crisis_type = request.form.get('crisis_type', 'general')
        
        # Immediate crisis response
        crisis_responses = {
            'general': {
                'response': "I'm concerned about you right now. Your safety is most important. Please consider reaching out to a crisis helpline or emergency services if you're in immediate danger.",
                'immediate_actions': [
                    "Call 988 (Suicide & Crisis Lifeline) if in the US",
                    "Text 'HELLO' to 741741 (Crisis Text Line)",
                    "Call emergency services (911) if in immediate danger"
                ],
                'skills': ['TIPP', 'Radical Acceptance', 'Crisis Survival']
            },
            'suicide': {
                'response': "I'm very concerned about you. Please reach out for immediate help. You don't have to go through this alone.",
                'immediate_actions': [
                    "Call 988 (Suicide & Crisis Lifeline) immediately",
                    "Go to your nearest emergency room",
                    "Call 911 if in immediate danger",
                    "Reach out to a trusted friend or family member"
                ],
                'skills': ['Crisis Survival', 'TIPP', 'Reach out for help']
            },
            'self_harm': {
                'response': "I can see you're in a lot of pain right now. Let's focus on keeping you safe and finding healthier ways to cope.",
                'immediate_actions': [
                    "Remove or put away anything that could be used for self-harm",
                    "Call a crisis line: 988 or text 741741",
                    "Use ice cubes or rubber band as alternatives",
                    "Reach out to someone you trust"
                ],
                'skills': ['Self-Soothing', 'TIPP', 'Distress Tolerance']
            }
        }
        
        crisis_info = crisis_responses.get(crisis_type, crisis_responses['general'])
        
        # Log crisis interaction (important for safety)
        logger.warning(f"Crisis support accessed by user {user_id}: {crisis_type}")
        
        return jsonify({
            'success': True,
            'crisis_response': True,
            'response': crisis_info['response'],
            'immediate_actions': crisis_info['immediate_actions'],
            'recommended_skills': crisis_info['skills'],
            'professional_help': {
                'crisis_text_line': '741741',
                'suicide_lifeline': '988',
                'emergency': '911'
            },
            'message': 'Professional help is available 24/7. Please reach out.'
        })
        
    except Exception as e:
        logger.error(f"Error in emergency support: {str(e)}")
        return jsonify({
            'success': True,  # Always succeed for safety
            'crisis_response': True,
            'response': "Please reach out for immediate help. Call 988 (crisis line) or 911 if you're in danger.",
            'immediate_actions': ["Call 988", "Call 911 if in immediate danger"],
            'error': 'System error, but help is still available'
        })

@therapeutic_chat_bp.route('/feedback', methods=['POST'])
def feedback():
    """
    Capture user feedback (helpful/not) for personalization.
    """
    try:
        user_id = get_user_id()
        if request.is_json:
            data = request.json
        else:
            data = request.form

        content_id = data.get('content_id')
        helpful = data.get('helpful')
        tags = data.get('tags', [])
        locale = data.get('locale', 'en')

        if content_id is None:
            return jsonify({'success': False, 'error': 'content_id is required'}), 400

        # Cast helpful to bool if passed as string
        if isinstance(helpful, str):
            helpful = helpful.lower() in ['true', '1', 'yes', 'y']

        if isinstance(tags, str):
            try:
                tags = json.loads(tags)
            except Exception:
                tags = [tags]

        personalization_service.record_feedback(
            user_id=user_id,
            content_id=content_id,
            tags=tags if isinstance(tags, list) else [],
            helpful=helpful,
            locale=locale
        )

        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error recording feedback: {str(e)}")
        return jsonify({'success': False, 'error': 'Unable to record feedback'}), 500
