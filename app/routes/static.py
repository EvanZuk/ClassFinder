# pylint: disable=missing-function-docstring
"""
Static routes for the application.
"""
import os
from flask import Response
from flask import send_from_directory, render_template
from app import app
from app.utilities.config import devmode

@app.route("/index.css")
def index_css():
    """
    Serves the index.css file.
    """

    if not devmode:
        return send_from_directory("static", "index.css")

    # Read index.css
    with open(os.path.join(app.static_folder, "index.css"), "r", encoding="UTF-8") as f:
        css_content = f.read()

    # Append colors-dev.css
    try:
        with open(os.path.join(app.static_folder, "colors-dev.css"), "r", encoding="UTF-8") as f:
            css_content += "\n\n/* Development mode styles */\n" + f.read()
    except (IOError, FileNotFoundError):
        app.logger.warning("colors-dev.css not found")

    return Response(css_content, mimetype="text/css")

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
