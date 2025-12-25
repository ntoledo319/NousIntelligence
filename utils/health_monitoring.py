"""
Enhanced Health Monitoring
Comprehensive health checks and system metrics for production monitoring
"""

import os
import time
import psutil
from datetime import datetime, timedelta
from flask import jsonify
import logging

logger = logging.getLogger(__name__)


class HealthMonitor:
    """
    Comprehensive health monitoring for the NOUS application.

    Provides detailed health checks, metrics, and diagnostics for production monitoring.
    """

    def __init__(self, app=None, db=None):
        """
        Initialize health monitor.

        Args:
            app: Flask application instance
            db: SQLAlchemy database instance
        """
        self.app = app
        self.db = db
        self.start_time = datetime.utcnow()
        self.request_count = 0
        self.error_count = 0

    def get_health_status(self, detailed=False):
        """
        Get comprehensive health status.

        Args:
            detailed: Include detailed metrics and diagnostics

        Returns:
            dict: Health status information
        """
        status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'environment': os.environ.get('FLASK_ENV', 'production'),
        }

        # Check database health
        db_status = self._check_database()
        status['database'] = db_status

        # If database is down, mark overall status as unhealthy
        if db_status.get('status') != 'healthy':
            status['status'] = 'degraded'

        if detailed:
            # Add detailed system metrics
            status['system'] = self._get_system_metrics()
            status['application'] = self._get_application_metrics()
            status['dependencies'] = self._check_dependencies()

        return status

    def _check_database(self):
        """
        Check database connectivity and health.

        Returns:
            dict: Database health information
        """
        if not self.db:
            return {
                'status': 'not_configured',
                'message': 'Database not initialized'
            }

        try:
            # Test database connection with simple query
            start_time = time.time()
            self.db.session.execute(self.db.text('SELECT 1'))
            query_time = (time.time() - start_time) * 1000  # Convert to ms

            # Get connection pool stats if available
            pool_status = self._get_pool_stats()

            return {
                'status': 'healthy',
                'response_time_ms': round(query_time, 2),
                'pool': pool_status,
                'message': 'Database connected'
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'message': 'Database connection failed'
            }

    def _get_pool_stats(self):
        """
        Get database connection pool statistics.

        Returns:
            dict: Connection pool stats
        """
        try:
            engine = self.db.engine
            pool = engine.pool

            return {
                'size': pool.size(),
                'checked_in': pool.checkedin(),
                'checked_out': pool.checkedout(),
                'overflow': pool.overflow(),
                'total': pool.size() + pool.overflow()
            }
        except Exception as e:
            logger.debug(f"Could not get pool stats: {e}")
            return {'available': True}

    def _get_system_metrics(self):
        """
        Get system resource metrics.

        Returns:
            dict: System metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': psutil.cpu_count(),
                    'status': 'healthy' if cpu_percent < 80 else 'high'
                },
                'memory': {
                    'total_mb': round(memory.total / 1024 / 1024, 2),
                    'available_mb': round(memory.available / 1024 / 1024, 2),
                    'percent': memory.percent,
                    'status': 'healthy' if memory.percent < 80 else 'high'
                },
                'disk': {
                    'total_gb': round(disk.total / 1024 / 1024 / 1024, 2),
                    'free_gb': round(disk.free / 1024 / 1024 / 1024, 2),
                    'percent': disk.percent,
                    'status': 'healthy' if disk.percent < 80 else 'high'
                }
            }
        except Exception as e:
            logger.warning(f"Could not get system metrics: {e}")
            return {'status': 'unavailable'}

    def _get_application_metrics(self):
        """
        Get application-specific metrics.

        Returns:
            dict: Application metrics
        """
        uptime = datetime.utcnow() - self.start_time

        return {
            'uptime_seconds': int(uptime.total_seconds()),
            'uptime_formatted': str(uptime).split('.')[0],
            'requests_total': self.request_count,
            'errors_total': self.error_count,
            'error_rate': round((self.error_count / max(self.request_count, 1)) * 100, 2)
        }

    def _check_dependencies(self):
        """
        Check external dependencies and services.

        Returns:
            dict: Dependency health status
        """
        dependencies = {}

        # Check Redis (if configured)
        redis_url = os.environ.get('REDIS_URL')
        if redis_url:
            dependencies['redis'] = self._check_redis(redis_url)

        # Check Google OAuth
        has_oauth = bool(
            os.environ.get('GOOGLE_CLIENT_ID') and
            os.environ.get('GOOGLE_CLIENT_SECRET')
        )
        dependencies['google_oauth'] = {
            'configured': has_oauth,
            'status': 'healthy' if has_oauth else 'not_configured'
        }

        return dependencies

    def _check_redis(self, redis_url):
        """
        Check Redis connectivity.

        Args:
            redis_url: Redis connection URL

        Returns:
            dict: Redis health status
        """
        try:
            import redis
            client = redis.from_url(redis_url)
            client.ping()
            return {
                'status': 'healthy',
                'configured': True
            }
        except ImportError:
            return {
                'status': 'not_installed',
                'configured': True
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'configured': True
            }

    def record_request(self):
        """Record a request for metrics."""
        self.request_count += 1

    def record_error(self):
        """Record an error for metrics."""
        self.error_count += 1

    def get_readiness_check(self):
        """
        Kubernetes-style readiness check.

        Returns:
            tuple: (status_dict, http_code)
        """
        db_status = self._check_database()

        if db_status.get('status') == 'healthy':
            return {'ready': True}, 200
        else:
            return {'ready': False, 'reason': 'database_unavailable'}, 503

    def get_liveness_check(self):
        """
        Kubernetes-style liveness check.

        Returns:
            tuple: (status_dict, http_code)
        """
        # Simple check - if we can respond, we're alive
        return {'alive': True}, 200


# Global health monitor instance
_health_monitor = None


def init_health_monitor(app, db):
    """
    Initialize global health monitor.

    Args:
        app: Flask application
        db: Database instance

    Returns:
        HealthMonitor: Initialized health monitor
    """
    global _health_monitor
    _health_monitor = HealthMonitor(app, db)

    logger.info("Health monitoring initialized")
    return _health_monitor


def get_health_monitor():
    """
    Get global health monitor instance.

    Returns:
        HealthMonitor: Health monitor instance
    """
    return _health_monitor


def create_health_endpoints(app, db):
    """
    Create health check endpoints for the Flask app.

    Args:
        app: Flask application
        db: Database instance
    """
    monitor = init_health_monitor(app, db)

    @app.route('/health')
    @app.route('/api/health')
    def health_check():
        """Basic health check endpoint."""
        status = monitor.get_health_status(detailed=False)
        http_code = 200 if status['status'] == 'healthy' else 503
        return jsonify(status), http_code

    @app.route('/health/detailed')
    @app.route('/api/health/detailed')
    def health_check_detailed():
        """Detailed health check with full metrics."""
        status = monitor.get_health_status(detailed=True)
        http_code = 200 if status['status'] == 'healthy' else 503
        return jsonify(status), http_code

    @app.route('/health/ready')
    @app.route('/api/health/ready')
    def readiness_check():
        """Kubernetes-style readiness check."""
        status, code = monitor.get_readiness_check()
        return jsonify(status), code

    @app.route('/health/live')
    @app.route('/api/health/live')
    def liveness_check():
        """Kubernetes-style liveness check."""
        status, code = monitor.get_liveness_check()
        return jsonify(status), code

    # Middleware to track requests and errors
    @app.before_request
    def track_request():
        """Track incoming requests."""
        monitor.record_request()

    @app.errorhandler(Exception)
    def track_error(error):
        """Track errors."""
        monitor.record_error()
        raise error

    logger.info("Health check endpoints created: /health, /health/detailed, /health/ready, /health/live")
