"""
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
Async Api Routes
Async Api functionality for the NOUS application
"""

from flask import Blueprint, render_template, session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated

async_api_bp = Blueprint('async_api', __name__)


def require_authentication():
    """Check if user is authenticated, allow demo mode"""
    from flask import session, request, redirect, url_for, jsonify
from utils.unified_auth import login_required, demo_allowed, get_demo_user, is_authenticated
    
    # Check session authentication
    if 'user' in session and session['user']:
        return None  # User is authenticated
    
    # Allow demo mode
    if request.args.get('demo') == 'true':
        return None  # Demo mode allowed
    
    # For API endpoints, return JSON error
    if request.path.startswith('/api/'):
        return jsonify({'error': "Demo mode - limited access", 'demo_available': True}), 401
    
    # For web routes, redirect to login
    return redirect(url_for("main.demo"))

def get_get_demo_user()():
    """Get current user from session with demo fallback"""
    from flask import session
    return session.get('user', {
        'id': 'demo_user',
        'name': 'Demo User',
        'email': 'demo@example.com',
        'is_demo': True
    })

def is_authenticated():
    """Check if user is authenticated"""
    from flask import session
    return 'user' in session and session['user'] is not None

Asynchronous API Routes

This module provides API endpoints for working with asynchronous tasks.
These endpoints allow clients to submit long-running tasks, check their status,
and retrieve results when completed.

@module: async_api
@author: NOUS Development Team
"""
import time
import logging
from typing import Dict, Any
from flask import Blueprint, request, jsonify, current_app
from werkzeug.exceptions import BadRequest, NotFound

from utils.async_processor import (
    submit_task,
    get_task_status,
    wait_for_task,
    AsyncTaskStatus
)
from utils.security_helper import rate_limit
from utils.schema_validation import validate_with_schema

# Create blueprint
async_api = Blueprint('async_api', __name__, url_prefix='/api/async')

# Configure logger
logger = logging.getLogger(__name__)

# Example function for a CPU-intensive task
def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number recursively (intentionally inefficient)"""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

# Example function for a long-running IO task
def simulate_api_call(duration: int) -> Dict[str, Any]:
    """Simulate a long-running API call"""
    start_time = time.time()

    # Simulate work
    time.sleep(duration)

    return {
        "success": True,
        "duration": duration,
        "execution_time": time.time() - start_time
    }

# Example function for an embedded processing task
def process_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a data object with simulated work"""
    result = {}

    # Simulate complex processing
    time.sleep(1)

    # Process each field
    if "text" in data:
        # Simulate text processing
        result["text_length"] = len(data["text"])
        result["word_count"] = len(data["text"].split())
        time.sleep(0.5)

    if "numbers" in data and isinstance(data["numbers"], list):
        # Simulate number processing
        result["sum"] = sum(data["numbers"])
        result["average"] = sum(data["numbers"]) / len(data["numbers"]) if data["numbers"] else 0
        time.sleep(0.5)

    return result

@async_api.route('/tasks/fibonacci', methods=['POST'])
@rate_limit(max_requests=10, time_window=60)
@validate_with_schema("fibonacci")
def start_fibonacci_task():
    """
    Start a Fibonacci calculation task

    Request JSON:
    {
        "n": 30  # The Fibonacci number to calculate
    }

    Response:
    {
        "task_id": "task_12345",
        "status": "pending"
    }
    """
    data = request.get_json()
    n = data['n']

    # Submit the task
    task_id = submit_task(fibonacci, n)

    return jsonify({
        "task_id": task_id,
        "status": AsyncTaskStatus.PENDING
    })

@async_api.route('/tasks/api_simulation', methods=['POST'])
@rate_limit(max_requests=10, time_window=60)
@validate_with_schema("api_simulation")
def start_api_simulation():
    """
    Start a simulated API call task

    Request JSON:
    {
        "duration": 5  # The duration in seconds
    }

    Response:
    {
        "task_id": "task_12345",
        "status": "pending"
    }
    """
    data = request.get_json()
    duration = data['duration']

    # Submit the task
    task_id = submit_task(simulate_api_call, duration)

    return jsonify({
        "task_id": task_id,
        "status": AsyncTaskStatus.PENDING
    })

@async_api.route('/tasks/process_data', methods=['POST'])
@rate_limit(max_requests=10, time_window=60)
@validate_with_schema("process_data")
def start_data_processing():
    """
    Start a data processing task

    Request JSON:
    {
        "data": {
            "text": "Sample text to process",
            "numbers": [1, 2, 3, 4, 5]
        }
    }

    Response:
    {
        "task_id": "task_12345",
        "status": "pending"
    }
    """
    data = request.get_json()

    # Submit the task
    task_id = submit_task(process_data, data['data'])

    return jsonify({
        "task_id": task_id,
        "status": AsyncTaskStatus.PENDING
    })

@async_api.route('/tasks/<task_id>', methods=['GET'])

    # Check authentication
    auth_result = require_authentication()
    if auth_result:
        return auth_result

def get_task_result(task_id):
    """
    Get the result of a task

    Response:
    {
        "task_id": "task_12345",
        "status": "completed",
        "result": {...},
        "error": null
    }
    """
    # Check if we should wait for the task
    wait_for_completion = request.args.get('wait', 'false').lower() == 'true'
    timeout = int(request.args.get('timeout', '0')) if request.args.get('timeout') else None

    if wait_for_completion and timeout:
        # Wait for the task with timeout
        status = wait_for_task(task_id, timeout)
    else:
        # Just get current status
        status = get_task_status(task_id)

    return jsonify(status)

# Register error handlers
@async_api.errorhandler(BadRequest)
def handle_bad_request(error):
    """Handle bad request errors"""
    response = jsonify({
        "error": "Bad Request",
        "message": str(error.description)
    })
    response.status_code = 400
    return response

@async_api.errorhandler(NotFound)
def handle_not_found(error):
    """Handle not found errors"""
    response = jsonify({
        "error": "Not Found",
        "message": str(error.description)
    })
    response.status_code = 404
    return response