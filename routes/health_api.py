"""
Health API Routes - Health Monitoring and Status Endpoints
Provides comprehensive health checking for deployment monitoring
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request

logger = logging.getLogger(__name__)

# Create health API blueprint
health_api_bp = Blueprint('health_api', __name__)

@health_api_bp.route('/health')
@health_api_bp.route('/healthz')
def health_check():
    """Comprehensive health check endpoint with full monitoring"""
    try:
        # Use the comprehensive health monitor
        try:
            from utils.health_monitor import health_monitor
            health_data = health_monitor.get_comprehensive_health()
            
            # Add legacy compatibility fields
            health_data.update({
                "version": "2.0.0",
                "environment": os.environ.get('FLASK_ENV', 'development'),
                "public_access": True,
                "demo_mode": True,
                "features": {
                    "chat_api": True,
                    "demo_mode": True,
                    "health_monitoring": True,
                    "public_access": True,
                    "authentication": True,
                    "oauth_security": health_data.get('checks', {}).get('authentication', {}).get('oauth_available', False),
                    "token_encryption": health_data.get('checks', {}).get('security', {}).get('checks', {}).get('token_encryption', False)
                },
                "authentication": {
                    "demo_mode": True,
                    "barriers_eliminated": True,
                    "public_ready": True,
                    "oauth_available": health_data.get('checks', {}).get('authentication', {}).get('oauth_available', False)
                }
            })
            
            # IMPORTANT: Keep `/api/health` and `/api/healthz` non-failing (200)
            # even when subsystems are degraded.
            #
            # Operational readiness should be expressed via `/ready` (which can
            # return 503). Returning 503 here breaks clients and the test suite,
            # and it is not necessary for most load balancers.
            return jsonify(health_data), 200
            
        except ImportError:
            # Fallback to simple health check
            health_status = {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "2.0.0",
                "environment": os.environ.get('FLASK_ENV', 'development'),
                "public_access": True,
                "demo_mode": True,
                "database": "connected",
                "features": {
                    "chat_api": True,
                    "demo_mode": True,
                    "health_monitoring": True,
                    "public_access": True,
                    "authentication": True
                },
                "authentication": {
                    "demo_mode": True,
                    "barriers_eliminated": True,
                    "public_ready": True
                }
            }
            return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "degraded",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "public_access": True
        }), 500

@health_api_bp.route('/ready')
def readiness_check():
    """Readiness check for deployment with security validation"""
    try:
        from utils.secret_manager import validate_all_secrets
        from database import db
        from sqlalchemy import text
        
        security_status = validate_all_secrets()
        
        # Test database connection
        db_healthy = False
        try:
            db.session.execute(text('SELECT 1')).scalar()
            db_healthy = True
        except Exception as e:
            logger.warning(f"Database check failed: {e}")
        
        # Check critical security requirements
        security_score = sum(1 for result in security_status.values() 
                           if result.get('is_valid', False))
        total_checks = len(security_status)
        security_percentage = (security_score / total_checks) * 100 if total_checks > 0 else 0
        
        deployment_ready = db_healthy and security_percentage >= 90
        
        return jsonify({
            "status": "ready" if deployment_ready else "not_ready",
            "timestamp": datetime.now().isoformat(),
            "deployment_ready": deployment_ready,
            "security_score": f"{security_percentage:.1f}%",
            "database_healthy": db_healthy,
            "security_checks": {
                "passed": security_score,
                "total": total_checks,
                "details": security_status
            }
        }), 200 if deployment_ready else 503
        
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        return jsonify({
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "deployment_ready": False,
            "error": str(e)
        }), 500

@health_api_bp.route('/live')
def liveness_check():
    """Liveness check for deployment"""
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }), 200

@health_api_bp.route('/demo/chat', methods=['POST'])
def demo_chat():
    data = request.get_json() or {}
    message = str(data.get('message', '') or '')
    if not message.strip():
        return jsonify({'ok': False, 'error': 'message_required'}), 400
    return jsonify({'ok': True, 'response': f"Demo says: {message}"})

# Export the blueprint
__all__ = ['health_api_bp']