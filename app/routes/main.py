from app import app
from flask import render_template
from app.utilities.users import verify_user
from datetime import datetime
from app.utilities.classes import (
    get_today_courses,
    neededperiods,
    get_periods_of_user_classes,
    get_user_current_period,
)
from app.utilities.canvas import canvas_url


@app.route("/dashboard")
@verify_user
def dashboard(user):
    currentperiod = get_user_current_period(user)
    app.logger.debug(currentperiod)
    return render_template(
        "dashboard.html",
        classes=user.classes,
        username=user.username,
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
    )
