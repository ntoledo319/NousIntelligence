"""
NOUS Personal Assistant - Gunicorn Configuration

This file configures Gunicorn for production deployment.
"""

import os
import multiprocessing

# Bind to all network interfaces on the specified port
bind = "0.0.0.0:" + os.environ.get("PORT", "8080")

# Number of worker processes
# A good rule of thumb is (2 x number of CPUs) + 1
workers = int(os.environ.get("GUNICORN_WORKERS", multiprocessing.cpu_count() * 2 + 1))

# Maximum number of simultaneous clients per worker
worker_connections = 1000

# Maximum number of requests a worker will process before restarting
max_requests = 1000
max_requests_jitter = 50

# Worker timeout in seconds
timeout = 120

# Keep the workers alive for this many seconds after a restart
graceful_timeout = 30

# Restart workers that have taken more than this many seconds to boot
worker_boot_timeout = 60

# Access log format
accesslog = "-"  # stdout
errorlog = "-"   # stderr
loglevel = "info"

# Process name
proc_name = "nous_app"

# Set environment variables
raw_env = [
    "FLASK_ENV=production",
    "PYTHONUNBUFFERED=1"
]

# Pre-load application to reduce startup time
preload_app = True

# Gunicorn hooks
def on_starting(server):
    """
    Log when Gunicorn is starting
    """
    print("Gunicorn starting...")

def on_exit(server):
    """
    Log when Gunicorn is shutting down
    """
    print("Gunicorn shutting down...")