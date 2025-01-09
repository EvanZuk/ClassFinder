from app import app
from app.utilities.times import create_schedule_pdf
from app.utilities.users import verify_user
from flask import request, send_file

@app.route("/classes/schedulepdf", methods=["GET"])
@verify_user(required=False)
def schedulepdf(user):
    return send_file(create_schedule_pdf(user), download_name=f"schedule.pdf")

@app.route("/classes/schedulepdf/<days>", methods=["GET"])
@verify_user(required=False)
def schedulepdfday(user, days):
    if days == "all":
        ndays = "0,1,2,3,4,7,8"
    else:
        ndays = days.lower().replace("monday", "0").replace("m", "0").replace("tuesday", "1").replace("t", "1").replace("wednesday", "2").replace("w", "2").replace("thursday", "3").replace("r", "3").replace("friday", "4").replace("f", "4").replace("eb", "7").replace("eg", "8")
    return send_file(create_schedule_pdf(user, [int(day) for day in ndays.split(",")]), download_name=f"schedule.pdf")