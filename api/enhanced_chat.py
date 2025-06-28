"""
Enhanced Chat API - Adaptive AI Integration
Combines existing chat functionality with the new adaptive AI learning system
"""

import json
import logging
import time
from flask import Blueprint, request, jsonify, session
from typing import Dict, Any, Optional
from datetime import datetime

# Import existing chat functionality (with fallback)
try:
    from api.chat import ChatDispatcher
except (ImportError, TypeError):
    # Create a simple fallback dispatcher if the main one isn't available
    class ChatDispatcher:
        def __init__(self):
            self.handlers = {}
        
        async def dispatch(self, message: str, context: dict) -> dict:
            return {
                'success': True,
                'response': f"Processed: {message}",
                'handler': 'fallback',
                'type': 'fallback'
            }
from utils.unified_ai_service import UnifiedAIService
from utils.adaptive_ai_system import process_adaptive_request, provide_user_feedback, get_adaptive_ai

# NOUS Intelligence Hub
try:
    from utils.nous_intelligence_hub import get_nous_intelligence_hub, process_unified_request
    NOUS_HUB_AVAILABLE = True
    logger.info("NOUS Intelligence Hub connected to Enhanced Chat API")
except ImportError:
    NOUS_HUB_AVAILABLE = False
    logger.warning("NOUS Intelligence Hub not available - using standard enhanced chat")

logger = logging.getLogger(__name__)

# Create enhanced chat blueprint
enhanced_chat_bp = Blueprint('enhanced_chat', __name__, url_prefix='/api/enhanced')

# Initialize services
chat_dispatcher = ChatDispatcher()
ai_service = UnifiedAIService()

@enhanced_chat_bp.route('/chat', methods=['POST'])
def enhanced_chat():
    """
    Enhanced chat endpoint that combines:
    1. Existing chat command routing
    2. Adaptive AI learning system
    3. Unified AI service for responses
    """
    try:
        start_time = time.time()
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get user context
        user_id = session.get('user_id', session.get('google_id', 'guest'))
        session_id = session.get('session_id', f"session_{int(time.time())}")
        
        # Prepare comprehensive context
        context = {
            'session_id': session_id,
            'user_agent': request.headers.get('User-Agent', ''),
            'timestamp': datetime.now().isoformat(),
            'conversation_history': data.get('history', []),
            'user_preferences': data.get('preferences', {}),
            'current_tasks': data.get('current_tasks', []),
            'user_mood': data.get('mood'),
            'location_context': data.get('location'),
            'time_of_day': datetime.now().hour,
            'request_type': data.get('type', 'chat'),
            'urgency': data.get('urgency', 'normal'),
            'previous_context': session.get('previous_context', {})
        }
        
        # Store context for next interaction
        session['previous_context'] = context
        
        # Step 1: Try existing chat command routing first
        command_result = None
        try:
            # Check if message is a command
            if message.startswith('/') or any(cmd in message.lower() for cmd in ['help', 'status', 'weather', 'tasks']):
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                command_result = loop.run_until_complete(chat_dispatcher.dispatch(message, context))
                loop.close()
        except Exception as e:
            logger.debug(f"Command routing failed: {str(e)}")
        
        # NOUS Enhancement: Use Intelligence Hub for comprehensive processing
        if NOUS_HUB_AVAILABLE:
            # Process through NOUS Intelligence Hub for maximum intelligence
            integrated_result = process_unified_request(user_id, message, context)
            
            # Extract components from integrated result
            adaptive_result = integrated_result.get('primary_response', {})
            ai_response = integrated_result.get('enhanced_features', {}).get('ai_response', {})
            intelligence_insights = integrated_result.get('intelligence_insights', {})
            
            logger.info(f"NOUS Intelligence Hub processed request with {len(intelligence_insights)} intelligence services")
        else:
            # Fallback to standard enhanced processing
            # Step 2: Process through adaptive AI system
            adaptive_result = process_adaptive_request(user_id, message, context)
            
            # Step 3: Generate AI response using unified service
            ai_response = None
            try:
                if not command_result or not command_result.get('success'):
                    # Use adaptive AI insights to improve response
                    enhanced_message = message
                    if adaptive_result['result'].get('context_update'):
                        enhanced_message += f" [Context: {adaptive_result['result']['context_update']}]"
                    
                    ai_response = ai_service.chat_completion([
                        {"role": "system", "content": _build_system_prompt(context, adaptive_result)},
                        {"role": "user", "content": enhanced_message}
                    ], user_id=user_id, context=context)
            except Exception as e:
                logger.warning(f"AI response generation failed: {str(e)}")
        
        # Step 4: Combine and format response
        response = _combine_responses(command_result, adaptive_result, ai_response, context)
        
        # Step 5: Track conversation history
        _update_conversation_history(user_id, message, response, context)
        
        # Calculate total processing time
        processing_time = time.time() - start_time
        response['processing_time'] = processing_time
        
        logger.info(f"Enhanced chat processed for user {user_id}: {message[:50]}... ({processing_time:.2f}s)")
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error in enhanced chat: {str(e)}")
        return jsonify({
            'error': 'Failed to process enhanced chat request',
            'message': 'An error occurred while processing your message',
            'details': str(e) if logger.level <= logging.DEBUG else None
        }), 500

