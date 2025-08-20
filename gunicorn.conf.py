import multiprocessing

bind = "0.0.0.0:5000"
backlog = 2048

workers = max(2, multiprocessing.cpu_count() // 2)
worker_class = "gthread"
threads = 8
timeout = 120
keepalive = 5

preload_app = True

accesslog = "-"
errorlog = "-"
loglevel = "info"
proc_name = "weather-app"
daemon = False
pidfile = "/tmp/gunicorn.pid"

limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
