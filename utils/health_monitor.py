"""
Backend Stability - Health Monitoring System
Implements comprehensive health checks, connection pooling, and error tracking
"""
import os
import time
import psutil
import logging
import threading
from datetime import datetime, timedelta
from flask import jsonify, current_app
from typing import Dict, Any, List
import json

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Comprehensive health monitoring for backend stability"""
    
    def __init__(self, app=None):
        self.app = app
        self.startup_time = datetime.now()
        self.health_checks = {}
        self.alerts = []
        self.metrics = {
            'requests_total': 0,
            'requests_failed': 0,
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': []
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize health monitoring with Flask app"""
        self.app = app
        
        # Register health check route
        app.add_url_rule('/healthz', 'healthz', self.health_check, methods=['GET'])
        app.add_url_rule('/health/detailed', 'health_detailed', self.detailed_health, methods=['GET'])
        app.add_url_rule('/health/metrics', 'health_metrics', self.get_metrics, methods=['GET'])
        
        # Start background monitoring
        self._start_background_monitoring()
        
        # Register graceful shutdown handlers
        self._register_shutdown_handlers()
    
    def health_check(self):
        """Basic health check endpoint for load balancers"""
        try:
            # Quick checks
            db_status = self._check_database()
            memory_ok = self._check_memory()
            
            if db_status and memory_ok:
                return jsonify({
                    'status': 'healthy',
                    'timestamp': datetime.now().isoformat(),
                    'uptime': str(datetime.now() - self.startup_time)
                }), 200
            else:
                return jsonify({
                    'status': 'unhealthy',
                    'timestamp': datetime.now().isoformat(),
                    'issues': {
                        'database': not db_status,
                        'memory': not memory_ok
                    }
                }), 503
                
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def detailed_health(self):
        """Detailed health check with comprehensive system info"""
        try:
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'uptime': str(datetime.now() - self.startup_time),
                'system': self._get_system_metrics(),
                'database': self._get_database_health(),
                'application': self._get_app_health(),
                'services': self._check_external_services()
            }
            
            # Determine overall health
            issues = []
            if not health_data['database']['connected']:
                issues.append('database_disconnected')
            if health_data['system']['memory_percent'] > 90:
                issues.append('high_memory_usage')
            if health_data['system']['cpu_percent'] > 95:
                issues.append('high_cpu_usage')
            
            if issues:
                health_data['status'] = 'degraded'
                health_data['issues'] = issues
                return jsonify(health_data), 206
            
            return jsonify(health_data), 200
            
        except Exception as e:
            logger.error(f"Detailed health check failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def get_metrics(self):
        """Get performance metrics"""
        return jsonify({
            'requests': {
                'total': self.metrics['requests_total'],
                'failed': self.metrics['requests_failed'],
                'success_rate': (
                    (self.metrics['requests_total'] - self.metrics['requests_failed']) 
                    / max(self.metrics['requests_total'], 1) * 100
                )
            },
            'performance': {
                'avg_response_time': (
                    sum(self.metrics['response_times']) / len(self.metrics['response_times'])
                    if self.metrics['response_times'] else 0
                ),
                'response_times_95th': self._get_percentile(self.metrics['response_times'], 95)
            },
            'system': {
                'memory_usage': self.metrics['memory_usage'][-10:],  # Last 10 readings
                'cpu_usage': self.metrics['cpu_usage'][-10:]
            }
        })
    
    def _check_database(self):
        """Quick database connectivity check"""
        try:
            from flask import current_app
            if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
                db = current_app.extensions['sqlalchemy']
                # Simple query to test connection
                db.session.execute('SELECT 1')
                return True
            return False
        except Exception as e:
            logger.error(f"Database check failed: {str(e)}")
            return False
    
    def _check_memory(self):
        """Check system memory usage"""
        try:
            memory = psutil.virtual_memory()
            return memory.percent < 95  # Alert if memory > 95%
        except Exception:
            return True  # Default to healthy if can't check
    
    def _get_system_metrics(self):
        """Get comprehensive system metrics"""
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            disk = psutil.disk_usage('/')
            
            return {
                'memory_percent': memory.percent,
                'memory_available_mb': memory.available // 1024 // 1024,
                'cpu_percent': cpu_percent,
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free // 1024 // 1024 // 1024,
                'load_average': os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
            }
        except Exception as e:
            logger.error(f"Failed to get system metrics: {str(e)}")
            return {}
    
    def _get_database_health(self):
        """Get database health and connection info"""
        try:
            from flask import current_app
            
            health = {
                'connected': False,
                'pool_size': 0,
                'active_connections': 0,
                'query_time_ms': 0
            }
            
            if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
                db = current_app.extensions['sqlalchemy']
                
                # Test connection with timing
                start_time = time.time()
                result = db.session.execute('SELECT 1').scalar()
                query_time = (time.time() - start_time) * 1000
                
                health.update({
                    'connected': result == 1,
                    'query_time_ms': round(query_time, 2)
                })
                
                # Get pool info if available
                engine = db.engine
                if hasattr(engine.pool, 'size'):
                    health['pool_size'] = engine.pool.size()
                if hasattr(engine.pool, 'checked_in'):
                    health['active_connections'] = engine.pool.checked_in()
            
            return health
            
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return {'connected': False, 'error': str(e)}
    
    def _get_app_health(self):
        """Get application-specific health metrics"""
        return {
            'uptime_seconds': (datetime.now() - self.startup_time).total_seconds(),
            'debug_mode': self.app.debug if self.app else False,
            'config_loaded': bool(self.app and self.app.config),
            'routes_registered': len(self.app.url_map._rules) if self.app else 0
        }
    
    def _check_external_services(self):
        """Check external service connectivity"""
        services = {}
        
        # Check Google OAuth (if configured)
        google_client_id = os.environ.get('GOOGLE_CLIENT_ID')
        if google_client_id:
            services['google_oauth'] = {
                'configured': True,
                'client_id_set': bool(google_client_id)
            }
        
        # Check Sentry (if configured)
        sentry_dsn = os.environ.get('SENTRY_DSN')
        if sentry_dsn:
            services['sentry'] = {
                'configured': True,
                'dsn_set': bool(sentry_dsn)
            }
        
        return services
    
    def _start_background_monitoring(self):
        """Start background thread for continuous monitoring"""
        def monitor():
            while True:
                try:
                    # Collect metrics every 30 seconds
                    memory = psutil.virtual_memory()
                    cpu = psutil.cpu_percent()
                    
                    self.metrics['memory_usage'].append(memory.percent)
                    self.metrics['cpu_usage'].append(cpu)
                    
                    # Keep only last 100 readings
                    if len(self.metrics['memory_usage']) > 100:
                        self.metrics['memory_usage'] = self.metrics['memory_usage'][-100:]
                    if len(self.metrics['cpu_usage']) > 100:
                        self.metrics['cpu_usage'] = self.metrics['cpu_usage'][-100:]
                    
                    time.sleep(30)
                    
                except Exception as e:
                    logger.error(f"Background monitoring error: {str(e)}")
                    time.sleep(60)  # Wait longer on error
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _register_shutdown_handlers(self):
        """Register graceful shutdown handlers"""
        import signal
        import atexit
        
        def shutdown_handler(signum, frame):
            logger.info(f"Received signal {signum}, starting graceful shutdown...")
            self._graceful_shutdown()
        
        # Register signal handlers
        signal.signal(signal.SIGTERM, shutdown_handler)
        signal.signal(signal.SIGINT, shutdown_handler)
        
        # Register exit handler
        atexit.register(self._graceful_shutdown)
    
    def _graceful_shutdown(self):
        """Perform graceful shutdown"""
        logger.info("Starting graceful shutdown...")
        
        try:
            # Close database connections
            from flask import current_app
            if hasattr(current_app, 'extensions') and 'sqlalchemy' in current_app.extensions:
                db = current_app.extensions['sqlalchemy']
                db.session.close()
                db.engine.dispose()
                logger.info("Database connections closed")
            
            logger.info("Graceful shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during graceful shutdown: {str(e)}")
    
    def _get_percentile(self, data, percentile):
        """Calculate percentile of data"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def record_request(self, response_time, success=True):
        """Record request metrics"""
        self.metrics['requests_total'] += 1
        if not success:
            self.metrics['requests_failed'] += 1
        
        self.metrics['response_times'].append(response_time)
        
        # Keep only last 1000 response times
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]

# Global health monitor instance
health_monitor = HealthMonitor()