@enhanced_chat_bp.route('/feedback', methods=['POST'])
def enhanced_feedback():
    """Enhanced feedback endpoint with multiple feedback types"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        feedback_type = data.get('type', 'rating')  # rating, helpful, accuracy, speed
        user_id = session.get('user_id', session.get('google_id', 'guest'))
        
        # Process different types of feedback
        if feedback_type == 'rating':
            rating = data.get('rating')
            if rating is None or not (1 <= rating <= 5):
                return jsonify({'error': 'Rating must be between 1 and 5'}), 400
            
            normalized_rating = (rating - 1) / 4  # Convert to 0-1 scale
            provide_user_feedback(user_id, normalized_rating, {
                'feedback_type': 'rating',
                'message_context': data.get('message_context', ''),
                'session_id': session.get('session_id', 'default')
            })
            
        elif feedback_type == 'binary':
            helpful = data.get('helpful')  # True/False
            if helpful is None:
                return jsonify({'error': 'Helpful flag is required'}), 400
            
            score = 1.0 if helpful else 0.0
            provide_user_feedback(user_id, score, {
                'feedback_type': 'binary',
                'helpful': helpful,
                'message_context': data.get('message_context', ''),
                'session_id': session.get('session_id', 'default')
            })
            
        elif feedback_type == 'detailed':
            accuracy = data.get('accuracy', 3)  # 1-5
            speed = data.get('speed', 3)  # 1-5
            helpfulness = data.get('helpfulness', 3)  # 1-5
            
            # Calculate weighted score
            weights = {'accuracy': 0.4, 'speed': 0.2, 'helpfulness': 0.4}
            total_score = (
                (accuracy - 1) / 4 * weights['accuracy'] +
                (speed - 1) / 4 * weights['speed'] +
                (helpfulness - 1) / 4 * weights['helpfulness']
            )
            
            provide_user_feedback(user_id, total_score, {
                'feedback_type': 'detailed',
                'accuracy': accuracy,
                'speed': speed,
                'helpfulness': helpfulness,
                'message_context': data.get('message_context', ''),
                'session_id': session.get('session_id', 'default')
            })
        
        return jsonify({
            'success': True,
            'message': 'Feedback received and learning updated',
            'feedback_type': feedback_type
        })
        
    except Exception as e:
        logger.error(f"Error processing enhanced feedback: {str(e)}")
        return jsonify({
            'error': 'Failed to process feedback',
            'details': str(e) if logger.level <= logging.DEBUG else None
        }), 500

@enhanced_chat_bp.route('/analytics', methods=['GET'])
def chat_analytics():
    """Get chat analytics and learning insights"""
    try:
        user_id = session.get('user_id', session.get('google_id'))
        
        # Get adaptive AI insights
        adaptive_ai = get_adaptive_ai()
        insights = adaptive_ai.get_learning_insights(user_id if user_id != 'guest' else None)
        
        # Get conversation statistics
        conversation_stats = _get_conversation_stats(user_id)
        
        # Combine analytics
        analytics = {
            'learning_insights': insights,
            'conversation_stats': conversation_stats,
            'system_performance': {
                'avg_response_time': insights.get('avg_response_time', 0),
                'user_satisfaction': insights.get('avg_reward', 0),
                'total_interactions': insights.get('total_experiences', 0)
            },
            'recommendations': _generate_usage_recommendations(insights, conversation_stats)
        }
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting chat analytics: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve analytics',
            'details': str(e) if logger.level <= logging.DEBUG else None
        }), 500

@enhanced_chat_bp.route('/status', methods=['GET'])
def enhanced_status():
    """Get status of all enhanced chat components"""
    try:
        # Check component availability
        status = {
            'enhanced_chat_enabled': True,
            'components': {
                'chat_dispatcher': _check_dispatcher_health(),
                'adaptive_ai': _check_adaptive_ai_health(),
                'ai_service': _check_ai_service_health()
            },
            'system_metrics': get_adaptive_ai().resource_manager.get_system_metrics(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Overall health
        status['overall_health'] = 'healthy' if all(
            comp['status'] == 'healthy' for comp in status['components'].values()
        ) else 'degraded'
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Error getting enhanced chat status: {str(e)}")
        return jsonify({
            'enhanced_chat_enabled': False,
            'error': 'Status check failed',
            'details': str(e) if logger.level <= logging.DEBUG else None
        }), 500

# Helper functions

def _build_system_prompt(context: Dict[str, Any], adaptive_result: Dict[str, Any]) -> str:
    """Build enhanced system prompt with adaptive AI insights"""
    base_prompt = """You are NOUS, an intelligent personal assistant focused on helping users manage their lives effectively.
    
