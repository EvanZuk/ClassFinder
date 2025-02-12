from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import importlib
import logging
from flask_apscheduler import APScheduler
from app.utilities.config import devmode
from datetime import datetime


app = Flask(__name__, template_folder="templates", static_folder="static")
#app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_proto=2, x_host=2, x_port=2, x_prefix=2)

@app.before_request
def fix_ip():
    if request.headers.get("Cf-Connecting-Ip"):
        request.remote_addr = request.headers.get("Cf-Connecting-Ip")

app.secret_key = os.environ.get("APP_KEY", "devkey")

app.logger.setLevel(os.environ.get("LOG_LEVEL", "DEBUG" if devmode else "INFO"))

app.config["POSTHOG_API_KEY"] = os.environ.get("POSTHOG_API_KEY")

class CustomFormatter(logging.Formatter):
    def format(self, record):
        relative_path = os.path.relpath(record.pathname, os.path.dirname(__file__)).removesuffix(".py")
        reset_color = "\033[0m"
        level_color = {
            "DEBUG": "\033[97m",  # white
            "INFO": "\033[94m",   # blue
            "WARNING": "\033[93m", # yellow
            "ERROR": "\033[91m",  # red
            "CRITICAL": "\033[91m" # red
        }.get(record.levelname, reset_color)  # default to no color
        bold = "\033[1m"
        if os.path.basename(record.pathname) == "__init__.py":
            return f"{bold}{level_color}{record.levelname}{reset_color}{level_color}: {record.getMessage().replace('\033[0m', '\033[0m'+level_color)}{reset_color}"
        else:
            return f"{bold}{level_color}{record.levelname}{reset_color}{level_color} in {bold}{relative_path}{reset_color}{level_color} at {bold}{record.lineno}{reset_color}{level_color}: {record.getMessage()}{reset_color}"

formatter = CustomFormatter()
handler = logging.StreamHandler()
handler.setFormatter(formatter)
app.logger.handlers.clear()
app.logger.addHandler(handler)

# Configure waitress logger to use the same handler
waitress_logger = logging.getLogger('waitress')
waitress_logger.handlers.clear()
waitress_logger.addHandler(handler)

@app.before_request
def log_request():
    reset_color = "\033[0m"
    method_colors = {
        "GET": "\033[92m",  # green
        "POST": "\033[96m", # cyan
        "PUT": "\033[95m",  # purple
        "DELETE": "\033[91m", # red
        "PATCH": "\033[94m", # blue
    }
    method_color = method_colors.get(request.method, "\033[97m")  # white
    params = request.args.to_dict() if request.method == 'GET' else request.json
    if isinstance(params, dict):
        if params.get("password"):
            params["password"] = ("*" * len(params["password"])) if len(params["password"]) < 25 else "*****"
        if params.get("token"):
            params["token"] = params["token"][:3] + "*" * (len(params["token"]) - 2)
    app.logger.debug(f"Processing {method_color}{request.method}{reset_color} {request.path} with {str(params)}")

@app.after_request
def log_response(response):
    reset_color = "\033[0m"
    status_colors = {
        200: "\033[92m",  # green
        201: "\033[96m",  # cyan
        204: "\033[96m",  # cyan
        304: "\033[96m",  # cyan
        300: "\033[96m",  # cyan
        301: "\033[96m",  # cyan
        302: "\033[96m",  # cyan
        400: "\033[93m",  # yellow
        401: "\033[91m",  # red
        403: "\033[91m",  # red
        404: "\033[91m",  # red
        429: "\033[93m",  # yellow
        500: "\033[91m",  # red
    }
    method_colors = {
        "GET": "\033[92m",  # green
        "POST": "\033[96m", # cyan
        "PUT": "\033[95m",  # purple
        "DELETE": "\033[91m", # red
        "PATCH": "\033[94m", # blue
    }
    status_color = status_colors.get(response.status_code, "\033[97m")  # white
    method_color = method_colors.get(request.method, "\033[97m") # white
    app.logger.debug(f"Response for {method_color}{request.method}{reset_color} {request.path} is {status_color}{response.status_code}{reset_color}")
    # PostHog integration
    if response.content_type == "text/html":
        response.set_data(response.get_data(as_text=True).replace("<head>", "<head><title>Classfinder</title>"))
    return response

def import_routes(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                module_name = (
                    os.path.join(root, file)
                    .replace(directory, "app.routes")
                    .replace(os.sep, ".")
                    .replace(".py", "")
                )
                btime = datetime.now()
                importlib.import_module(module_name)
                atime = datetime.now()
                app.logger.debug(f"Imported {module_name} in {(atime - btime).total_seconds()}s")


import_routes(os.path.join(os.path.dirname(__file__), "routes"))

scheduler = APScheduler()
from app.db import db_cleanup

@scheduler.task("cron", hour=2, misfire_grace_time=3600)
def do_daily_tasks():
    app.logger.info("Cleaning up database...")
    db_cleanup()

app.logger.info("Runing daily tasks for initialization")
with app.app_context():
    btime = datetime.now()
    do_daily_tasks()
    atime = datetime.now()
    app.logger.info(f"Daily tasks completed in {(atime - btime).total_seconds()}s")

scheduler.init_app(app)
scheduler.start()

# Disable the werkzeug logger to prevent double logging
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.ERROR)

for logger in [logging.getLogger('waitress')]:
    logger.disabled = True

for handler in app.logger.handlers[:]:
    app.logger.removeHandler(handler)
app.logger.addHandler(handler)

class CustomWerkzeugFormatter(logging.Formatter):
    def format(self, record):
        if "Exception" in record.getMessage() or "Traceback" in record.getMessage():
            return super().format(record)
        return ""

werkzeug_logger.handlers.clear()
werkzeug_handler = logging.StreamHandler()
werkzeug_handler.setFormatter(CustomWerkzeugFormatter())
werkzeug_handler.addFilter(lambda record: "Exception" in record.getMessage() or "Traceback" in record.getMessage())
werkzeug_logger.addHandler(werkzeug_handler)
logging.basicConfig(handlers=[werkzeug_handler], level=app.logger.level)

app.logger.info("App initialized")

app.logger.info(f"Starting app on {os.environ.get('FLASK_RUN_HOST', '127.0.0.1')}:{os.environ.get('FLASK_RUN_PORT', '5000')} ...")
