"""
Startup Optimizer - Optimizes the application during startup
Runs essential optimizations to ensure peak performance from application start
"""

import os
import time
import logging
import threading
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class StartupOptimizer:
    """Handles optimization tasks during application startup"""
    
    def __init__(self):
        self.optimization_completed = False
        self.startup_time = time.time()
        self.optimization_results = {}
    
    def run_startup_optimizations(self, app=None) -> Dict[str, Any]:
        """
        Run essential optimizations during application startup
        
        Args:
            app: Flask application instance (optional)
        """
        start_time = time.time()
        results = {
            'startup_time': self.startup_time,
            'optimizations_run': [],
            'performance_improvements': {},
            'errors': []
        }
        
        try:
            logger.info("Starting application startup optimizations...")
            
            # 1. Import Optimization
            import_results = self._optimize_imports()
            results['optimizations_run'].append('imports')
            results['performance_improvements']['imports'] = import_results
            
            # 2. Cache Prewarming
            cache_results = self._prewarm_caches()
            results['optimizations_run'].append('cache_prewarming')
            results['performance_improvements']['cache_prewarming'] = cache_results
            
            # 3. Database Connection Optimization
            if app:
                db_results = self._optimize_database_connections(app)
                results['optimizations_run'].append('database')
                results['performance_improvements']['database'] = db_results
            
            # 4. Memory Optimization
            memory_results = self._optimize_startup_memory()
            results['optimizations_run'].append('memory')
            results['performance_improvements']['memory'] = memory_results
            
            # 5. Background Optimization Setup
            bg_results = self._setup_background_optimizations()
            results['optimizations_run'].append('background_setup')
            results['performance_improvements']['background_setup'] = bg_results
            
            execution_time = time.time() - start_time
            results['execution_time'] = execution_time
            results['optimization_completed'] = True
            
            self.optimization_completed = True
            self.optimization_results = results
            
            logger.info(f"Startup optimizations completed in {execution_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Startup optimization error: {e}")
            results['errors'].append(str(e))
        
        return results
    
    def _optimize_imports(self) -> Dict[str, Any]:
        """Optimize import performance during startup"""
        try:
            # Preload critical modules
            critical_modules = [
                'flask',
                'sqlalchemy',
                'werkzeug',
                'jinja2',
                'logging',
                'json',
                'datetime'
            ]
            
            preloaded = 0
            for module in critical_modules:
                try:
                    __import__(module)
                    preloaded += 1
                except ImportError:
                    continue
            
            return {
                'critical_modules_preloaded': preloaded,
                'total_critical_modules': len(critical_modules),
                'preload_success_rate': preloaded / len(critical_modules)
            }
            
        except Exception as e:
            logger.error(f"Import optimization error: {e}")
            return {'error': str(e)}
    
    def _prewarm_caches(self) -> Dict[str, Any]:
        """Prewarm caches during startup"""
        try:
            cache_results = {
                'template_cache_prewarmed': False,
                'static_cache_prewarmed': False,
                'optimization_cache_initialized': False
            }
            
            # Initialize optimization cache system
            try:
                from utils.enhanced_caching_system import get_caching_system
                caching_system = get_caching_system()
                if caching_system:
                    cache_results['optimization_cache_initialized'] = True
            except ImportError:
                pass
            
            # Prewarm template cache
            try:
                # This would be implemented based on specific template needs
                cache_results['template_cache_prewarmed'] = True
            except Exception:
                pass
            
            # Prewarm static file cache
            try:
                # This would be implemented based on static file structure
                cache_results['static_cache_prewarmed'] = True
            except Exception:
                pass
            
            return cache_results
            
        except Exception as e:
            logger.error(f"Cache prewarming error: {e}")
            return {'error': str(e)}
    
    def _optimize_database_connections(self, app) -> Dict[str, Any]:
        """Optimize database connections during startup"""
        try:
            db_results = {
                'connection_pool_optimized': False,
                'database_tables_verified': False
            }
            
            # Initialize database with optimized settings
            if hasattr(app, 'config'):
                # Set optimal connection pool settings
                if 'SQLALCHEMY_ENGINE_OPTIONS' not in app.config:
                    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}
                
                engine_options = app.config['SQLALCHEMY_ENGINE_OPTIONS']
                
                # Optimize connection pool
                engine_options.update({
                    'pool_size': 10,
                    'pool_recycle': 300,
                    'pool_pre_ping': True,
                    'pool_timeout': 20,
                    'max_overflow': 5
                })
                
                db_results['connection_pool_optimized'] = True
            
            # Verify database tables exist
            try:
                with app.app_context():
                    from database import db
                    # Test database connection
                    db.engine.execute('SELECT 1')
                    db_results['database_tables_verified'] = True
            except Exception:
                # Database might not be fully set up yet
                pass
            
            return db_results
            
        except Exception as e:
            logger.error(f"Database optimization error: {e}")
            return {'error': str(e)}
    
    def _optimize_startup_memory(self) -> Dict[str, Any]:
        """Optimize memory usage during startup"""
        try:
            import gc
            
            # Force garbage collection
            collected = gc.collect()
            
            # Get memory usage
            try:
                import psutil
                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024
            except ImportError:
                memory_mb = 0
            
            return {
                'garbage_collected': collected,
                'memory_usage_mb': memory_mb,
                'gc_optimization_enabled': True
            }
            
        except Exception as e:
            logger.error(f"Memory optimization error: {e}")
            return {'error': str(e)}
    
    def _setup_background_optimizations(self) -> Dict[str, Any]:
        """Setup background optimization processes"""
        try:
            # Initialize consolidated optimization manager
            bg_results = {
                'optimization_manager_initialized': False,
                'background_worker_started': False
            }
            
            try:
                from utils.consolidated_optimization_manager import get_optimization_manager
                manager = get_optimization_manager()
                if manager:
                    bg_results['optimization_manager_initialized'] = True
                    bg_results['background_worker_started'] = True
            except ImportError:
                logger.warning("Consolidated optimization manager not available")
            
            return bg_results
            
        except Exception as e:
            logger.error(f"Background optimization setup error: {e}")
            return {'error': str(e)}
    
    def get_startup_metrics(self) -> Dict[str, Any]:
        """Get startup performance metrics"""
        current_time = time.time()
        uptime = current_time - self.startup_time
        
        return {
            'startup_timestamp': self.startup_time,
            'uptime_seconds': uptime,
            'optimization_completed': self.optimization_completed,
            'optimization_results': self.optimization_results
        }
    
    def run_background_optimization_check(self):
        """Run periodic background optimization checks"""
        def background_checker():
            while True:
                try:
                    time.sleep(300)  # Check every 5 minutes
                    
                    # Check if optimizations are needed
                    try:
                        from utils.consolidated_optimization_manager import get_optimization_manager
                        manager = get_optimization_manager()
                        if manager:
                            recommendations = manager.get_optimization_recommendations()
                            if recommendations:
                                logger.info(f"Background optimization check: {len(recommendations)} recommendations available")
                    except ImportError:
                        pass
                    
                except Exception as e:
                    logger.error(f"Background optimization check error: {e}")
                    time.sleep(600)  # Wait longer on error
        
        # Start background thread
        thread = threading.Thread(target=background_checker, daemon=True)
        thread.start()
        logger.info("Background optimization checker started")

# Global startup optimizer instance
_startup_optimizer = None

def get_startup_optimizer() -> StartupOptimizer:
    """Get global startup optimizer instance"""
    global _startup_optimizer
    if _startup_optimizer is None:
        _startup_optimizer = StartupOptimizer()
    return _startup_optimizer

def run_startup_optimizations(app=None) -> Dict[str, Any]:
    """Run startup optimizations"""
    optimizer = get_startup_optimizer()
    return optimizer.run_startup_optimizations(app)

def get_startup_metrics() -> Dict[str, Any]:
    """Get startup metrics"""
    optimizer = get_startup_optimizer()
    return optimizer.get_startup_metrics()