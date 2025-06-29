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

Adaptive AI Routes - Integration with NOUS chat system
Provides endpoints for adaptive learning and enhanced AI responses
"""

import logging
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any
from utils.adaptive_ai_system import (
    process_adaptive_request, 
    provide_user_feedback, 
    get_ai_insights
)

logger = logging.getLogger(__name__)

# Create blueprint
adaptive_ai_bp = Blueprint('adaptive_ai', __name__, url_prefix='/api/adaptive')

@adaptive_ai_bp.route('/chat', methods=['POST'])
def adaptive_chat():
    """Enhanced chat endpoint with adaptive learning"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user ID from session or use guest
        user_id = session.get('user_id', session.get('google_id', 'guest'))
        
        # Prepare context
        context = {
            'session_id': session.get('session_id', 'default'),
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': data.get('timestamp'),
            'conversation_history': data.get('history', []),
            'user_preferences': data.get('preferences', {}),
            'current_tasks': data.get('current_tasks', []),
            'user_mood': data.get('mood'),
            'location_context': data.get('location'),
            'time_of_day': data.get('time_of_day')
        }
        
        # Process request through adaptive AI system
        result = process_adaptive_request(user_id, message, context)
        
        # Format response for chat interface
        response = {
            'success': True,
            'message': result['result'].get('message', 'I understand your request.'),
            'response_data': {
                'processing_time': result['processing_time'],
                'agent_used': result['agent_used'],
                'confidence': min(1.0, max(0.0, result['reward'])),
                'adaptive_insights': {
                    'action_taken': result['result'].get('action_type'),
                    'tasks_created': result['result'].get('tasks_created', []),
                    'context_enhanced': result['result'].get('context_update', {}),
                    'learning_applied': result['result'].get('learning', {})
                }
            },
            'suggestions': _generate_suggestions(result, context),
            'metadata': {
                'adaptive_learning': True,
                'system_optimized': True,
                'user_profile_updated': True
            }
        }
        
        logger.info(f"Adaptive chat processed for user {user_id}: {message[:50]}...")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in adaptive chat: {str(e)}")
        return jsonify({
            'error': 'Failed to process adaptive chat request',
            'details': str(e) if logger.level <= logging.DEBUG else None
        }), 500

@adaptive_ai_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Submit user feedback for AI learning"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        feedback_score = data.get('rating')
        if feedback_score is None:
            return jsonify({'error': 'Rating is required'}), 400
        
        # Validate rating (1-5 scale, convert to 0-1)
        try:
            rating = float(feedback_score)
            if not (1 <= rating <= 5):
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            normalized_rating = (rating - 1) / 4  # Convert to 0-1 scale
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid rating format'}), 400
        
        user_id = session.get('user_id', session.get('google_id', 'guest'))
        
        session_context = {
            'feedback_type': data.get('feedback_type', 'general'),
            'message_context': data.get('message_context', ''),
            'session_id': session.get('session_id', 'default'),
            'timestamp': data.get('timestamp'),
            'response_time': data.get('response_time'),
            'helpful_aspects': data.get('helpful_aspects', []),
            'improvement_areas': data.get('improvement_areas', [])
        }
        
        # Submit feedback to adaptive AI system
        provide_user_feedback(user_id, normalized_rating, session_context)
        
        response = {
            'success': True,
            'message': 'Feedback received and learning updated',
            'feedback_processed': {
                'rating': rating,
                'normalized_score': normalized_rating,
                'learning_impact': 'Applied to user profile and system optimization'
            }
        }
        
        logger.info(f"Feedback processed for user {user_id}: rating={rating}")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error processing feedback: {str(e)}")
        return jsonify({
            'error': 'Failed to process feedback',
            'details': str(e) if logger.level <= logging.DEBUG else None
        }), 500

