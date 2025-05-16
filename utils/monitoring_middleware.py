"""
Monitoring Middleware Module

This module provides middleware for monitoring application performance,
tracking response times, request counts, and errors.

@module: monitoring_middleware
@author: NOUS Development Team
"""
import time
import logging
import threading
import collections
from typing import Callable, Dict, List, Any
from flask import Flask, request, g, current_app

# Configure logger
logger = logging.getLogger(__name__)

# Constants
MAX_RESPONSE_TIMES = 1000  # Maximum number of response times to store
RECENT_ERRORS_LIMIT = 50   # Maximum number of recent errors to store

# Lock for thread safety
stats_lock = threading.RLock()

def init_monitoring(app: Flask) -> None:
    """
    Initialize monitoring for a Flask application
    
    Args:
        app: Flask application instance
    """
    # Initialize metrics
    app.request_count = 0
    app.error_count = 0
    app.rate_limited_count = 0
    app.response_times = collections.deque(maxlen=MAX_RESPONSE_TIMES)
    app.recent_errors = collections.deque(maxlen=RECENT_ERRORS_LIMIT)
    app.endpoint_stats = {}  # Stats per endpoint
    
    # Register before_request handler
    @app.before_request
    def before_request_handler():
        """Record request start time"""
        g.start_time = time.time()
    
    # Register after_request handler
    @app.after_request
    def after_request_handler(response):
        """Record response time and update stats"""
        # Skip for static files
        if request.path.startswith('/static/'):
            return response
        
        # Calculate response time
        if hasattr(g, 'start_time'):
            response_time = (time.time() - g.start_time) * 1000  # in milliseconds
            
            with stats_lock:
                # Update global stats
                app.request_count += 1
                app.response_times.append(response_time)
                
                # Update endpoint stats
                endpoint = request.endpoint or 'unknown'
                if endpoint not in app.endpoint_stats:
                    app.endpoint_stats[endpoint] = {
                        'count': 0,
                        'error_count': 0,
                        'response_times': collections.deque(maxlen=100)
                    }
                
                app.endpoint_stats[endpoint]['count'] += 1
                app.endpoint_stats[endpoint]['response_times'].append(response_time)
                
                # Log slow responses (>1000ms)
                if response_time > 1000:
                    logger.warning(f"Slow response: {request.method} {request.path} - {response_time:.2f}ms")
        
        return response
    
    # Register error handler
    @app.errorhandler(Exception)
    def error_handler(error):
        """Record and log errors"""
        with stats_lock:
            app.error_count += 1
            
            # Update endpoint stats
            endpoint = request.endpoint or 'unknown'
            if endpoint in app.endpoint_stats:
                app.endpoint_stats[endpoint]['error_count'] += 1
            
            # Record error details
            error_details = {
                'timestamp': time.time(),
                'endpoint': endpoint,
                'method': request.method,
                'path': request.path,
                'error': str(error),
                'type': error.__class__.__name__
            }
            app.recent_errors.append(error_details)
            
            # Log error
            logger.error(f"Request error: {request.method} {request.path} - {str(error)}")
        
        # Continue with normal error handling
        raise error

def get_application_stats(app: Flask) -> Dict[str, Any]:
    """
    Get comprehensive application statistics
    
    Args:
        app: Flask application instance
        
    Returns:
        Dict with application statistics
    """
    with stats_lock:
        # Calculate average response time
        avg_response_time = sum(app.response_times) / len(app.response_times) if app.response_times else 0
        
        # Calculate endpoint stats
        endpoint_stats = {}
        for endpoint, stats in app.endpoint_stats.items():
            endpoint_stats[endpoint] = {
                'count': stats['count'],
                'error_count': stats['error_count'],
                'error_rate': (stats['error_count'] / stats['count']) * 100 if stats['count'] > 0 else 0,
                'avg_response_time': sum(stats['response_times']) / len(stats['response_times']) if stats['response_times'] else 0
            }
        
        # Combine all stats
        return {
            'requests': {
                'total': app.request_count,
                'errors': app.error_count,
                'success_rate': (1 - (app.error_count / app.request_count)) * 100 if app.request_count > 0 else 100
            },
            'response_time': {
                'average_ms': avg_response_time,
                'min_ms': min(app.response_times) if app.response_times else 0,
                'max_ms': max(app.response_times) if app.response_times else 0
            },
            'rate_limits': {
                'count': app.rate_limited_count
            },
            'endpoints': endpoint_stats,
            'recent_errors': list(app.recent_errors)
        }

def log_rate_limit_hit(app: Flask, endpoint: str) -> None:
    """
    Log a rate limit hit
    
    Args:
        app: Flask application instance
        endpoint: Endpoint that was rate limited
    """
    with stats_lock:
        app.rate_limited_count += 1
        
        # Log the rate limit
        logger.warning(f"Rate limit hit: {endpoint} - {request.remote_addr}")

def reset_stats(app: Flask) -> None:
    """
    Reset all application statistics
    
    Args:
        app: Flask application instance
    """
    with stats_lock:
        app.request_count = 0
        app.error_count = 0
        app.rate_limited_count = 0
        app.response_times.clear()
        app.recent_errors.clear()
        app.endpoint_stats = {} 