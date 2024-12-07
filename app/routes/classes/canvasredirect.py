from app import app
from flask import redirect
from app.utilities.canvas import canvas_url
from app.utilities.classes import get_user_current_period
from app.utilities.users import verify_user

@app.route('/canvas')
@verify_user
def canvas(user):
    period = get_user_current_period(user)
    if period is None or period['course'] is None or period.canvasid is None:
        return redirect(canvas_url)
    return redirect(f"{canvas_url}/courses/{period.canvasid}")

@app.route('/canvas/<path>')
@verify_user
def canvas_with_path(user, path):
    period = get_user_current_period(user)
    if period is None or period['course'] is None or period.canvasid is None:
        return redirect(canvas_url)
    return redirect(f"{canvas_url}/courses/{period.canvasid}/{path}")