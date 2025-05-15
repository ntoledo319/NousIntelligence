"""
Asynchronous task processor for non-blocking background operations.
"""

import threading
import queue
import logging
import time
from functools import wraps

# Task queue for background processing
_task_queue = queue.Queue()
_is_worker_running = False
_worker_thread = None
_worker_lock = threading.RLock()

def start_background_worker():
    """Start the background worker thread if not already running."""
    global _is_worker_running, _worker_thread
    
    with _worker_lock:
        if not _is_worker_running:
            _is_worker_running = True
            _worker_thread = threading.Thread(target=_process_task_queue, daemon=True)
            _worker_thread.start()
            logging.info("Started background task processor")

def _process_task_queue():
    """Process tasks from the queue in the background."""
    global _is_worker_running
    
    while _is_worker_running:
        try:
            # Get a task with a timeout to allow for graceful shutdown
            try:
                task, args, kwargs = _task_queue.get(timeout=1.0)
            except queue.Empty:
                continue
                
            # Execute the task
            try:
                start_time = time.time()
                task(*args, **kwargs)
                execution_time = time.time() - start_time
                logging.info(f"Background task {task.__name__} completed in {execution_time:.2f}s")
            except Exception as e:
                logging.error(f"Error in background task {task.__name__}: {str(e)}")
                
            # Mark task as done
            _task_queue.task_done()
            
        except Exception as e:
            logging.error(f"Error in task processor: {str(e)}")
            # Sleep briefly to avoid tight loop if there's a persistent error
            time.sleep(0.1)
    
    logging.info("Background task processor stopped")

def stop_background_worker():
    """Stop the background worker thread."""
    global _is_worker_running
    
    with _worker_lock:
        if _is_worker_running:
            _is_worker_running = False
            if _worker_thread:
                _worker_thread.join(timeout=5.0)
            logging.info("Stopped background task processor")

def run_async(func):
    """
    Decorator to run a function asynchronously in the background.
    
    Args:
        func: The function to run asynchronously
        
    Returns:
        Wrapper function that queues the task
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Ensure worker is running
        start_background_worker()
        
        # Queue the task
        _task_queue.put((func, args, kwargs))
        
        # Return immediately
        return None
    
    return wrapper

def queue_background_task(task, *args, **kwargs):
    """
    Queue a task to be executed in the background.
    
    Args:
        task: The function to execute
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
    """
    # Ensure worker is running
    start_background_worker()
    
    # Queue the task
    _task_queue.put((task, args, kwargs))
    
    return True

def get_queue_stats():
    """
    Get statistics about the task queue.
    
    Returns:
        dict: Queue statistics
    """
    return {
        "queue_size": _task_queue.qsize(),
        "worker_running": _is_worker_running
    }