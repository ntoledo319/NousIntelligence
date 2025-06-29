
"""Celery Fallback - Synchronous Task Processing"""
import logging
from functools import wraps

logger = logging.getLogger(__name__)

class MockCelery:
    def __init__(self, *args, **kwargs):
        self.tasks = {}
        logger.warning("Using synchronous fallback for Celery tasks")
    
    def task(self, *args, **kwargs):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Execute synchronously
                return func(*args, **kwargs)
            
            # Add delay method for Celery compatibility
            wrapper.delay = lambda *a, **k: func(*a, **k)
            wrapper.apply_async = lambda *a, **k: func(*a, **k)
            
            self.tasks[func.__name__] = wrapper
            return wrapper
        return decorator

# Create fallback instance
app = MockCelery()
Celery = MockCelery

# Make available as celery
import sys
current_module = sys.modules[__name__]
sys.modules['celery'] = current_module
