"""
NOUS Monitoring & Metrics Module
Advanced monitoring, metrics collection, and performance tracking
"""

import logging
import time
from typing import Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# Track if Prometheus is available
PROMETHEUS_AVAILABLE = False
try:
    import prometheus_client
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
    PROMETHEUS_AVAILABLE = True
except ImportError:
    logger.warning("Prometheus client not available - monitoring will use basic logging")

# Global metrics collectors
request_count = None
request_latency = None
active_users = None
error_count = None
ai_requests = None

def init_monitoring(app):
    """Initialize monitoring and metrics collection
    
    Args:
        app: Flask application instance
    """
    global request_count, request_latency, active_users, error_count, ai_requests
    
    if not PROMETHEUS_AVAILABLE:
        logger.warning("Prometheus not installed - using basic monitoring")
        app.extensions['monitoring'] = None
        return
    
    try:
        # Create metrics collectors
        request_count = Counter(
            'nous_request_total',
            'Total number of HTTP requests',
            ['method', 'endpoint', 'status']
        )
        
        request_latency = Histogram(
            'nous_request_duration_seconds',
            'HTTP request latency in seconds',
            ['endpoint']
        )
        
        active_users = Gauge(
            'nous_active_users',
            'Number of currently active users'
        )
        
        error_count = Counter(
            'nous_errors_total',
            'Total number of errors',
            ['error_type', 'endpoint']
        )
        
        ai_requests = Counter(
            'nous_ai_requests_total',
            'Total number of AI processing requests',
            ['provider', 'status']
        )
        
        # Add WSGI middleware for metrics collection
        if hasattr(prometheus_client, 'make_wsgi_app'):
            app.wsgi_app = prometheus_client.make_wsgi_app(app.wsgi_app)
        
        # Register request hooks
        @app.before_request
        def before_request():
            """Record request start time"""
            from flask import request, g
            g.start_time = time.time()
        
        @app.after_request
        def after_request(response):
            """Record request metrics"""
            from flask import request, g
            
            if hasattr(g, 'start_time'):
                # Calculate request duration
                duration = time.time() - g.start_time
                
                # Record metrics
                endpoint = request.endpoint or 'unknown'
                method = request.method
                status = str(response.status_code)
                
                request_count.labels(method=method, endpoint=endpoint, status=status).inc()
                request_latency.labels(endpoint=endpoint).observe(duration)
                
                # Log slow requests
                if duration > 2.0:  # 2 seconds threshold
                    logger.warning(f"Slow request: {method} {endpoint} took {duration:.2f}s")
            
            return response
        
        # Error tracking
        @app.errorhandler(Exception)
        def track_errors(error):
            """Track application errors"""
            from flask import request
            endpoint = request.endpoint or 'unknown'
            error_type = type(error).__name__
            error_count.labels(error_type=error_type, endpoint=endpoint).inc()
            
            logger.error(f"Application error in {endpoint}: {error_type} - {str(error)}")
            raise error
        
        # Store monitoring instance
        app.extensions['monitoring'] = {
            'request_count': request_count,
            'request_latency': request_latency,
            'active_users': active_users,
            'error_count': error_count,
            'ai_requests': ai_requests
        }
        
        logger.info("Monitoring system initialized with Prometheus metrics")
        
    except Exception as e:
        logger.error(f"Failed to initialize monitoring: {e}")
        app.extensions['monitoring'] = None

def get_monitoring():
    """Get the monitoring instance from the current Flask app
    
    Returns:
        Monitoring metrics dictionary or None
    """
    from flask import current_app
    try:
        return current_app.extensions.get('monitoring')
    except RuntimeError:
        # No app context
        return None

def track_ai_request(provider: str, success: bool = True):
    """Track AI request metrics
    
    Args:
        provider: AI provider name (openrouter, gemini, etc.)
        success: Whether the request was successful
    """
    if ai_requests:
        status = 'success' if success else 'error'
        ai_requests.labels(provider=provider, status=status).inc()

def track_user_activity(user_id: str, action: str):
    """Track user activity for analytics
    
    Args:
        user_id: User identifier
        action: Action performed
    """
    logger.info(f"User activity: {user_id} performed {action}")
    
    # Could extend to track specific user metrics
    if active_users:
        # Simple active user tracking (would need Redis for proper implementation)
        pass

