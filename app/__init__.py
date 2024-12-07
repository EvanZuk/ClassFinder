from flask_apscheduler import APScheduler
from app.utilities.times import update_times
from app.utilities.env import devmode
from flask import Flask
import os
import importlib

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("APP_KEY", "devkey")

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
app.logger.info("Updating times for init...")
update_times()

scheduler = APScheduler()


@scheduler.task("cron", hour=2, misfire_grace_time=3600)
def do_update_times():
    app.logger.info("Updating times...")
    update_times()


scheduler.init_app(app)
scheduler.start()
