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

API Routes Module

This module provides API endpoints for the NOUS application,
including AI integration with cost-optimized processing.
"""

import logging
from flask import Blueprint, request, jsonify, current_app

import json

# Import AI integration with cost optimization
try:
    from utils.ai_integration import generate_ai_text, analyze_document_content
    AI_INTEGRATION_AVAILABLE = True
except ImportError:
    AI_INTEGRATION_AVAILABLE = False
    logging.warning("AI Integration not available")

# Create blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Set up logging
logger = logging.getLogger(__name__)

@api_bp.route('/ai/ask', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def ai_ask():
    """
    AI Question-Answer endpoint with context-aware responses

    This endpoint uses the cost-optimized AI integration to provide
    context-aware answers to user questions.
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No request data provided'
            }), 400

        # Extract question and context
        question = data.get('question', '')
        context = data.get('context', {})

        if not question:
            return jsonify({
                'success': False,
                'error': 'No question provided'
            }), 400

        # Determine context type
        source = context.get('source', '')

        # Build prompt based on context
        if source == 'aa_big_book':
            # Build AA Big Book context
            chapter = context.get('chapter', '')
            content = context.get('content', '')

            prompt = f"""
            Question: {question}

            Context: This question is about chapter "{chapter}" from the Alcoholics Anonymous Big Book, which contains the following excerpt:

            {content}

            Please answer the question based on the given context from the AA Big Book. Focus on explaining the principles and concepts in a straightforward way that helps someone in recovery. If the question cannot be answered from the context, say so politely and suggest where in the Big Book they might find relevant information.
            """

            # Use the cost-optimized AI integration
            if AI_INTEGRATION_AVAILABLE:
                user_id = session.get('user', {}).get('id', 'demo_user') if ('user' in session and session['user']) else None
                result = generate_ai_text(
                    prompt=prompt,
                    task_type='aa_content_question',
                    user_id=user_id,
                    max_tokens=500,
                    temperature=0.7
                )

                if result.get('success'):
                    return jsonify({
                        'success': True,
                        'response': result.get('response', ''),
                        'service': result.get('service', ''),
                        'model': result.get('model', '')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': 'AI services not available'
                }), 503

        elif source == 'aa_speaker':
            # Handle AA speaker recording context
            speaker = context.get('speaker', '')
            title = context.get('title', '')
            description = context.get('description', '')

            prompt = f"""
            Question: {question}

            Context: This question is about the AA speaker recording titled "{title}" by {speaker}, which is described as:

            {description}

            Please answer the question based on the given context about this AA speaker recording. Focus on explaining the key principles and experiences shared by the speaker. If the question cannot be answered from the context, say so politely.
            """

            # Use the cost-optimized AI integration
            if AI_INTEGRATION_AVAILABLE:
                user_id = session.get('user', {}).get('id', 'demo_user') if ('user' in session and session['user']) else None
                result = generate_ai_text(
                    prompt=prompt,
                    task_type='aa_content_question',
                    user_id=user_id,
                    max_tokens=500,
                    temperature=0.7
                )

                if result.get('success'):
                    return jsonify({
                        'success': True,
                        'response': result.get('response', ''),
                        'service': result.get('service', ''),
                        'model': result.get('model', '')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': 'AI services not available'
                }), 503

        else:
            # Generic question without specific AA content context
            prompt = f"""
            Question: {question}

            Please provide a helpful, supportive response to this question about recovery, sobriety, or the AA program. Focus on principles rather than specific medical advice, and encourage the person to speak with their sponsor or healthcare provider for personal guidance.
            """

            # Use the cost-optimized AI integration
            if AI_INTEGRATION_AVAILABLE:
                user_id = session.get('user', {}).get('id', 'demo_user') if ('user' in session and session['user']) else None
                result = generate_ai_text(
                    prompt=prompt,
                    task_type='general_question',
                    user_id=user_id,
                    max_tokens=500,
                    temperature=0.7
                )

                if result.get('success'):
                    return jsonify({
                        'success': True,
                        'response': result.get('response', ''),
                        'service': result.get('service', ''),
                        'model': result.get('model', '')
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    }), 500
            else:
                return jsonify({
                    'success': False,
                    'error': 'AI services not available'
                }), 503

    except Exception as e:
        logger.error(f"Error in AI ask endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

@api_bp.route('/ai/analyze', methods=['POST'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def ai_analyze():
    """
    AI document analysis endpoint

    This endpoint uses the cost-optimized AI integration to analyze
    documents and extract key information.
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No request data provided'
            }), 400

        # Extract document text and type
        document_text = data.get('text', '')
        document_type = data.get('type', 'general')

        if not document_text:
            return jsonify({
                'success': False,
                'error': 'No document text provided'
            }), 400

        # Use the cost-optimized AI integration
        if AI_INTEGRATION_AVAILABLE:
            result = analyze_document_content(
                document_text=document_text,
                document_type=document_type,
                user_id=session.get('user', {}).get('id', 'demo_user')
            )

            if result.get('success', False):
                return jsonify(result)
            else:
                return jsonify({
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'AI services not available'
            }), 503

    except Exception as e:
        logger.error(f"Error in AI analyze endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500

@api_bp.route('/ai/stats', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def ai_stats():
    """
    Get AI usage statistics for the current user

    This endpoint provides information about AI service usage, costs,
    and optimizations applied for the current user.
    """
    try:
        from utils.ai_service_manager import get_ai_service_manager

        manager = get_ai_service_manager()
        if not manager:
            return jsonify({
                'success': False,
                'error': 'AI service manager not available'
            }), 503

        # Get usage data from database
        from models.ai_models import UserAIUsage
        from datetime import datetime, timedelta
        from sqlalchemy import func

        # Calculate dates
        today = datetime.utcnow().date()
        yesterday = today - timedelta(days=1)
        month_ago = today - timedelta(days=30)

        # Today's usage
        today_usage = UserAIUsage.query.filter(
            UserAIUsage.user_id == session.get('user', {}).get('id', 'demo_user'),
            func.date(UserAIUsage.timestamp) == today
        ).all()

        # Yesterday's usage
        yesterday_usage = UserAIUsage.query.filter(
            UserAIUsage.user_id == session.get('user', {}).get('id', 'demo_user'),
            func.date(UserAIUsage.timestamp) == yesterday
        ).all()

        # Last 30 days usage
        month_usage = UserAIUsage.query.filter(
            UserAIUsage.user_id == session.get('user', {}).get('id', 'demo_user'),
            UserAIUsage.timestamp >= month_ago
        ).all()

        # Calculate statistics
        stats = {
            'today': {
                'requests': len(today_usage),
                'total_tokens': sum(u.input_tokens + u.output_tokens for u in today_usage),
                'estimated_cost': sum(u.estimated_cost for u in today_usage),
                'success_rate': sum(1 for u in today_usage if u.success) / max(len(today_usage), 1) * 100
            },
            'yesterday': {
                'requests': len(yesterday_usage),
                'total_tokens': sum(u.input_tokens + u.output_tokens for u in yesterday_usage),
                'estimated_cost': sum(u.estimated_cost for u in yesterday_usage),
                'success_rate': sum(1 for u in yesterday_usage if u.success) / max(len(yesterday_usage), 1) * 100
            },
            'month': {
                'requests': len(month_usage),
                'total_tokens': sum(u.input_tokens + u.output_tokens for u in month_usage),
                'estimated_cost': sum(u.estimated_cost for u in month_usage),
                'success_rate': sum(1 for u in month_usage if u.success) / max(len(month_usage), 1) * 100
            }
        }

        # Get service breakdown
        service_breakdown = {}
        for usage in month_usage:
            service = usage.service
            if service not in service_breakdown:
                service_breakdown[service] = {
                    'requests': 0,
                    'total_tokens': 0,
                    'estimated_cost': 0
                }

            service_breakdown[service]['requests'] += 1
            service_breakdown[service]['total_tokens'] += (usage.input_tokens + usage.output_tokens)
            service_breakdown[service]['estimated_cost'] += usage.estimated_cost

        stats['service_breakdown'] = service_breakdown

        # Get optimization impact estimate
        if len(month_usage) > 0:
            # Estimated savings from optimization (assuming premium models would cost 2x more)
            premium_cost_estimate = sum(u.estimated_cost * 2 for u in month_usage)
            actual_cost = sum(u.estimated_cost for u in month_usage)
            savings_estimate = premium_cost_estimate - actual_cost

            stats['optimization_impact'] = {
                'estimated_savings': savings_estimate,
                'savings_percentage': (savings_estimate / premium_cost_estimate) * 100 if premium_cost_estimate > 0 else 0
            }
        else:
            stats['optimization_impact'] = {
                'estimated_savings': 0,
                'savings_percentage': 0
            }

        return jsonify({
            'success': True,
            'stats': stats
        })

    except ImportError:
        return jsonify({
            'success': False,
            'error': 'AI service statistics not available'
        }), 503
    except Exception as e:
        logger.error(f"Error in AI stats endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500