from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import importlib

app = Flask(__name__, template_folder="templates", static_folder="static")
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
app.secret_key = os.environ.get("APP_KEY", "devkey")

from app.utilities.env import devmode

app.logger.setLevel("DEBUG" if devmode else "INFO")


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