"""
Health Check and Monitoring Routes

This module provides endpoints for monitoring system health,
resource usage, and performance metrics.

@module: health_check
@author: NOUS Development Team
"""
import os
import time
import datetime
import platform
import logging
import psutil
import json
from flask import Blueprint, jsonify, request, current_app
from typing import Dict, Any

# Create blueprint
health_check = Blueprint('health_check', __name__)

# Configure logger
logger = logging.getLogger(__name__)

# Store startup time
START_TIME = time.time()

@health_check.route('/health')
def basic_health_check():
    """
    Basic health check endpoint
    
    This endpoint returns a simple status check to verify that
    the application is running and reachable.
    
    Returns:
        JSON with status information
    """
    return jsonify({
        "status": "ok",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": os.environ.get("APP_VERSION", "development")
    })

@health_check.route('/health/detailed')
def detailed_health_check():
    """
    Detailed health check with component status
    
    This endpoint checks the health of all major subsystems
    and returns detailed status information.
    
    Returns:
        JSON with detailed health status
    """
    # Check database connection
    db_status = check_database_health()
    
    # Check Redis connection if configured
    redis_status = check_redis_health()
    
    # Get uptime
    uptime_seconds = time.time() - START_TIME
    uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
    
    # Build response
    response = {
        "status": "ok" if all(s["status"] == "ok" for s in [db_status, redis_status]) else "degraded",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "version": os.environ.get("APP_VERSION", "development"),
        "uptime": uptime_str,
        "uptime_seconds": uptime_seconds,
        "components": {
            "database": db_status,
            "redis": redis_status
        }
    }
    
    return jsonify(response)

@health_check.route('/health/system')
def system_health():
    """
    System resource usage information
    
    This endpoint returns information about system resources
    like CPU, memory, and disk usage.
    
    Returns:
        JSON with system resource information
    """
    # Get CPU usage
    cpu_percent = psutil.cpu_percent(interval=0.1)
    cpu_count = psutil.cpu_count()
    
    # Get memory usage
    memory = psutil.virtual_memory()
    
    # Get disk usage
    disk = psutil.disk_usage('/')
    
    # Build response
    response = {
        "cpu": {
            "percent": cpu_percent,
            "count": cpu_count,
            "per_cpu": psutil.cpu_percent(interval=0.1, percpu=True)
        },
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "percent": memory.percent
        },
        "disk": {
            "total": disk.total,
            "free": disk.free,
            "used": disk.used,
            "percent": disk.percent
        },
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "python": platform.python_version()
        }
    }
    
    return jsonify(response)

@health_check.route('/health/metrics')
def application_metrics():
    """
    Application performance metrics
    
    This endpoint returns metrics about the application's
    performance, including response times and request counts.
    
    Returns:
        JSON with application metrics
    """
    from app import app
    
    # Get request stats from the app's metrics if available
    request_count = getattr(app, 'request_count', 0)
    error_count = getattr(app, 'error_count', 0)
    response_times = getattr(app, 'response_times', [])
    
    # Calculate average response time
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Build response
    response = {
        "requests": {
            "total": request_count,
            "errors": error_count,
            "success_rate": (1 - (error_count / request_count)) * 100 if request_count > 0 else 100
        },
        "response_time": {
            "average_ms": avg_response_time,
            "min_ms": min(response_times) if response_times else 0,
            "max_ms": max(response_times) if response_times else 0
        },
        "rate_limits": {
            "current": getattr(app, 'rate_limited_count', 0)
        }
    }
    
    return jsonify(response)

def check_database_health() -> Dict[str, Any]:
    """
    Check the health of the database connection
    
    Returns:
        Dict with database health status
    """
    try:
        # Try a simple query to check the database connection
        from app import db
        result = db.session.execute("SELECT 1").scalar()
        
        return {
            "status": "ok" if result == 1 else "error",
            "message": "Connected to database"
        }
    except Exception as e:
        logger.exception("Database health check failed")
        return {
            "status": "error",
            "message": str(e)
        }

def check_redis_health() -> Dict[str, Any]:
    """
    Check the health of the Redis connection if configured
    
    Returns:
        Dict with Redis health status
    """
    # Skip if Redis is not configured
    if not os.environ.get("REDIS_URL"):
        return {
            "status": "skipped",
            "message": "Redis not configured"
        }
    
    try:
        # Try to connect to Redis and run a simple command
        import redis
        redis_client = redis.from_url(os.environ.get("REDIS_URL"))
        redis_client.ping()
        
        return {
            "status": "ok",
            "message": "Connected to Redis"
        }
    except Exception as e:
        logger.exception("Redis health check failed")
        return {
            "status": "error",
            "message": str(e)
        } 