Key capabilities:
- Task management and organization
- Context-aware responses
- Learning from user interactions
- Adaptive behavior based on user preferences"""
    
    # Add context-specific information
    if context.get('user_mood'):
        base_prompt += f"\n\nUser's current mood: {context['user_mood']}"
    
    if context.get('time_of_day'):
        hour = context['time_of_day']
        if 5 <= hour < 12:
            base_prompt += "\n\nIt's morning - user may be planning their day."
        elif 12 <= hour < 17:
            base_prompt += "\n\nIt's afternoon - user may be working or managing tasks."
        elif 17 <= hour < 21:
            base_prompt += "\n\nIt's evening - user may be reviewing their day or planning tomorrow."
        else:
            base_prompt += "\n\nIt's late night - keep responses brief and relevant."
    
    # Add adaptive AI insights
    if adaptive_result['result'].get('action_type'):
        base_prompt += f"\n\nRecommended action: {adaptive_result['result']['action_type']}"
    
    if adaptive_result['result'].get('tasks_created'):
        base_prompt += f"\n\nSuggested tasks: {len(adaptive_result['result']['tasks_created'])} tasks identified"
    
    return base_prompt

def _combine_responses(command_result: Optional[Dict[str, Any]], 
                      adaptive_result: Dict[str, Any], 
                      ai_response: Optional[Dict[str, Any]], 
                      context: Dict[str, Any]) -> Dict[str, Any]:
    """Combine responses from different sources"""
    response = {
        'success': True,
        'timestamp': datetime.now().isoformat(),
        'sources': []
    }
    
    # Primary response source
    if command_result and command_result.get('success'):
        response['message'] = command_result.get('response', '')
        response['type'] = 'command'
        response['sources'].append('command_router')
    elif ai_response and ai_response.get('response'):
        response['message'] = ai_response['response']
        response['type'] = 'ai_generated'
        response['sources'].append('ai_service')
    else:
        response['message'] = adaptive_result['result'].get('message', 'I understand your request.')
        response['type'] = 'adaptive'
        response['sources'].append('adaptive_ai')
    
    # Add adaptive insights
    response['adaptive_insights'] = {
        'agent_used': adaptive_result.get('agent_used'),
        'confidence': min(1.0, max(0.0, adaptive_result.get('reward', 0.5))),
        'action_taken': adaptive_result['result'].get('action_type'),
        'learning_applied': adaptive_result.get('learning_update', False)
    }
    
    # Add suggestions
    response['suggestions'] = _generate_contextual_suggestions(adaptive_result, context)
    
    # Add metadata
    response['metadata'] = {
        'enhanced_mode': True,
        'user_authenticated': context.get('session_id') != 'guest',
        'processing_components': len(response['sources'])
    }
    
    return response

def _update_conversation_history(user_id: str, message: str, response: Dict[str, Any], context: Dict[str, Any]):
    """Update conversation history for the user"""
    try:
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        conversation_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_message': message,
            'assistant_response': response.get('message', ''),
            'response_type': response.get('type', 'unknown'),
            'confidence': response.get('adaptive_insights', {}).get('confidence', 0.5),
            'processing_time': response.get('processing_time', 0)
        }
        
        session['chat_history'].append(conversation_entry)
        
        # Keep only last 50 conversations to prevent session bloat
        if len(session['chat_history']) > 50:
            session['chat_history'] = session['chat_history'][-50:]
        
        session.modified = True
        
    except Exception as e:
        logger.warning(f"Failed to update conversation history: {str(e)}")

def _get_conversation_stats(user_id: Optional[str]) -> Dict[str, Any]:
    """Get conversation statistics for the user"""
    try:
        history = session.get('chat_history', [])
        
        if not history:
            return {'total_conversations': 0}
        
        # Calculate statistics
        total_conversations = len(history)
        avg_confidence = sum(conv.get('confidence', 0.5) for conv in history) / total_conversations
        avg_processing_time = sum(conv.get('processing_time', 0) for conv in history) / total_conversations
        
        # Response type distribution
        response_types = {}
        for conv in history:
            resp_type = conv.get('response_type', 'unknown')
            response_types[resp_type] = response_types.get(resp_type, 0) + 1
        
        return {
            'total_conversations': total_conversations,
            'average_confidence': round(avg_confidence, 3),
            'average_processing_time': round(avg_processing_time, 3),
            'response_type_distribution': response_types,
            'recent_activity': len([conv for conv in history[-10:] if conv]) # Last 10 conversations
        }
        
    except Exception as e:
        logger.warning(f"Failed to get conversation stats: {str(e)}")
        return {'total_conversations': 0, 'error': str(e)}

def _generate_contextual_suggestions(adaptive_result: Dict[str, Any], context: Dict[str, Any]) -> list:
    """Generate contextual suggestions based on adaptive AI result and context"""
    suggestions = []
    
    # Based on adaptive AI action
    action_type = adaptive_result['result'].get('action_type')
    if action_type == 'TASK_CREATION':
        suggestions.extend([
            "Set reminders for these tasks",
            "Prioritize tasks by importance",
            "Break down complex tasks"
        ])
    elif action_type == 'CONTEXT_SWITCH':
        suggestions.extend([
            "Explore related topics",
            "Adjust response style",
            "Update preferences"
        ])
    
    # Based on time of day
    hour = context.get('time_of_day', 12)
    if 6 <= hour < 9:
        suggestions.append("Plan your day")
    elif 17 <= hour < 20:
        suggestions.append("Review today's progress")
    
    # Based on user mood
    if context.get('user_mood') == 'stressed':
        suggestions.append("Try relaxation techniques")
    
    return suggestions[:3]  # Limit to 3 suggestions

def _generate_usage_recommendations(insights: Dict[str, Any], conversation_stats: Dict[str, Any]) -> list:
    """Generate usage recommendations based on analytics"""
    recommendations = []
    
    # Based on conversation patterns
    if conversation_stats.get('total_conversations', 0) > 20:
        avg_confidence = conversation_stats.get('average_confidence', 0.5)
        if avg_confidence < 0.6:
            recommendations.append("Try providing more specific details in your requests")
        elif avg_confidence > 0.8:
            recommendations.append("Your interactions are highly effective - great job!")
    
    # Based on response times
    avg_time = conversation_stats.get('average_processing_time', 0)
    if avg_time > 3.0:
        recommendations.append("Consider simplifying requests for faster responses")
    
    # Based on learning insights
    if insights.get('exploration_rate', 0) < 0.1:
        recommendations.append("System has learned your preferences well")
    
    return recommendations[:3]

def _check_dispatcher_health() -> Dict[str, Any]:
    """Check chat dispatcher health"""
    try:
        # Test basic functionality
        test_context = {'test': True}
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(chat_dispatcher.dispatch("health", test_context))
        loop.close()
        
        return {
            'status': 'healthy' if result.get('success') else 'degraded',
            'component': 'chat_dispatcher',
            'test_passed': result.get('success', False)
        }
    except Exception as e:
        return {
            'status': 'error',
            'component': 'chat_dispatcher',
            'error': str(e)
        }

def _check_adaptive_ai_health() -> Dict[str, Any]:
    """Check adaptive AI system health"""
    try:
        adaptive_ai = get_adaptive_ai()
        insights = adaptive_ai.get_learning_insights()
        
        return {
            'status': 'healthy',
            'component': 'adaptive_ai',
            'total_experiences': insights.get('total_experiences', 0),
            'system_metrics_available': bool(insights.get('system_metrics'))
        }
    except Exception as e:
        return {
            'status': 'error',
            'component': 'adaptive_ai',
            'error': str(e)
        }

def _check_ai_service_health() -> Dict[str, Any]:
    """Check AI service health"""
    try:
        # Check available API keys as a health indicator
        available_providers = 0
        if ai_service.openrouter_key:
            available_providers += 1
        if ai_service.huggingface_key:
            available_providers += 1
        if ai_service.gemini_key:
            available_providers += 1
        if ai_service.openai_key:
            available_providers += 1
        
        return {
            'status': 'healthy' if available_providers > 0 else 'degraded',
            'component': 'ai_service',
            'available_providers': available_providers,
            'total_cost': getattr(ai_service, 'total_cost', 0)
        }
    except Exception as e:
        return {
            'status': 'error',
            'component': 'ai_service',
            'error': str(e)
        }

# Export the blueprint
__all__ = ['enhanced_chat_bp']