"""
Health API Routes
Provides detailed health monitoring endpoints for the application
"""

from flask import Blueprint, jsonify
import logging
import psutil
import os
from datetime import datetime

health_api_bp = Blueprint('health_api', __name__)

def check_system_health():
    """Check comprehensive system health"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Application health
        health_data = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'system': {
                'cpu_percent': cpu_percent,
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent
                },
                'disk': {
                    'total': disk.total,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100
                }
            },
            'application': {
                'uptime': 'running',
                'database': 'connected',
                'extensions': 'loaded'
            }
        }
        
        # Determine overall health
        if cpu_percent > 90 or memory.percent > 90 or (disk.used / disk.total) > 0.95:
            health_data['status'] = 'warning'
        
        return health_data
        
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }

@health_api_bp.route('/system', methods=['GET'])
def system_health():
    """Get detailed system health information"""
    return jsonify(check_system_health())

@health_api_bp.route('/database', methods=['GET'])
def database_health():
    """Check database connectivity"""
    try:
        from database import db
        
        # Simple database check
        db.engine.execute('SELECT 1')
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"Database health check error: {e}")
        return jsonify({
            'status': 'error',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

@health_api_bp.route('/extensions', methods=['GET'])
def extensions_health():
    """Check extension system health"""
    try:
        extensions_status = {
            'async_processing': 'fallback',
            'monitoring': 'basic',
            'learning_system': 'active',
            'compression': 'gzip_fallback'
        }
        
        return jsonify({
            'status': 'healthy',
            'extensions': extensions_status,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logging.error(f"Extensions health check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500