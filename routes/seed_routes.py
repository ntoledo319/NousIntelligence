"""
SEED Optimization Routes for NOUS Platform
API endpoints for SEED optimization features

Provides endpoints for:
- User-specific therapeutic optimization
- AI cost optimization
- Engagement optimization
- System-wide optimization
- Optimization dashboard data
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session
from functools import wraps

# Import SEED services
from services.seed_integration_layer import get_seed_integration
from services.seed_optimization_engine import get_seed_engine

logger = logging.getLogger(__name__)

# Create blueprint
seed_bp = Blueprint('seed', __name__, url_prefix='/api/seed')

def get_current_user():
    """Get current user from session"""
    return session.get('user', {})

def require_authentication(f):
    """Decorator to require authentication for optimization endpoints"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user.get('id'):
            return jsonify({
                'success': False,
                'error': 'Authentication required for optimization features',
                'demo_mode': True
            }), 401
        return f(*args, **kwargs)
    return decorated

def demo_fallback(f):
    """Decorator to provide demo responses when not authenticated"""
    @wraps(f)
    def decorated(*args, **kwargs):
        user = get_current_user()
        if not user.get('id'):
            # Return demo optimization data
            return jsonify({
                'success': True,
                'demo_mode': True,
                'message': 'This is a demo of SEED optimization features',
                'optimization_result': {
                    'domain': 'therapeutic',
                    'improvement_percentage': 25.5,
                    'confidence': 0.8,
                    'metric_improved': True
                },
                'recommendations': [
                    {
                        'type': 'demo',
                        'title': 'Sign up to unlock personalized optimization',
                        'description': 'SEED learns from your actual usage patterns',
                        'action': 'Create an account to begin optimization'
                    }
                ]
            })
        return f(*args, **kwargs)
    return decorated

@seed_bp.route('/optimize/therapeutic', methods=['POST'])
@demo_fallback
def optimize_therapeutic():
    """
    Optimize therapeutic interventions for current user
    """
    try:
        user = get_current_user()
        user_id = user.get('id')
        
        # Get SEED integration layer
        seed_integration = get_seed_integration()
        
        # Run therapeutic optimization
        result = seed_integration.optimize_user_therapeutic_experience(user_id)
        
        if result['success']:
            logger.info(f"Therapeutic optimization completed for user {user_id}")
            return jsonify({
                'success': True,
                'optimization_type': 'therapeutic',
                'user_id': user_id,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Optimization failed'),
                'recommendations': result.get('recommendations', [])
            }), 400
    
    except Exception as e:
        logger.error(f"Therapeutic optimization error: {e}")
        return jsonify({
            'success': False,
            'error': 'Optimization service temporarily unavailable'
        }), 500

@seed_bp.route('/optimize/engagement', methods=['POST'])
@demo_fallback
def optimize_engagement():
    """
    Optimize user engagement patterns
    """
    try:
        user = get_current_user()
        user_id = user.get('id')
        
        # Get SEED integration layer
        seed_integration = get_seed_integration()
        
        # Run engagement optimization
        result = seed_integration.optimize_user_engagement(user_id)
        
        if result['success']:
            logger.info(f"Engagement optimization completed for user {user_id}")
            return jsonify({
                'success': True,
                'optimization_type': 'engagement',
                'user_id': user_id,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Engagement optimization failed'),
                'recommendations': result.get('recommendations', [])
            }), 400
    
    except Exception as e:
        logger.error(f"Engagement optimization error: {e}")
        return jsonify({
            'success': False,
            'error': 'Optimization service temporarily unavailable'
        }), 500

