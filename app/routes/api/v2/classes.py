from app import app
from app.utilities.users import verify_user
from app.utilities.classes import get_user_current_period, get_today_courses, get_current_period
from app.utilities.responses import success_response, error_response
from datetime import datetime

@app.route("/api/v2/classes/current")
@verify_user(onfail=lambda:(error_response("You must be logged in to do that."), 401))
def current_classes(user):
    currentperiod = get_user_current_period(user)
    app.logger.debug(f"Current period: {currentperiod}")
    return success_response(None, {
        "classes": {
            c.period: {
                "id": c.id,
                "name": c.name,
                "room": c.room,
                "lunch": c.lunch,
                "verified": c.verified,
                "canvasid": c.canvasid
            } for c in get_today_courses(user)
        },
        "period": currentperiod['period'] if currentperiod is not None else None,
        "endtime": int(datetime.combine(datetime.today(), currentperiod['end']).timestamp()) if (currentperiod is not None) else None,
        "passing": currentperiod['passing'] if currentperiod is not None and 'passing' in currentperiod else None,
        "lunch": currentperiod['lunch'] if currentperiod is not None else None
    })

@app.route("/api/v2/classes/all")
@verify_user(onfail=lambda:(error_response("You must be logged in to do that."), 401))
def all_classes(user):
    return success_response(None, {
        "classes": {
            c.id: {
                "name": c.name,
                "room": c.room,
                "period": c.period,
                "lunch": c.lunch,
                "verified": c.verified,
                "canvasid": c.canvasid
            } for c in user.classes
        }
    })

@app.route("/api/v2/classes/timeuntilend")
def time_until_end():
    currentperiod = get_current_period()
    return success_response(None, {
        "time": int(datetime.combine(datetime.today(), currentperiod['end']).timestamp()) if (currentperiod is not None) else None,
        "passing": currentperiod['passing'] if currentperiod is not None and 'passing' in currentperiod else None,
        "period": currentperiod['period'] if currentperiod is not None else None,
    })