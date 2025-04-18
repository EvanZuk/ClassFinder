# pylint: disable=missing-function-docstring
"""
Static routes for the application.
"""

from flask import send_from_directory, render_template
from app import app
from app.utilities.config import devmode

@app.route("/index.css")
def index_css():
    """
    Serves the index.css file.
    """
    return send_from_directory("static", "index.css")

@app.route("/favicon.ico")
def favicon():
    """
    Serves the favicon.
    """
    return send_from_directory("static", "favicondev.ico" if devmode else "favicon.ico")

@app.route("/privacy")
def privacy():
    """
    Serves the privacy policy.
    """
    return render_template("privacy.html")

@app.route("/ping")
def ping():
    """
    Pings the server.
    """
    return "Pong"

@app.route("/robots.txt")
def robots():
    """
    Returns a robots.txt.
    """
    return """
        User-agent: *
        Disallow: /
    """ # There is no reason to allow robots to index this site, as it is not a public site.
