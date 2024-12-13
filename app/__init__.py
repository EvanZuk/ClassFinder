from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import importlib
import logging

app = Flask(__name__, template_folder="templates", static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_proto=2, x_host=2, x_port=2, x_prefix=2)

app.secret_key = os.environ.get("APP_KEY", "devkey")
logging.getLogger("werkzeug").disabled = True

from app.utilities.env import devmode

app.logger.setLevel("DEBUG" if devmode else "INFO")

if devmode:
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
            return f"{bold}{level_color}{record.levelname}{reset_color}{level_color} in {bold}{relative_path}{reset_color}{level_color}: {record.getMessage()}{reset_color}"

    formatter = CustomFormatter()
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    app.logger.handlers.clear()
    app.logger.addHandler(handler)

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
                app.logger.debug(f"Importing {module_name}")
                importlib.import_module(module_name)


import_routes(os.path.join(os.path.dirname(__file__), "routes"))
from app.utilities.times import update_times
from app.db import db_cleanup

from flask_apscheduler import APScheduler

scheduler = APScheduler()


@scheduler.task("cron", hour=2, misfire_grace_time=3600)
def do_daily_tasks():
    app.logger.info("Running daily tasks...")
    update_times()
    db_cleanup()

app.logger.info("Runing daily tasks for initialization")
with app.app_context():
    do_daily_tasks()

scheduler.init_app(app)
scheduler.start()

app.logger.info("App initialized")