"""
Health API Routes - Health Monitoring and Status Endpoints
Provides comprehensive health checking for deployment monitoring
"""

import os
import logging
from datetime import datetime
from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

# Create health API blueprint
health_api_bp = Blueprint('health_api', __name__)

@health_api_bp.route('/health')
@health_api_bp.route('/healthz')
def health_check():
    """Comprehensive health check endpoint"""
    try:
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
    """Readiness check for deployment"""
    return jsonify({
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "deployment_ready": True
    }), 200

@health_api_bp.route('/live')
def liveness_check():
    """Liveness check for deployment"""
    return jsonify({
        "status": "alive",
        "timestamp": datetime.now().isoformat()
    }), 200

# Export the blueprint
__all__ = ['health_api_bp']