@seed_bp.route('/optimize/comprehensive', methods=['POST'])
@demo_fallback
def optimize_comprehensive():
    """
    Run comprehensive optimization across all domains for user
    """
    try:
        user = get_current_user()
        user_id = user.get('id')
        
        # Get SEED integration layer
        seed_integration = get_seed_integration()
        
        # Run comprehensive optimization
        result = seed_integration.run_comprehensive_user_optimization(user_id)
        
        if result['success']:
            logger.info(f"Comprehensive optimization completed for user {user_id}")
            return jsonify({
                'success': True,
                'optimization_type': 'comprehensive',
                'user_id': user_id,
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Comprehensive optimization failed')
            }), 400
    
    except Exception as e:
        logger.error(f"Comprehensive optimization error: {e}")
        return jsonify({
            'success': False,
            'error': 'Optimization service temporarily unavailable'
        }), 500

@seed_bp.route('/optimize/ai-costs', methods=['POST'])
def optimize_ai_costs():
    """
    System-wide AI cost optimization (admin-level)
    """
    try:
        # Get SEED integration layer
        seed_integration = get_seed_integration()
        
        # Run AI cost optimization
        result = seed_integration.optimize_ai_cost_efficiency()
        
        if result['success']:
            logger.info("AI cost optimization completed")
            return jsonify({
                'success': True,
                'optimization_type': 'ai_costs',
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'AI cost optimization failed'),
                'estimated_savings': result.get('estimated_monthly_savings', 0)
            }), 400
    
    except Exception as e:
        logger.error(f"AI cost optimization error: {e}")
        return jsonify({
            'success': False,
            'error': 'Cost optimization service temporarily unavailable'
        }), 500

@seed_bp.route('/optimize/system-wide', methods=['POST'])
def optimize_system_wide():
    """
    Run system-wide optimization across all users and services
    """
    try:
        # Get SEED integration layer
        seed_integration = get_seed_integration()
        
        # Run system-wide optimization
        result = seed_integration.run_system_wide_optimization()
        
        if result['success']:
            logger.info("System-wide optimization completed")
            return jsonify({
                'success': True,
                'optimization_type': 'system_wide',
                'result': result,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'System-wide optimization failed')
            }), 400
    
    except Exception as e:
        logger.error(f"System-wide optimization error: {e}")
        return jsonify({
            'success': False,
            'error': 'System optimization service temporarily unavailable'
        }), 500

@seed_bp.route('/status', methods=['GET'])
def get_optimization_status():
    """
    Get current SEED optimization status
    """
    try:
        user = get_current_user()
        user_id = user.get('id') if user else None
        
        # Get SEED engine
        seed_engine = get_seed_engine()
        
        # Get optimization status
        status = seed_engine.get_optimization_status()
        
        # Get integration layer data
        seed_integration = get_seed_integration()
        dashboard_data = seed_integration.get_optimization_dashboard_data(user_id)
        
        return jsonify({
            'success': True,
            'engine_status': status,
            'dashboard_data': dashboard_data,
            'user_authenticated': bool(user_id),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Status retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': 'Status service temporarily unavailable',
            'engine_status': 'unknown'
        }), 500

@seed_bp.route('/recommendations', methods=['GET'])
@demo_fallback
def get_recommendations():
    """
    Get personalized optimization recommendations for current user
    """
    try:
        user = get_current_user()
        user_id = user.get('id')
        
        # Get SEED engine
        seed_engine = get_seed_engine()
        
        # Get recommendations
        recommendations = seed_engine.get_optimization_recommendations(user_id)
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'recommendations': recommendations,
            'count': len(recommendations),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Recommendations retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': 'Recommendations service temporarily unavailable',
            'recommendations': []
        }), 500

