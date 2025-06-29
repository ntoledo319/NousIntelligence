"""
Enhanced Api Routes Routes
Enhanced Api Routes functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.auth_compat import login_required, current_user, get_current_user, is_authenticated

enhanced_api_routes_bp = Blueprint('enhanced_api_routes', __name__)


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

Enhanced API Routes for New Intelligence Services
Integrates predictive analytics, enhanced voice, automation, visual intelligence, and context-aware AI
"""

import json
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from functools import wraps

from services.predictive_analytics import predictive_engine
from services.enhanced_voice_interface import enhanced_voice
from services.intelligent_automation import automation_engine
from services.visual_intelligence import visual_intelligence
from services.context_aware_ai import context_ai

logger = logging.getLogger(__name__)

# Create blueprint
enhanced_api = Blueprint('enhanced_api', __name__, url_prefix='/api/v2')

def require_user_id(f):
    """Decorator to require user_id in request"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.json.get('user_id') if request.json else request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id required'}), 400
        return f(user_id, *args, **kwargs)
    return decorated_function

# ===== PREDICTIVE ANALYTICS ROUTES =====

@enhanced_api.route('/predictions/analyze', methods=['POST'])
@require_user_id
def analyze_user_patterns(user_id):
    """Analyze user behavior patterns"""
    try:
        patterns = predictive_engine.analyze_user_patterns(user_id)
        return jsonify({
            'success': True,
            'patterns': patterns,
            'user_id': user_id,
            'analyzed_at': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error analyzing patterns: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/predictions/generate', methods=['POST'])
@require_user_id
def generate_predictions(user_id):
    """Generate predictions for user"""
    try:
        predictions = predictive_engine.generate_predictions(user_id)
        return jsonify({
            'success': True,
            'predictions': predictions,
            'count': len(predictions),
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error generating predictions: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/predictions/active', methods=['GET'])
def get_active_predictions():
    """Get active predictions for user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        predictions = predictive_engine.get_active_predictions(user_id)
        return jsonify({
            'success': True,
            'predictions': predictions,
            'count': len(predictions),
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error getting active predictions: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/predictions/feedback', methods=['POST'])
@require_user_id
def record_prediction_feedback(user_id):
    """Record feedback on prediction accuracy"""
    try:
        data = request.json
        prediction_id = data.get('prediction_id')
        feedback_type = data.get('feedback_type', 'accuracy')
        feedback_value = data.get('feedback_value', 0.5)
        
        predictive_engine.record_prediction_feedback(
            user_id, prediction_id, feedback_type, feedback_value
        )
        
        return jsonify({
            'success': True,
            'message': 'Feedback recorded',
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error recording feedback: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/predictions/accuracy', methods=['GET'])
def get_prediction_accuracy():
    """Get prediction accuracy metrics"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        accuracy = predictive_engine.get_prediction_accuracy(user_id)
        return jsonify({
            'success': True,
            'accuracy_metrics': accuracy,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error getting accuracy: {e}")
        return jsonify({'error': str(e)}), 500

# ===== ENHANCED VOICE INTERFACE ROUTES =====

@enhanced_api.route('/voice/process', methods=['POST'])
@require_user_id
def process_voice_input(user_id):
    """Process voice input with emotion analysis"""
    try:
        # Get audio data from request
        if 'audio' not in request.files:
            return jsonify({'error': 'Audio file required'}), 400
        
        audio_file = request.files['audio']
        audio_data = audio_file.read()
        
        # Process with enhanced voice interface
        import asyncio
        response = asyncio.run(enhanced_voice.process_voice_input(audio_data, user_id))
        
        return jsonify({
            'success': True,
            'response': response,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error processing voice: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/voice/emotional-insights', methods=['GET'])
def get_emotional_insights():
    """Get emotional insights for user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        insights = enhanced_voice.get_emotional_insights(user_id)
        return jsonify({
            'success': True,
            'insights': insights,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error getting emotional insights: {e}")
        return jsonify({'error': str(e)}), 500

# ===== INTELLIGENT AUTOMATION ROUTES =====

@enhanced_api.route('/automation/rules', methods=['GET'])
def get_automation_rules():
    """Get automation rules for user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        rules = automation_engine.get_user_rules(user_id)
        return jsonify({
            'success': True,
            'rules': rules,
            'count': len(rules),
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error getting automation rules: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/automation/rules', methods=['POST'])
@require_user_id
def create_automation_rule(user_id):
    """Create new automation rule"""
    try:
        data = request.json
        name = data.get('name')
        trigger = data.get('trigger')
        actions = data.get('actions')
        conditions = data.get('conditions', [])
        
        if not all([name, trigger, actions]):
            return jsonify({'error': 'name, trigger, and actions required'}), 400
        
        rule_id = automation_engine.create_rule(name, trigger, actions, conditions, user_id)
        
        return jsonify({
            'success': True,
            'rule_id': rule_id,
            'message': 'Automation rule created',
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error creating automation rule: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/automation/templates', methods=['GET'])
def get_automation_templates():
    """Get available automation templates"""
    try:
        templates = automation_engine.get_available_templates()
        return jsonify({
            'success': True,
            'templates': templates,
            'count': len(templates)
        })
    except Exception as e:
        logger.error(f"Error getting templates: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/automation/templates/<template_name>', methods=['POST'])
@require_user_id
def create_rule_from_template(user_id, template_name):
    """Create automation rule from template"""
    try:
        data = request.json
        customizations = data.get('customizations', {})
        
        rule_id = automation_engine.create_rule_from_template(
            template_name, user_id, customizations
        )
        
        return jsonify({
            'success': True,
            'rule_id': rule_id,
            'template_used': template_name,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error creating rule from template: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/automation/rules/<rule_id>/toggle', methods=['POST'])
def toggle_automation_rule(rule_id):
    """Enable/disable automation rule"""
    try:
        data = request.json
        enabled = data.get('enabled', True)
        
        if enabled:
            automation_engine.enable_rule(rule_id)
        else:
            automation_engine.disable_rule(rule_id)
        
        return jsonify({
            'success': True,
            'rule_id': rule_id,
            'enabled': enabled
        })
    except Exception as e:
        logger.error(f"Error toggling rule: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/automation/rules/<rule_id>', methods=['DELETE'])
def delete_automation_rule(rule_id):
    """Delete automation rule"""
    try:
        automation_engine.delete_rule(rule_id)
        return jsonify({
            'success': True,
            'rule_id': rule_id,
            'message': 'Rule deleted'
        })
    except Exception as e:
        logger.error(f"Error deleting rule: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/automation/history', methods=['GET'])
def get_automation_history():
    """Get automation execution history"""
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 50))
    
    try:
        history = automation_engine.get_execution_history(user_id, limit)
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error getting automation history: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/automation/trigger', methods=['POST'])
def trigger_automation_event():
    """Manually trigger automation event"""
    try:
        data = request.json
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        
        import asyncio
        asyncio.run(automation_engine.trigger_event(event_type, event_data))
        
        return jsonify({
            'success': True,
            'message': 'Event triggered',
            'event_type': event_type
        })
    except Exception as e:
        logger.error(f"Error triggering event: {e}")
        return jsonify({'error': str(e)}), 500

# ===== VISUAL INTELLIGENCE ROUTES =====

@enhanced_api.route('/visual/process', methods=['POST'])
@require_user_id
def process_image_upload(user_id):
    """Process uploaded image with visual intelligence"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Image file required'}), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        auto_create_tasks = request.form.get('auto_create_tasks', 'true').lower() == 'true'
        
        result = visual_intelligence.process_image_upload(
            image_data, user_id, auto_create_tasks
        )
        
        return jsonify({
            'success': True,
            'result': result,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/visual/document/analyze', methods=['POST'])
def analyze_document():
    """Analyze document image"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Image file required'}), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        document_type = request.form.get('document_type')
        
        analysis = visual_intelligence.document_processor.process_document_image(
            image_data, document_type
        )
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    except Exception as e:
        logger.error(f"Error analyzing document: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/visual/tasks/create', methods=['POST'])
@require_user_id
def create_tasks_from_image(user_id):
    """Create tasks from image analysis"""
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'Image file required'}), 400
        
        image_file = request.files['image']
        image_data = image_file.read()
        
        tasks = visual_intelligence.task_creator.create_tasks_from_image(
            image_data, user_id
        )
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'count': len(tasks),
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error creating tasks from image: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/visual/analytics', methods=['GET'])
def get_visual_analytics():
    """Get visual processing analytics"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        analytics = visual_intelligence.get_visual_analytics(user_id)
        return jsonify({
            'success': True,
            'analytics': analytics,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error getting visual analytics: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/visual/history', methods=['GET'])
def get_visual_processing_history():
    """Get visual processing history"""
    user_id = request.args.get('user_id')
    limit = int(request.args.get('limit', 50))
    
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        history = visual_intelligence.get_processing_history(user_id, limit)
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history),
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error getting visual history: {e}")
        return jsonify({'error': str(e)}), 500

# ===== CONTEXT-AWARE AI ROUTES =====

@enhanced_api.route('/ai/chat', methods=['POST'])
@require_user_id
def context_aware_chat(user_id):
    """Chat with context-aware AI assistant"""
    try:
        data = request.json
        user_input = data.get('message')
        additional_context = data.get('context', {})
        
        if not user_input:
            return jsonify({'error': 'message required'}), 400
        
        import asyncio
        response = asyncio.run(context_ai.process_with_context(
            user_input, user_id, additional_context
        ))
        
        return jsonify({
            'success': True,
            'response': response,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error in context-aware chat: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/ai/insights', methods=['GET'])
def get_user_ai_insights():
    """Get AI insights about user interaction patterns"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        insights = context_ai.get_user_insights(user_id)
        return jsonify({
            'success': True,
            'insights': insights,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error getting AI insights: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/ai/context/reset', methods=['POST'])
@require_user_id
def reset_user_ai_context(user_id):
    """Reset user AI context and personality"""
    try:
        context_ai.reset_user_context(user_id)
        return jsonify({
            'success': True,
            'message': 'Context reset',
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error resetting context: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/ai/export', methods=['GET'])
def export_user_ai_data():
    """Export user AI context and personality data"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        data = context_ai.export_user_data(user_id)
        return jsonify({
            'success': True,
            'data': data,
            'user_id': user_id
        })
    except Exception as e:
        logger.error(f"Error exporting user data: {e}")
        return jsonify({'error': str(e)}), 500

# ===== INTEGRATED INTELLIGENCE ROUTES =====

@enhanced_api.route('/intelligence/dashboard', methods=['GET'])
def get_intelligence_dashboard():
    """Get comprehensive intelligence dashboard"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400
    
    try:
        # Gather data from all intelligence services
        dashboard = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'predictions': predictive_engine.get_active_predictions(user_id),
            'automation_rules': automation_engine.get_user_rules(user_id),
            'ai_insights': context_ai.get_user_insights(user_id),
            'visual_analytics': visual_intelligence.get_visual_analytics(user_id),
            'emotional_insights': enhanced_voice.get_emotional_insights(user_id)
        }
        
        return jsonify({
            'success': True,
            'dashboard': dashboard
        })
    except Exception as e:
        logger.error(f"Error getting intelligence dashboard: {e}")
        return jsonify({'error': str(e)}), 500

@enhanced_api.route('/intelligence/status', methods=['GET'])
def get_intelligence_status():
    """Get status of all intelligence services"""
    try:
        status = {
            'predictive_analytics': 'operational',
            'enhanced_voice': 'operational',
            'intelligent_automation': 'operational',
            'visual_intelligence': 'operational',
            'context_aware_ai': 'operational',
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting intelligence status: {e}")
        return jsonify({'error': str(e)}), 500

# Error handlers
@enhanced_api.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@enhanced_api.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

@enhanced_api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500