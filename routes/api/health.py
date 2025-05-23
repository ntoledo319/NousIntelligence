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