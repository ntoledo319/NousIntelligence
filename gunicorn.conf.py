# Gunicorn Production Configuration
import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.environ.get('PORT', '8080')}"
backlog = 2048

# Worker processes - optimized for Replit
workers = min(multiprocessing.cpu_count() * 2 + 1, 4)  # Cap at 4 for Replit
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers for memory management
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "nous-assistant"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance optimizations
enable_stdio_inheritance = True
sendfile = True