from app import app
from app.utilities.users import verify_user
from app.utilities.classes import get_user_current_period, get_today_courses
from app.utilities.responses import success_response, error_response
from datetime import datetime

@app.route("/api/v2/classes/current")
@verify_user
def current_classes(user):
    currentperiod = get_user_current_period(user)
    return success_response(None, {
        "classes": [
            {
                "name": c.name,
                "room": c.room,
                "period": c.period,
                "lunch": c.lunch,
                "verified": c.verified,
                "canvasid": c.canvasid
            } for c in get_today_courses(user)
        ],
        "period": currentperiod['period'],
        "endtime": int(datetime.combine(datetime.today(), currentperiod['end']).timestamp()) if (currentperiod is not None) else None,
    })

@app.route("/api/v2/classes/all")
@verify_user
def all_classes(user):
    return success_response(None, {
        "classes": [
            {
                "name": c.name,
                "room": c.room,
                "period": c.period,
                "lunch": c.lunch,
                "verified": c.verified,
                "canvasid": c.canvasid
            } for c in user.classes
        ]
    })