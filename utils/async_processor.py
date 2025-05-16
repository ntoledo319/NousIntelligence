"""
Asynchronous Task Processing Module

This module provides asynchronous processing capabilities for long-running tasks.
It uses asyncio for concurrent task execution and supports different types of
background processing including:

1. Asynchronous API calls
2. Background job processing
3. Parallel data processing
4. Scheduled task execution

@module: async_processor
@author: NOUS Development Team
"""
import asyncio
import concurrent.futures
import functools
import logging
import time
import threading
import queue
from typing import Any, Callable, Dict, List, Optional, Tuple, Union, Coroutine

# Configure logger
logger = logging.getLogger(__name__)

# Thread pool for CPU-bound tasks
thread_pool = concurrent.futures.ThreadPoolExecutor(max_workers=10)

# Process pool for CPU-intensive tasks
process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=4)

# Task queue for background processing
task_queue = queue.Queue()

# Task results storage
task_results = {}
task_errors = {}

# Create a new event loop for the background thread
background_loop = None

class AsyncTaskStatus:
    """Status values for asynchronous tasks"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class AsyncTask:
    """Represents an asynchronous task with tracking capabilities"""
    
    def __init__(self, task_id: str, func: Callable, args: Tuple = None, kwargs: Dict = None):
        """
        Initialize a new async task
        
        Args:
            task_id: Unique identifier for this task
            func: The function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
        """
        self.task_id = task_id
        self.func = func
        self.args = args or ()
        self.kwargs = kwargs or {}
        self.status = AsyncTaskStatus.PENDING
        self.result = None
        self.error = None
        self.start_time = None
        self.end_time = None
    
    def execute(self):
        """Execute the task and track its status"""
        try:
            self.status = AsyncTaskStatus.RUNNING
            self.start_time = time.time()
            
            # Execute the function
            self.result = self.func(*self.args, **self.kwargs)
            
            self.status = AsyncTaskStatus.COMPLETED
        except Exception as e:
            self.status = AsyncTaskStatus.FAILED
            self.error = str(e)
            logger.exception(f"Task {self.task_id} failed with error: {str(e)}")
        finally:
            self.end_time = time.time()
            
        return self
    
    def to_dict(self) -> Dict:
        """Convert task information to a dictionary"""
        return {
            "task_id": self.task_id,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "execution_time": None if not self.end_time or not self.start_time else self.end_time - self.start_time
        }

def start_background_worker():
    """Start a background thread to process the task queue"""
    def worker():
        """Worker function that processes the queue"""
        while True:
            try:
                # Get a task from the queue
                task = task_queue.get()
                
                # Skip if task is None (shutdown signal)
                if task is None:
                    break
                
                # Execute the task
                task.execute()
                
                # Store the result
                task_results[task.task_id] = task.result
                if task.error:
                    task_errors[task.task_id] = task.error
                
                # Mark task as done
                task_queue.task_done()
                
                logger.debug(f"Completed background task: {task.task_id}")
            except Exception as e:
                logger.exception(f"Error in background worker: {str(e)}")
    
    # Start the background thread
    background_thread = threading.Thread(target=worker, daemon=True)
    background_thread.start()
    
    return background_thread

# Start the background worker thread
background_thread = start_background_worker()

def submit_task(func: Callable, *args, **kwargs) -> str:
    """
    Submit a task for background processing
    
    Args:
        func: The function to execute
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        
    Returns:
        str: The task ID
    """
    # Generate a unique task ID
    task_id = f"task_{int(time.time()*1000)}_{id(func)}"
    
    # Create a task object
    task = AsyncTask(task_id, func, args, kwargs)
    
    # Add it to the queue
    task_queue.put(task)
    
    logger.debug(f"Submitted task {task_id} to queue")
    
    return task_id

def get_task_status(task_id: str) -> Dict:
    """
    Get the status of a task
    
    Args:
        task_id: The ID of the task to check
        
    Returns:
        Dict: Task status information
    """
    # Check if task has completed
    if task_id in task_results:
        return {
            "task_id": task_id,
            "status": AsyncTaskStatus.COMPLETED,
            "result": task_results[task_id],
            "error": task_errors.get(task_id)
        }
    
    # Check if task has errored
    if task_id in task_errors and task_id not in task_results:
        return {
            "task_id": task_id,
            "status": AsyncTaskStatus.FAILED,
            "result": None,
            "error": task_errors[task_id]
        }
    
    # Task is still pending or running
    return {
        "task_id": task_id,
        "status": AsyncTaskStatus.PENDING,  # We can't distinguish between pending and running
        "result": None,
        "error": None
    }

def wait_for_task(task_id: str, timeout: Optional[float] = None) -> Dict:
    """
    Wait for a task to complete
    
    Args:
        task_id: The ID of the task to wait for
        timeout: Maximum time to wait in seconds, or None to wait indefinitely
        
    Returns:
        Dict: Task status information
    """
    start_time = time.time()
    
    while True:
        # Check if task has completed or failed
        status = get_task_status(task_id)
        if status["status"] in [AsyncTaskStatus.COMPLETED, AsyncTaskStatus.FAILED]:
            return status
        
        # Check if we've timed out
        if timeout is not None and time.time() - start_time > timeout:
            return {
                "task_id": task_id,
                "status": "timeout",
                "result": None,
                "error": "Task timed out"
            }
        
        # Sleep briefly to avoid hammering the CPU
        time.sleep(0.1)

async def run_in_thread(func: Callable, *args, **kwargs) -> Any:
    """
    Run a function in a thread and await its result
    
    This is useful for running blocking IO operations in an async context.
    
    Args:
        func: The function to execute
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        
    Returns:
        Any: The function's return value
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        thread_pool, 
        functools.partial(func, *args, **kwargs)
    )

