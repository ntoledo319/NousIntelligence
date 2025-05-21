"""
Gunicorn Configuration

This file contains production-ready settings for Gunicorn to ensure
the application runs reliably and continuously in production environments.
"""

import multiprocessing
import os

# Server socket settings
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Process naming
proc_name = 'nous-app'
default_proc_name = 'gunicorn'

# Server mechanics
daemon = False
raw_env = []
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
    """Log when server starts"""
    print("Starting Gunicorn server with production settings")

def on_exit(server):
    """Log when server exits"""
    print("Shutting down Gunicorn server")

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