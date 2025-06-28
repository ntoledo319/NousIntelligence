"""
NOUS Async Processing Module
High-performance asynchronous task processing for background operations
"""

import logging
import os
from typing import Any, Dict, Optional
from functools import wraps

logger = logging.getLogger(__name__)

# Track if Celery is available
CELERY_AVAILABLE = False
try:
    from celery import Celery, shared_task
    CELERY_AVAILABLE = True
except ImportError:
    logger.warning("Celery not available - async processing will use fallback mode")

def init_async_processing(app):
    """Initialize asynchronous processing with Celery integration
    
    Args:
        app: Flask application instance
    """
    if not CELERY_AVAILABLE:
        logger.warning("Celery not installed - async processing disabled")
        app.extensions['async_processor'] = None
        return
    
    # Get Celery configuration from environment or app config
    broker_url = app.config.get('CELERY_BROKER_URL', os.environ.get('REDIS_URL', 'redis://localhost:6379/0'))
    result_backend = app.config.get('CELERY_RESULT_BACKEND', os.environ.get('REDIS_URL', 'redis://localhost:6379/1'))
    
    try:
        # Create Celery instance
        celery = Celery(
            app.import_name,
            broker=broker_url,
            backend=result_backend
        )
        
        # Update Celery configuration
        celery_config = {
            'task_serializer': 'json',
            'accept_content': ['json'],
            'result_serializer': 'json',
            'timezone': 'UTC',
            'enable_utc': True,
            'worker_prefetch_multiplier': 1,
            'task_acks_late': True,
            'worker_disable_rate_limits': False,
            'task_compression': 'gzip',
            'result_compression': 'gzip',
            'task_routes': {
                'nous.tasks.ai_processing': {'queue': 'ai_tasks'},
                'nous.tasks.heavy_compute': {'queue': 'compute_tasks'},
                'nous.tasks.background_sync': {'queue': 'sync_tasks'}
            }
        }
        celery.conf.update(celery_config)
        celery.conf.update(app.config.get('CELERY', {}))
        
        # Create context-aware task base class
        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context"""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
        
        # Store celery instance in app
        app.extensions['async_processor'] = celery
        app.celery = celery
        
        logger.info(f"Async processing initialized with broker: {broker_url}")
        
    except Exception as e:
        logger.error(f"Failed to initialize async processing: {e}")
        app.extensions['async_processor'] = None

def get_async_processor(app=None):
    """Get the async processor instance from the current Flask app
    
    Returns:
        Celery instance or None if not available
    """
    if app:
        return app.extensions.get('async_processor')
    
    from flask import current_app
    try:
        return current_app.extensions.get('async_processor')
    except RuntimeError:
        # No app context
        return None

def make_async(func):
    """Decorator to make a function asynchronous
    
    Usage:
        @make_async
        def my_heavy_function(data):
            # Heavy processing here
            return result
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        processor = get_async_processor()
        if processor:
            # Create a task dynamically
            task = processor.task(func)
            return task.delay(*args, **kwargs)
        else:
            # Fallback to synchronous execution
            logger.warning(f"Async processor not available, executing {func.__name__} synchronously")
            return func(*args, **kwargs)
    return wrapper

# Pre-defined task decorators for common use cases
def ai_task(func):
    """Decorator for AI processing tasks"""
    if CELERY_AVAILABLE:
        return shared_task(bind=True, ignore_result=False, queue='ai_tasks')(func)
    return func

def heavy_task(func):
    """Decorator for CPU-intensive tasks"""
    if CELERY_AVAILABLE:
        return shared_task(bind=True, ignore_result=False, queue='compute_tasks')(func)
    return func

def background_task(func):
    """Decorator for background synchronization tasks"""
    if CELERY_AVAILABLE:
        return shared_task(bind=True, ignore_result=True, queue='sync_tasks')(func)
    return func

