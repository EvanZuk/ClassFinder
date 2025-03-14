"""
Hosts the dashboard route.
"""

from datetime import datetime, timedelta
from flask import render_template, request, make_response
from app import app
from app.utilities.users import verify_user
from app.utilities.classes import (
    get_today_courses,
    neededperiods,
    get_periods_of_user_classes,
    get_user_current_period,
)
from app.utilities.times import get_lunchtimes
from app.utilities.config import canvas_url


@app.route("/dashboard")
@verify_user
def dashboard():
    """
    Hosts the dashboard route.
    """
    user = request.user
    currentperiod = get_user_current_period(user)
    app.logger.debug(currentperiod)
    response = make_response(
        render_template(
            "dashboard.html",
            classes=user.classes,
            user=user,
            currentperiod=currentperiod,
            endtime=datetime.combine(datetime.today(), currentperiod['end']).strftime("%m/%d/%Y %I:%M %p") if (currentperiod is not None) else None,
            currentclasses=get_today_courses(user),
            classestoadd=len(
                [
                    period
                    for period in neededperiods
                    if period not in get_periods_of_user_classes(user)
                ]
            ),
            canvasurl=canvas_url,
            lunchtimes=get_lunchtimes(),
        ),
    )
    # if currentperiod is not None:
    #     end_time = datetime.combine(datetime.today(), currentperiod['end'])
    # else:
    #     end_time = datetime.combine(datetime.today(), datetime.strptime("06:00", "%H:%M").time())
    #     end_time += timedelta(days=1)

    # response.headers["Cache-Control"] = f"max-age={round((end_time - datetime.now()).total_seconds())}, immutable, must-revalidate, private"
    return response

