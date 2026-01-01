# Flask Application - Gunicorn WSGI Server Configuration
# Use this for production deployment with Apache2 reverse proxy

[unix_http_socket]
bind = 127.0.0.1:8000
workers = 4
worker_class = sync
threads = 2
timeout = 30
keepalive = 2

# Logging
accesslog = -
errorlog = -
loglevel = info

# Process naming
proc_name = flask_app

# Server mechanics
daemon = False
pidfile = None
tmp_upload_dir = None

# SSL (if using SSL)
# keyfile = /path/to/keyfile.key
# certfile = /path/to/certfile.crt
# ca_certs = /path/to/ca.pem

# Application
wsgi_app = wsgi:app
