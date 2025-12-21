"""
Gunicorn configuration file with gevent workers
Optimized for low-memory environments (Render Free: 512MB)
"""
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"  # Render uses PORT env variable
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', '2'))  # Default 2 workers (optimized for 512MB)
worker_class = 'sync'
worker_connections = 1000
max_requests = 5000
max_requests_jitter = 500
timeout = 60
keepalive = 2
threads = 2

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'anime-world-addon'

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = None
# certfile = None
