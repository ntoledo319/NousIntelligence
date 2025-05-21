"""
Gunicorn Configuration

This file contains production-ready settings for Gunicorn to ensure
the application runs reliably and continuously in production environments.
"""

import multiprocessing
import os

# Server socket settings - Using PORT from environment or default to 8080 for Replit
port = int(os.environ.get("PORT", 8080))
bind = f"0.0.0.0:{port}"
backlog = 2048

# Worker processes - Adjust based on available memory on Replit
workers = 2  # Replit has limited resources, so use fewer workers
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'nous-app'
default_proc_name = 'gunicorn'

# Server mechanics
daemon = False
raw_env = [
    f"FLASK_APP=main.py",
    f"FLASK_ENV=production"
]
pythonpath = None
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Server hooks
def on_starting(server):
    """Log when server starts and verify critical requirements"""
    print(f"Starting Gunicorn server on port {port} with production settings")
    
    # Ensure directories exist and have proper permissions
    for directory in ['flask_session', 'uploads', 'logs', 'instance']:
        os.makedirs(directory, exist_ok=True)
        os.chmod(directory, 0o777)  # Ensure directory is writable
    
    # Verify critical environment variables
    critical_vars = ['DATABASE_URL']
    optional_vars = ['SECRET_KEY', 'SESSION_SECRET', 'GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET']
    
    for var in critical_vars:
        if not os.environ.get(var):
            print(f"WARNING: Critical environment variable {var} is not set!")
    
    # At least one of SECRET_KEY or SESSION_SECRET must be set
    if not os.environ.get('SECRET_KEY') and not os.environ.get('SESSION_SECRET'):
        print("WARNING: Neither SECRET_KEY nor SESSION_SECRET is set!")
    
    for var in optional_vars:
        if not os.environ.get(var):
            print(f"Note: Optional environment variable {var} is not set")

def on_exit(server):
    """Log when server exits and perform cleanup"""
    print("Shutting down Gunicorn server")
    
    # Close any resources that might need explicit closing
    import gc
    gc.collect()  # Force garbage collection to clean up resources

# Process management
max_requests = 1000
max_requests_jitter = 50
graceful_timeout = 30
preload_app = True

def post_fork(server, worker):
    """Setup after forking worker processes"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Setup before forking worker processes"""
    pass

def pre_exec(server):
    """Setup before exec-ing a new binary of ourselves"""
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Server is ready. Spawning workers")
    
    # Create necessary directories
    for directory in ['flask_session', 'uploads', 'logs']:
        os.makedirs(directory, exist_ok=True)

def worker_int(worker):
    """Called when a worker receives SIGINT signal"""
    worker.log.info("worker received INT signal")

def worker_abort(worker):
    """Called when a worker receives SIGABRT signal"""
    worker.log.info("worker received ABORT signal")

# SSL Configuration
keyfile = None
certfile = None
ca_certs = None