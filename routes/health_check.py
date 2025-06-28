"""
Deployment Health Check Routes
Essential for deployment success monitoring
"""
from flask import Blueprint, jsonify
import datetime
import os

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
@health_bp.route('/healthz')
def health_check():
    """Health check endpoint for deployment monitoring"""
    try:
        # Basic health indicators
        health_data = {
            "status": "healthy",
            "timestamp": datetime.datetime.now().isoformat(),
            "version": "1.0.0",
            "environment": os.environ.get('FLASK_ENV', 'production'),
            "port": os.environ.get('PORT', '5000')
        }
        
        return jsonify(health_data), 200
        
    except Exception as e:
        error_data = {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.datetime.now().isoformat()
        }
        return jsonify(error_data), 500

@health_bp.route('/ready')
def readiness_check():
    """Readiness check for deployment"""
    return jsonify({"status": "ready"}), 200