def monitor_performance(func):
    """Decorator to monitor function performance
    
    Usage:
        @monitor_performance
        def my_function():
            # Function code here
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.debug(f"Function {func.__name__} completed in {duration:.3f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    return wrapper

def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics
    
    Returns:
        Dictionary of system metrics
    """
    try:
        import psutil
        
        metrics = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': time.time()
        }
        
        # Add network stats if available
        try:
            net_io = psutil.net_io_counters()
            metrics['network'] = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
        except:
            pass
            
        return metrics
        
    except ImportError:
        logger.warning("psutil not available - system metrics unavailable")
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'disk_usage': 0,
            'timestamp': time.time(),
            'error': 'psutil not available'
        }

def get_application_metrics() -> Dict[str, Any]:
    """Get current application metrics
    
    Returns:
        Dictionary of application metrics
    """
    monitoring = get_monitoring()
    
    if not monitoring or not PROMETHEUS_AVAILABLE:
        return {
            'total_requests': 'unavailable',
            'error_rate': 'unavailable',
            'avg_response_time': 'unavailable',
            'timestamp': time.time()
        }
    
    try:
        # Calculate basic metrics from Prometheus collectors
        metrics = {
            'timestamp': time.time(),
            'monitoring_enabled': True
        }
        
        # Add collected metrics if available
        if request_count:
            total_requests = sum(request_count._value.values())
            metrics['total_requests'] = total_requests
        
        if error_count:
            total_errors = sum(error_count._value.values())
            metrics['total_errors'] = total_errors
            
            if 'total_requests' in metrics and metrics['total_requests'] > 0:
                metrics['error_rate'] = total_errors / metrics['total_requests']
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error collecting application metrics: {e}")
        return {
            'error': str(e),
            'timestamp': time.time()
        }

def export_metrics() -> str:
    """Export metrics in Prometheus format
    
    Returns:
        Metrics in Prometheus text format
    """
    if PROMETHEUS_AVAILABLE:
        try:
            return generate_latest().decode('utf-8')
        except Exception as e:
            logger.error(f"Error exporting metrics: {e}")
            return f"# Error exporting metrics: {e}\n"
    else:
        return "# Prometheus not available\n"

class PerformanceProfiler:
    """Context manager for performance profiling"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        logger.debug(f"Starting profiling: {self.operation_name}")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type:
            logger.error(f"Profiling failed: {self.operation_name} - {exc_val} ({duration:.3f}s)")
        else:
            logger.info(f"Profiling completed: {self.operation_name} - {duration:.3f}s")
            
            # Track slow operations
            if duration > 1.0:  # 1 second threshold
                logger.warning(f"Slow operation detected: {self.operation_name} took {duration:.3f}s")

def health_check() -> Dict[str, Any]:
    """Comprehensive health check
    
    Returns:
        Health status dictionary
    """
    health = {
        'status': 'healthy',
        'timestamp': time.time(),
        'checks': {}
    }
    
    # Check database connectivity
    try:
        from database import db
        from sqlalchemy import text
        db.session.execute(text('SELECT 1')).scalar()
        health['checks']['database'] = 'healthy'
    except Exception as e:
        health['checks']['database'] = f'unhealthy: {str(e)}'
        health['status'] = 'unhealthy'
    
    # Check AI service availability
    try:
        from utils.unified_ai_service import get_unified_ai_service
        ai_service = get_unified_ai_service()
        if ai_service.available_providers:
            health['checks']['ai_service'] = 'healthy'
        else:
            health['checks']['ai_service'] = 'no_providers'
            health['status'] = 'degraded'
    except Exception as e:
        health['checks']['ai_service'] = f'unhealthy: {str(e)}'
        health['status'] = 'unhealthy'
    
    # Check system resources
    try:
        system_metrics = get_system_metrics()
        if system_metrics.get('memory_percent', 0) > 90:
            health['checks']['memory'] = 'high_usage'
            health['status'] = 'degraded'
        else:
            health['checks']['memory'] = 'healthy'
    except Exception as e:
        health['checks']['memory'] = f'check_failed: {str(e)}'
    
    return health