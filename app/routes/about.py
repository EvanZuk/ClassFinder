from app import app
from flask import render_template, redirect
from app.utilities.config import devmode
from app.utilities.users import get_user_count, verify_user


@app.route("/")
@verify_user(required=False)
def index(user):
    if user:
        app.logger.debug(f"{user.username} is already logged in, redirecting to dashboard")
        return redirect("/dashboard")
    return render_template("index.html", devmode=devmode, user_count=get_user_count())
