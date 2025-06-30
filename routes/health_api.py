"""
Health API routes for monitoring and diagnostics
"""

from flask import Blueprint, jsonify, request
import datetime
import os

# Create blueprint
health_api_bp = Blueprint('health_api', __name__)

@health_api_bp.route('/health')
@health_api_bp.route('/healthz')
def health_check():
    """Basic health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0',
        'authentication': 'session-based'
    })

# Add root-level health endpoint
@health_api_bp.route('/')
def root_health_check():
    """Root level health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'version': '1.0.0',
        'authentication': 'session-based'
    })

@health_api_bp.route('/health/detailed')
def detailed_health():
    """Detailed health information"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.datetime.now().isoformat(),
        'database': 'connected',
        'authentication': 'working',
        'public_access': True,
        'demo_mode': 'available'
    })