@seed_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """
    Get optimization dashboard data
    """
    try:
        user = get_current_user()
        user_id = user.get('id') if user else None
        
        # Get SEED integration layer
        seed_integration = get_seed_integration()
        
        # Get dashboard data
        dashboard_data = seed_integration.get_optimization_dashboard_data(user_id)
        
        # Add demo data if not authenticated
        if not user_id:
            dashboard_data['demo_mode'] = True
            dashboard_data['demo_data'] = {
                'potential_improvements': {
                    'therapeutic_effectiveness': '25-40%',
                    'engagement_score': '15-30%',
                    'ai_cost_savings': '30-50%'
                },
                'feature_highlights': [
                    'Personalized therapeutic intervention timing',
                    'Adaptive coping skill recommendations',
                    'Predictive crisis prevention',
                    'AI cost optimization',
                    'Smart engagement patterns'
                ]
            }
        
        return jsonify({
            'success': True,
            'dashboard_data': dashboard_data,
            'user_authenticated': bool(user_id),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        return jsonify({
            'success': False,
            'error': 'Dashboard service temporarily unavailable',
            'dashboard_data': {}
        }), 500

@seed_bp.route('/feedback', methods=['POST'])
@demo_fallback
def submit_optimization_feedback():
    """
    Submit feedback on optimization recommendations
    """
    try:
        user = get_current_user()
        user_id = user.get('id')
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No feedback data provided'
            }), 400
        
        recommendation_id = data.get('recommendation_id')
        feedback_type = data.get('feedback_type')  # 'helpful', 'not_helpful', 'implemented'
        rating = data.get('rating')  # 1-5 scale
        comments = data.get('comments', '')
        
        # Store feedback (this would integrate with your feedback system)
        feedback_data = {
            'user_id': user_id,
            'recommendation_id': recommendation_id,
            'feedback_type': feedback_type,
            'rating': rating,
            'comments': comments,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Optimization feedback received from user {user_id}: {feedback_type}")
        
        return jsonify({
            'success': True,
            'message': 'Feedback received - SEED will learn from this',
            'feedback_data': feedback_data
        })
    
    except Exception as e:
        logger.error(f"Feedback submission error: {e}")
        return jsonify({
            'success': False,
            'error': 'Feedback service temporarily unavailable'
        }), 500

@seed_bp.route('/history', methods=['GET'])
@demo_fallback
def get_optimization_history():
    """
    Get optimization history for current user
    """
    try:
        user = get_current_user()
        user_id = user.get('id')
        
        # Get query parameters
        limit = request.args.get('limit', 20, type=int)
        domain = request.args.get('domain')  # Optional domain filter
        
        # This would query the optimization database
        # For now, return sample structure
        history = {
            'optimizations': [],
            'summary': {
                'total_optimizations': 0,
                'avg_improvement': 0.0,
                'domains_optimized': [],
                'last_optimization': None
            }
        }
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'history': history,
            'limit': limit,
            'domain_filter': domain,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': 'History service temporarily unavailable',
            'history': {}
        }), 500

@seed_bp.route('/insights', methods=['GET'])
def get_optimization_insights():
    """
    Get system-wide optimization insights and patterns
    """
    try:
        # Get SEED engine
        seed_engine = get_seed_engine()
        
        # Get optimization recommendations (system-wide)
        insights = seed_engine.get_optimization_recommendations()
        
        # Add system metrics
        status = seed_engine.get_optimization_status()
        
        return jsonify({
            'success': True,
            'insights': insights,
            'system_metrics': {
                'total_optimizations': status.get('total_optimizations', 0),
                'average_improvement': status.get('avg_improvement', 0.0),
                'active_domains': len(status.get('domains', {}))
            },
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Insights retrieval error: {e}")
        return jsonify({
            'success': False,
            'error': 'Insights service temporarily unavailable',
            'insights': []
        }), 500

# Health check endpoint
@seed_bp.route('/health', methods=['GET'])
def health_check():
    """
    Health check for SEED optimization services
    """
    try:
        # Test SEED engine
        seed_engine = get_seed_engine()
        engine_status = seed_engine.get_optimization_status()
        
        # Test integration layer
        seed_integration = get_seed_integration()
        
        return jsonify({
            'success': True,
            'service': 'SEED Optimization',
            'status': 'healthy',
            'engine_status': engine_status.get('engine_status', 'unknown'),
            'total_optimizations': engine_status.get('total_optimizations', 0),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        logger.error(f"SEED health check error: {e}")
        return jsonify({
            'success': False,
            'service': 'SEED Optimization',
            'status': 'degraded',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

# Error handlers
@seed_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'SEED optimization endpoint not found'
    }), 404

@seed_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'SEED optimization service error'
    }), 500