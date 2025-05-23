"""
Health API Blueprint

This module provides health-related API endpoints for the NOUS application.
"""

from flask import Blueprint, jsonify, request
import datetime
import logging
import os

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint with URL prefix
health_api = Blueprint('health_api', __name__)

@health_api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring and load balancers"""
    # Log health check access
    logger.info(f"Health check from {request.remote_addr}")

    # For API clients requesting JSON format
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "environment": os.environ.get("FLASK_ENV", "production"),
        "timestamp": datetime.datetime.now().isoformat()
    })
"""
Health check API routes
"""

import os
import platform
import psutil
from datetime import datetime
from flask import Blueprint, jsonify

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """
    Health check endpoint for monitoring and deployment verification
    """
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "production")
    })

@health_bp.route('/health/system')
def system_health():
    """
    Extended health check with system information
    """
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "production"),
        "system": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "memory": {
                "total": round(psutil.virtual_memory().total / (1024 * 1024), 2),
                "available": round(psutil.virtual_memory().available / (1024 * 1024), 2),
                "percent": psutil.virtual_memory().percent
            },
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "cores": psutil.cpu_count()
            },
            "disk": {
                "total": round(psutil.disk_usage('/').total / (1024 * 1024 * 1024), 2),
                "free": round(psutil.disk_usage('/').free / (1024 * 1024 * 1024), 2),
                "percent": psutil.disk_usage('/').percent
            }
        }
    })
