"""
This file contains the route for the /canvas endpoint, which redirects the user to the Canvas course page.
"""
from flask import redirect, request
from app import app
from app.utilities.config import canvas_url
from app.utilities.classes import get_user_current_period
from app.utilities.users import verify_user

@app.route("/canvas")
@verify_user
def canvas():
    """
    Redirects the user to the Canvas course page.
    """
    user = request.user
    period = get_user_current_period(user)
    if period is None or period["course"] is None or period["course"].canvasid is None:
        reason = "no current period" if period is None else "no course for period" if period["course"] is None else "course has no Canvas ID"
        app.logger.debug(f"Redirecting user {user.username} to Canvas homepage: {reason}")
        return redirect(canvas_url)
    app.logger.debug(f"Redirecting user {user.username} to Canvas course {period['course'].canvasid}")
    return redirect(f"{canvas_url}/courses/{period['course'].canvasid}")


@app.route("/canvas/<path>")
@verify_user
def canvas_with_path(path):
    """
    Redirects the user to the Canvas course page with a path
    """
    user = request.user
    period = get_user_current_period(user)
    if period is None or period["course"] is None or period["course"].canvasid is None:
        reason = "no current period" if period is None else "no course for period" if period["course"] is None else "course has no Canvas ID"
        app.logger.debug(f"Redirecting user {user.username} to Canvas homepage: {reason}")
        return redirect(f"{canvas_url}/{path}")
    app.logger.debug(f"Redirecting user {user.username} to Canvas course {period['course'].canvasid} with path {path}")
    return redirect(f"{canvas_url}/courses/{period['course'].canvasid}/{path}")
