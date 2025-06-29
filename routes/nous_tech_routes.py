"""

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

NOUS Tech API Routes
Advanced AI, security, and monitoring endpoints for NOUS Tech integration
"""

from flask import Blueprint, request, jsonify, current_app
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

nous_tech_bp = Blueprint('nous_tech', __name__, url_prefix='/nous-tech')

@nous_tech_bp.route('/status', methods=['GET'])
def get_nous_tech_status():
    """Get comprehensive NOUS Tech system status"""
    try:
        status = {
            'timestamp': datetime.now().isoformat(),
            'system_status': 'operational',
            'components': {}
        }
        
        # Check AI System Brain
        if hasattr(current_app, 'ai_system_brain'):
            brain_status = current_app.ai_system_brain.get_system_status()
            status['components']['ai_system_brain'] = brain_status
        else:
            status['components']['ai_system_brain'] = {'status': 'not_available'}
        
        # Check Security Monitor
        if hasattr(current_app, 'security_monitor'):
            security_dashboard = current_app.security_monitor.get_security_dashboard()
            status['components']['security_monitor'] = security_dashboard
        else:
            status['components']['security_monitor'] = {'status': 'not_available'}
        
        # Check Parallel Processing
        if hasattr(current_app, 'celery'):
            status['components']['parallel_processing'] = {
                'status': 'available',
                'celery_available': True
            }
        else:
            status['components']['parallel_processing'] = {'status': 'fallback_mode'}
        
        # Check Compression
        if hasattr(current_app, 'compressor'):
            status['components']['compression'] = {
                'status': 'available',
                'compressor_type': 'zstandard'
            }
        else:
            status['components']['compression'] = {'status': 'fallback_mode'}
        
        # Check Brain module
        if hasattr(current_app, 'brain'):
            status['components']['brain'] = {
                'status': 'available',
                'ai_reasoning': True
            }
        else:
            status['components']['brain'] = {'status': 'fallback_mode'}
        
        # Overall health assessment
        available_components = sum(1 for comp in status['components'].values() 
                                 if comp.get('status') not in ['not_available', 'fallback_mode'])
        total_components = len(status['components'])
        health_percentage = (available_components / total_components) * 100 if total_components > 0 else 0
        
        status['health_percentage'] = health_percentage
        status['health_status'] = (
            'excellent' if health_percentage >= 90 else
            'good' if health_percentage >= 70 else
            'fair' if health_percentage >= 50 else
            'poor'
        )
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Failed to get NOUS Tech status: {e}")
        return jsonify({
            'error': str(e),
            'system_status': 'error',
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/ai/query', methods=['POST'])
def process_advanced_ai_query():
    """Process advanced AI query using AI System Brain"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data['query']
        context = data.get('context', {})
        
        # Check if AI System Brain is available
        if not hasattr(current_app, 'ai_system_brain'):
            return jsonify({
                'error': 'AI System Brain not available',
                'fallback_response': 'Advanced AI processing is currently unavailable'
            }), 503
        
        # Process the query using AI System Brain
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(
                current_app.ai_system_brain.process_complex_query(query, context)
            )
        finally:
            loop.close()
        
        return jsonify({
            'success': True,
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Advanced AI query processing failed: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/security/monitor', methods=['POST'])
def monitor_security_access():
    """Monitor security access with NOUS Tech security system"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        user_id = data.get('user_id', 'anonymous')
        resource = data.get('resource', 'unknown')
        action = data.get('action', 'access')
        context = data.get('context', {})
        
        # Check if security monitor is available
        if hasattr(current_app, 'security_monitor'):
            result = current_app.security_monitor.monitor_access(
                user_id, resource, action, context
            )
        else:
            # Fallback security monitoring
            result = {
                'access_granted': True,
                'risk_score': 0.5,
                'fallback_mode': True,
                'message': 'Security monitoring in fallback mode'
            }
        
        return jsonify({
            'success': True,
            'security_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Security monitoring failed: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/security/ai-monitor', methods=['POST'])
def monitor_ai_operation():
    """Monitor AI operations for security compliance"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data is required'}), 400
        
        user_id = data.get('user_id', 'anonymous')
        operation_type = data.get('operation_type', 'inference')
        model_info = data.get('model_info', {})
        security_level = data.get('security_level', 'standard')
        
        # Check if security monitor is available
        if hasattr(current_app, 'security_monitor'):
            result = current_app.security_monitor.monitor_ai_operation(
                user_id, operation_type, model_info, security_level
            )
        else:
            # Fallback AI security monitoring
            result = {
                'access_granted': True,
                'requires_tee': security_level in ['high', 'critical'],
                'fallback_mode': True,
                'message': 'AI security monitoring in fallback mode'
            }
        
        return jsonify({
            'success': True,
            'ai_security_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"AI security monitoring failed: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/learning/feedback', methods=['POST'])
def provide_learning_feedback():
    """Provide feedback for self-learning system"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Feedback data is required'}), 400
        
        user_id = data.get('user_id', 'anonymous')
        input_text = data.get('input', '')
        response_text = data.get('response', '')
        rating = data.get('rating')
        feedback_type = data.get('feedback_type', 'rating')
        metadata = data.get('metadata', {})
        
        # Try to log to self-learning system
        try:
            from nous_tech.features.selflearn import log_interaction
            log_interaction(user_id, input_text, response_text, rating, feedback_type, metadata)
            learning_logged = True
        except ImportError:
            learning_logged = False
        
        return jsonify({
            'success': True,
            'feedback_logged': learning_logged,
            'message': 'Feedback received and processed',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Learning feedback processing failed: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/learning/insights', methods=['GET'])
def get_learning_insights():
    """Get current learning insights"""
    try:
        insights = []
        
        # Try to get insights from self-learning system
        try:
            from nous_tech.features.selflearn import get_learning_insights
            insights = get_learning_insights()
        except ImportError:
            insights = [{'type': 'system', 'message': 'Learning system not available'}]
        
        return jsonify({
            'success': True,
            'insights': insights,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Failed to get learning insights: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/tee/secure-inference', methods=['POST'])
def secure_tee_inference():
    """Perform secure inference using TEE"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Inference data is required'}), 400
        
        model_path = data.get('model_path', 'default')
        input_data = data.get('input_data', {})
        security_level = data.get('security_level', 'high')
        
        # Try to use TEE for secure inference
        try:
            from nous_tech.features.security.tee import tee_run_inference
            result = tee_run_inference(model_path, input_data, security_level)
        except ImportError:
            result = {
                'success': False,
                'error': 'TEE system not available',
                'fallback_result': 'Secure inference unavailable'
            }
        
        return jsonify({
            'success': True,
            'tee_result': result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"TEE secure inference failed: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/blockchain/audit', methods=['POST'])
def log_blockchain_audit():
    """Log audit entry to blockchain"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Audit data is required'}), 400
        
        user_id = data.get('user_id', 'anonymous')
        record_id = data.get('record_id', 'unknown')
        action = data.get('action', 'access')
        metadata = data.get('metadata', {})
        
        # Try to log to blockchain audit system
        try:
            from nous_tech.features.security.blockchain import log_user_access
            transaction_hash = log_user_access(user_id, record_id, action)
            audit_logged = True
        except ImportError:
            transaction_hash = 'fallback_log'
            audit_logged = False
        
        return jsonify({
            'success': True,
            'audit_logged': audit_logged,
            'transaction_hash': transaction_hash,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Blockchain audit logging failed: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/compression/compress', methods=['POST'])
def compress_data():
    """Compress data using NOUS Tech compression"""
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return jsonify({'error': 'Data to compress is required'}), 400
        
        input_data = data['data']
        
        # Try to use NOUS Tech compression
        try:
            from nous_tech.features.compress import compress_data as nous_compress
            compressed_data = nous_compress(input_data)
            compression_used = True
        except ImportError:
            compressed_data = input_data.encode() if isinstance(input_data, str) else input_data
            compression_used = False
        
        return jsonify({
            'success': True,
            'compression_used': compression_used,
            'compressed_size': len(compressed_data),
            'original_size': len(str(input_data)),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Data compression failed: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/parallel/task', methods=['POST'])
def submit_parallel_task():
    """Submit task for parallel processing"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Task data is required'}), 400
        
        task_type = data.get('task_type', 'compute')
        payload = data.get('payload', {})
        
        # Try to submit to Celery
        task_id = None
        task_submitted = False
        
        if hasattr(current_app, 'celery'):
            try:
                if task_type == 'compute':
                    result = current_app.celery.send_task('nous_tech.features.parallel.heavy_compute', args=[payload])
                    task_id = result.id
                    task_submitted = True
                elif task_type == 'ai_inference':
                    result = current_app.celery.send_task('nous_tech.features.parallel.ai_inference_task', 
                                                        args=[payload.get('model_path', 'default'), payload])
                    task_id = result.id
                    task_submitted = True
            except Exception as e:
                logger.warning(f"Celery task submission failed: {e}")
        
        return jsonify({
            'success': True,
            'task_submitted': task_submitted,
            'task_id': task_id,
            'message': 'Task submitted for parallel processing' if task_submitted else 'Parallel processing unavailable',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Parallel task submission failed: {e}")
        return jsonify({
            'error': str(e),
            'success': False,
            'timestamp': datetime.now().isoformat()
        }), 500

@nous_tech_bp.route('/health', methods=['GET'])
def nous_tech_health():
    """Health check for NOUS Tech systems"""
    try:
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'components': {
                'ai_system_brain': hasattr(current_app, 'ai_system_brain'),
                'security_monitor': hasattr(current_app, 'security_monitor'),
                'parallel_processing': hasattr(current_app, 'celery'),
                'compression': hasattr(current_app, 'compressor'),
                'brain_module': hasattr(current_app, 'brain'),
                'security_audit': hasattr(current_app, 'security_audit')
            }
        }
        
        # Calculate overall health
        healthy_components = sum(health_status['components'].values())
        total_components = len(health_status['components'])
        health_percentage = (healthy_components / total_components) * 100
        
        health_status['health_percentage'] = health_percentage
        health_status['overall_status'] = (
            'excellent' if health_percentage >= 90 else
            'good' if health_percentage >= 70 else
            'fair' if health_percentage >= 50 else
            'degraded'
        )
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"NOUS Tech health check failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Error handlers for NOUS Tech routes
@nous_tech_bp.errorhandler(404)
def nous_tech_not_found(error):
    return jsonify({
        'error': 'NOUS Tech endpoint not found',
        'message': 'The requested NOUS Tech feature is not available',
        'timestamp': datetime.now().isoformat()
    }), 404

@nous_tech_bp.errorhandler(500)
def nous_tech_internal_error(error):
    return jsonify({
        'error': 'NOUS Tech internal error',
        'message': 'An internal error occurred in NOUS Tech system',
        'timestamp': datetime.now().isoformat()
    }), 500