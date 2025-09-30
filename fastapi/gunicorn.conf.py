# gunicorn.conf.py
import multiprocessing

# Number of workers (Cloud Run handles scaling, so keep this small)
workers = 2
worker_class = "uvicorn.workers.UvicornWorker"

# Bind to Cloud Run expected port
bind = "0.0.0.0:8080"

# Timeout (avoid worker kill during cold starts)
timeout = 120

# Optional: preload app for slightly faster response, but may affect async DB init
# preload_app = True