async def run_in_process(func: Callable, *args, **kwargs) -> Any:
    """
    Run a function in a separate process and await its result
    
    This is useful for CPU-intensive operations that would block the event loop.
    
    Args:
        func: The function to execute
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        
    Returns:
        Any: The function's return value
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        process_pool, 
        functools.partial(func, *args, **kwargs)
    )

async def run_tasks_parallel(tasks: List[Coroutine]) -> List[Any]:
    """
    Run multiple async tasks in parallel and wait for all results
    
    Args:
        tasks: List of coroutines to execute
        
    Returns:
        List[Any]: The results of all tasks
    """
    return await asyncio.gather(*tasks)

def create_task_context() -> Dict:
    """
    Create a task context dictionary for tracking task execution details
    
    Returns:
        Dict: Empty task context
    """
    return {
        "start_time": time.time(),
        "steps_completed": [],
        "current_step": None,
        "execution_times": {}
    }

def update_task_context(context: Dict, step: str, status: str = "completed") -> Dict:
    """
    Update a task context with information about a step
    
    Args:
        context: The task context to update
        step: The name of the step that was completed
        status: The status of the step
        
    Returns:
        Dict: The updated context
    """
    now = time.time()
    
    # If this is a new step, record the start time
    if step != context.get("current_step"):
        if context.get("current_step"):
            # Calculate execution time for previous step
            start = context.get("step_start_time", context["start_time"])
            context["execution_times"][context["current_step"]] = now - start
            
        # Update current step
        context["current_step"] = step
        context["step_start_time"] = now
    
    # If step is completed, add to completed steps
    if status == "completed":
        context["steps_completed"].append(step)
        # Calculate execution time
        start = context.get("step_start_time", context["start_time"])
        context["execution_times"][step] = now - start
        context["current_step"] = None
    
    return context

def cleanup():
    """Cleanup resources used by the async processor"""
    # Signal the worker thread to exit
    task_queue.put(None)
    
    # Wait for the thread to finish
    background_thread.join(timeout=2.0)
    
    # Shutdown the thread and process pools
    thread_pool.shutdown(wait=False)
    process_pool.shutdown(wait=False)
    
    logger.info("Async processor resources cleaned up")

# Register cleanup handler
import atexit
atexit.register(cleanup)