from app import app
from flask import send_from_directory, render_template
from app.utilities.env import devmode


@app.route("/index.css")
def index_css():
    return send_from_directory("static", "index.css")

@app.route("/favicon.ico")
def favicon():
    return send_from_directory("static", "favicondev.ico" if devmode else "favicon.ico")

@app.route("/privacy")
def privacy():
    return render_template("privacy.html")