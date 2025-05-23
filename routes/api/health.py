"""
Health API Blueprint

This module provides health-related API endpoints for the NOUS application.
"""

import os
import platform
import psutil
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request

# Import our standardized API route helpers
from utils.api_route_helper import create_api_blueprint, api_route, register_api_error_handlers

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint with standardized naming and versioning
health_bp = create_api_blueprint('health', __name__, '/api', version='v1')

# Register standardized error handlers
register_api_error_handlers(health_bp)

@api_route(health_bp, '/health', methods=['GET'], 
    api_doc={
        'summary': 'Basic health check endpoint',
        'description': 'Simple health check for monitoring and load balancers',
        'responses': {
            '200': {'description': 'Application is healthy'}
        }
    }
)
def health_check():
    """
    Health check endpoint for monitoring and load balancers
    """
    # Log health check access
    logger.info(f"Health check from {request.remote_addr}")

    # Return standardized health check response
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.environ.get("FLASK_ENV", "production")
    }

@api_route(health_bp, '/health/system', methods=['GET'],
    api_doc={
        'summary': 'Extended system health check',
        'description': 'Provides detailed information about system health and resources',
        'responses': {
            '200': {'description': 'System health information'}
        }
    }
)
def system_health():
    """
    Extended health check with system information
    """
    # Log detailed health check access
    logger.info(f"System health check from {request.remote_addr}")
    
    try:
        # Get system information with error handling
        memory_info = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=0.1)  # Quick sampling
        disk_info = psutil.disk_usage('/')
        
        # Return comprehensive system health information
        return {
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.environ.get("FLASK_ENV", "production"),
            "system": {
                "platform": platform.platform(),
                "python": platform.python_version(),
                "memory": {
                    "total": round(memory_info.total / (1024 * 1024), 2),
                    "available": round(memory_info.available / (1024 * 1024), 2),
                    "percent": memory_info.percent
                },
                "cpu": {
                    "percent": cpu_percent,
                    "cores": psutil.cpu_count()
                },
                "disk": {
                    "total": round(disk_info.total / (1024 * 1024 * 1024), 2),
                    "free": round(disk_info.free / (1024 * 1024 * 1024), 2),
                    "percent": disk_info.percent
                }
            }
        }
    except Exception as e:
        # Log the error but still return basic health info
        logger.error(f"Error in system health check: {str(e)}")
        return {
            "status": "degraded",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.environ.get("FLASK_ENV", "production"),
            "error": "Unable to retrieve full system information"
        }