@adaptive_ai_bp.route('/insights', methods=['GET'])
def get_learning_insights():
    """Get AI learning insights and analytics"""
    try:
        user_id = session.get('user_id', session.get('google_id'))
        
        # Get insights from adaptive AI system
        insights = get_ai_insights(user_id if user_id != 'guest' else None)
        
        # Add user-specific context if authenticated
        user_specific = user_id is not None and user_id != 'guest'
        
        response = {
            'success': True,
            'insights': {
                'learning_metrics': {
                    'total_experiences': insights['total_experiences'],
                    'exploration_rate': round(insights['exploration_rate'], 3),
                    'average_response_time': round(insights['avg_response_time'], 3),
                    'average_reward': round(insights['avg_reward'], 3),
                    'personalized': user_specific
                },
                'system_performance': insights['system_metrics'],
                'user_profile': insights.get('user_profile') if user_specific else None,
                'recommendations': _generate_learning_recommendations(insights)
            },
            'metadata': {
                'timestamp': insights.get('timestamp'),
                'user_authenticated': user_specific,
                'insights_available': True
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error getting learning insights: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve learning insights',
            'details': str(e) if logger.level <= logging.DEBUG else None
        }), 500

@adaptive_ai_bp.route('/status', methods=['GET'])
def adaptive_ai_status():
    """Get adaptive AI system status"""
    try:
        # Get basic system insights
        insights = get_ai_insights()
        
        status = {
            'adaptive_ai_enabled': True,
            'learning_active': insights['total_experiences'] > 0,
            'system_health': {
                'cpu_usage': insights['system_metrics']['cpu_usage'],
                'memory_usage': insights['system_metrics']['memory_usage'],
                'performance_status': 'optimal' if insights['avg_response_time'] < 2.0 else 'degraded'
            },
            'learning_stats': {
                'experiences_collected': insights['total_experiences'],
                'current_exploration_rate': round(insights['exploration_rate'], 3),
                'average_performance': round(insights['avg_reward'], 3)
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting adaptive AI status: {str(e)}")
        return jsonify({
            'adaptive_ai_enabled': False,
            'error': 'Adaptive AI system unavailable',
            'details': str(e) if logger.level <= logging.DEBUG else None
        }), 500

def _generate_suggestions(result: Dict[str, Any], context: Dict[str, Any]) -> list:
    """Generate contextual suggestions based on AI result"""
    suggestions = []
    
    # Based on action taken
    action_type = result['result'].get('action_type')
    
    if action_type == 'TASK_CREATION':
        suggestions.extend([
            "Would you like me to set reminders for these tasks?",
            "Should I prioritize these tasks based on your schedule?",
            "Would you like to break down any of these tasks further?"
        ])
    elif action_type == 'CONTEXT_SWITCH':
        suggestions.extend([
            "I've updated my understanding of your preferences",
            "Would you like to explore related topics?",
            "Should I adjust my responses based on this context?"
        ])
    elif action_type == 'USER_ASSISTANCE':
        suggestions.extend([
            "Is there anything specific you'd like me to help with?",
            "Would you like me to learn more about your preferences?",
            "Should I provide more detailed explanations?"
        ])
    
    # Based on context
    if context.get('current_tasks'):
        suggestions.append("I can help manage your current tasks")
    
    if context.get('user_mood'):
        suggestions.append("I can adapt my responses to your current mood")
    
    return suggestions[:3]  # Limit to 3 suggestions

def _generate_learning_recommendations(insights: Dict[str, Any]) -> list:
    """Generate recommendations based on learning insights"""
    recommendations = []
    
    # Performance-based recommendations
    if insights['avg_response_time'] > 3.0:
        recommendations.append("System could benefit from optimization - consider reducing task complexity")
    
    if insights['avg_reward'] < 0.5:
        recommendations.append("AI performance could be improved with more user feedback")
    
    if insights['exploration_rate'] < 0.1:
        recommendations.append("System is in exploitation mode - learning from established patterns")
    elif insights['exploration_rate'] > 0.3:
        recommendations.append("System is actively exploring new response patterns")
    
    # System resource recommendations
    system_metrics = insights.get('system_metrics', {})
    if system_metrics.get('cpu_usage', 0) > 80:
        recommendations.append("High CPU usage detected - consider reducing concurrent operations")
    
    if system_metrics.get('memory_usage', 0) > 85:
        recommendations.append("High memory usage - system may benefit from optimization")
    
    # User profile recommendations
    user_profile = insights.get('user_profile')
    if user_profile:
        if user_profile.get('learning_rate', 0) < 0.05:
            recommendations.append("User profile learning rate is conservative - responses are stable")
        elif user_profile.get('learning_rate', 0) > 0.15:
            recommendations.append("User profile is actively adapting - responses will improve quickly")
    
    return recommendations[:4]  # Limit to 4 recommendations