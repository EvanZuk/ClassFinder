from app import app
from app.utilities.times import create_time_pdf, create_personal_time_pdf
from app.utilities.users import verify_user
from flask import request, send_file

@app.route("/classes/schedulepdf", methods=["GET"])
def schedulepdf():
    return send_file(create_time_pdf(), download_name="schedule.pdf")

@app.route("/classes/personalschedulepdf", methods=["GET"])
@verify_user
def personalschedulepdf(user):
    return send_file(create_personal_time_pdf(user), download_name="schedule.pdf")

@app.route("/classes/personalschedulepdf/<day>", methods=["GET"])
@verify_user
def personalschedulepdf_day(user, day):
    return send_file(create_personal_time_pdf(user, int(day)), download_name="schedule.pdf")