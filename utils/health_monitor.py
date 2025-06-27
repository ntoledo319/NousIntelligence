"""
Health Monitor Module
Provides system health monitoring and status endpoints
"""

import logging
import psutil
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class HealthMonitor:
    """Health monitoring system for NOUS application"""
    
    def __init__(self):
        self.app = None
        self.start_time = time.time()
    
    def init_app(self, app):
        """Initialize health monitor with Flask app"""
        self.app = app
        logger.info("Health monitor initialized")
        
        # Register health check routes
        @app.route('/health')
        def health_check():
            """Basic health check endpoint"""
            return {
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': time.time() - self.start_time
            }
        
        @app.route('/healthz')
        def health_detailed():
            """Detailed health check with system metrics"""
            try:
                memory = psutil.virtual_memory()
                cpu = psutil.cpu_percent(interval=1)
                
                return {
                    'status': 'healthy',
                    'timestamp': datetime.utcnow().isoformat(),
                    'uptime': time.time() - self.start_time,
                    'system': {
                        'memory_percent': memory.percent,
                        'cpu_percent': cpu,
                        'available_memory': memory.available
                    }
                }
            except Exception as e:
                logger.error(f"Health check error: {e}")
                return {
                    'status': 'degraded',
                    'error': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }, 503

# Global health monitor instance
health_monitor = HealthMonitor()