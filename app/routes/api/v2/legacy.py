from app import app
from app.utilities.users import verify_user
from app.utilities.classes import get_user_current_period
import datetime

@app.route("/api/plain/endtime")
@verify_user
def api_plain_endtime(user):
    period = get_user_current_period(user)
    end_time = period.get('end')
    if end_time:
        return datetime.datetime.combine(datetime.date.today(), end_time).timestamp()
    return "0"

@app.route("/api/plain/timeuntilclassend")
@verify_user
def api_plain_timeuntilclassend(user):
    period = get_user_current_period(user)
    if period:
        return str(int((datetime.datetime.combine(datetime.date.today(), period.get('end')) - datetime.datetime.now()).total_seconds()))
    return "0"