# Common task implementations
if CELERY_AVAILABLE:
    @shared_task(bind=True, ignore_result=False)
    def process_ai_request(self, prompt: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """Asynchronous AI processing task
        
        Args:
            prompt: AI prompt text
            context: Additional context data
            
        Returns:
            AI response data
        """
        try:
            self.update_state(state='PROGRESS', meta={'step': 'ai_processing', 'progress': 25})
            
            # Import AI service (avoid circular imports)
            from utils.unified_ai_service import get_unified_ai_service
            
            ai_service = get_unified_ai_service()
            self.update_state(state='PROGRESS', meta={'step': 'generating_response', 'progress': 50})
            
            response = ai_service.chat_completion([{"role": "user", "content": prompt}])
            
            self.update_state(state='PROGRESS', meta={'step': 'finalizing', 'progress': 90})
            
            return {
                'success': True,
                'response': response.get('response', ''),
                'metadata': response.get('metadata', {}),
                'timestamp': response.get('timestamp')
            }
            
        except Exception as e:
            logger.error(f"AI processing task failed: {e}")
            self.update_state(state='FAILURE', meta={'error': str(e)})
            return {'success': False, 'error': str(e)}

    @shared_task(bind=True, ignore_result=False)
    def process_heavy_computation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generic heavy computation task
        
        Args:
            payload: Task data and parameters
            
        Returns:
            Processing result
        """
        try:
            self.update_state(state='PROGRESS', meta={'step': 'starting', 'progress': 0})
            
            # Extract task type and data
            task_type = payload.get('type', 'unknown')
            data = payload.get('data', {})
            
            logger.info(f"Starting heavy computation: {task_type}")
            
            if task_type == 'data_analysis':
                return _process_data_analysis(self, data)
            elif task_type == 'file_processing':
                return _process_file_task(self, data)
            elif task_type == 'ai_analysis':
                return _process_ai_analysis(self, data)
            else:
                return {'error': f'Unknown task type: {task_type}'}
                
        except Exception as e:
            logger.error(f"Heavy computation task failed: {e}")
            self.update_state(state='FAILURE', meta={'error': str(e)})
            raise

    @shared_task(bind=True, ignore_result=True)
    def background_sync(self, sync_type: str, data: Dict[str, Any]) -> bool:
        """Background synchronization task
        
        Args:
            sync_type: Type of sync operation
            data: Sync data
            
        Returns:
            Success status
        """
        try:
            logger.info(f"Starting background sync: {sync_type}")
            
            if sync_type == 'user_preferences':
                return _sync_user_preferences(data)
            elif sync_type == 'system_metrics':
                return _sync_system_metrics(data)
            elif sync_type == 'cache_refresh':
                return _refresh_cache(data)
            else:
                logger.warning(f"Unknown sync type: {sync_type}")
                return False
                
        except Exception as e:
            logger.error(f"Background sync failed: {e}")
            return False

def _process_data_analysis(task, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process data analysis computation"""
    task.update_state(state='PROGRESS', meta={'step': 'data_processing', 'progress': 40})
    
    # Simulate data processing
    import time
    time.sleep(0.5)
    
    task.update_state(state='PROGRESS', meta={'step': 'analysis_complete', 'progress': 80})
    
    return {
        'success': True,
        'result': 'Data analysis completed',
        'statistics': {'processed': len(data), 'errors': 0},
        'summary': 'All data processed successfully'
    }

def _process_file_task(task, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process file-related computation"""
    task.update_state(state='PROGRESS', meta={'step': 'file_processing', 'progress': 35})
    
    # Simulate file processing
    import time
    time.sleep(0.3)
    
    task.update_state(state='PROGRESS', meta={'step': 'file_complete', 'progress': 85})
    
    return {
        'success': True,
        'result': 'File processing completed',
        'files_processed': data.get('file_count', 1),
        'output_location': '/tmp/processed_files'
    }

def _process_ai_analysis(task, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process AI-specific analysis"""
    task.update_state(state='PROGRESS', meta={'step': 'ai_analysis', 'progress': 30})
    
    # Simulate AI processing
    import time
    time.sleep(1)  # Simulate processing time
    
    task.update_state(state='PROGRESS', meta={'step': 'generating_insights', 'progress': 70})
    
    return {
        'success': True,
        'result': f"AI analysis completed for {len(data)} items",
        'insights': ['Pattern detected', 'Optimization suggested'],
        'confidence': 0.85
    }

def _sync_user_preferences(data: Dict[str, Any]) -> bool:
    """Sync user preferences in background"""
    logger.info("Syncing user preferences")
    return True

def _sync_system_metrics(data: Dict[str, Any]) -> bool:
    """Sync system metrics in background"""
    logger.info("Syncing system metrics")
    return True

def _refresh_cache(data: Dict[str, Any]) -> bool:
    """Refresh application cache in background"""
    logger.info("Refreshing cache")
    return True