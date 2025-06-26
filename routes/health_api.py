"""
Health Check API Routes

This module provides comprehensive health check endpoints for all external service integrations.
"""

import logging
from flask import Blueprint, jsonify, request
from utils.service_health_checker import health_checker

logger = logging.getLogger(__name__)

# Create blueprint
health_api_bp = Blueprint('health_api', __name__, url_prefix='/api/health')

@health_api_bp.route('/')
def comprehensive_health_check():
    """Run comprehensive health checks for all services"""
    try:
        results = health_checker.run_full_health_check()
        
        # Determine HTTP status code based on results
        if results['overall_status'] == 'healthy':
            status_code = 200
        elif results['overall_status'] == 'degraded':
            status_code = 206  # Partial Content
        else:
            status_code = 503  # Service Unavailable
            
        return jsonify(results), status_code
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'overall_status': 'error',
            'error': str(e)
        }), 500

@health_api_bp.route('/google-oauth')
def google_oauth_health():
    """Check Google OAuth service health"""
    try:
        result = health_checker.check_google_oauth()
        
        status_code = 200 if result['status'] == 'healthy' else 503
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Google OAuth health check failed: {e}")
        return jsonify({
            'service': 'Google OAuth',
            'status': 'error',
            'error': str(e)
        }), 500

@health_api_bp.route('/ai-services')
def ai_services_health():
    """Check AI services health"""
    try:
        results = {
            'openai': health_checker.check_openai_api(),
            'openrouter': health_checker.check_openrouter_api(),
            'huggingface': health_checker.check_huggingface_api()
        }
        
        # Determine overall status
        healthy_count = sum(1 for r in results.values() if r['status'] == 'healthy')
        error_count = sum(1 for r in results.values() if r['status'] == 'error')
        
        if error_count == 0:
            overall_status = 'healthy'
            status_code = 200
        elif healthy_count > 0:
            overall_status = 'degraded'
            status_code = 206
        else:
            overall_status = 'unhealthy'
            status_code = 503
            
        return jsonify({
            'overall_status': overall_status,
            'services': results
        }), status_code
    except Exception as e:
        logger.error(f"AI services health check failed: {e}")
        return jsonify({
            'overall_status': 'error',
            'error': str(e)
        }), 500

@health_api_bp.route('/database')
def database_health():
    """Check database connectivity"""
    try:
        result = health_checker.check_database_connection()
        
        status_code = 200 if result['status'] == 'healthy' else 503
        return jsonify(result), status_code
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return jsonify({
            'service': 'Database',
            'status': 'error',
            'error': str(e)
        }), 500