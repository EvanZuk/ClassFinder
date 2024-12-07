from app import app
from app.utilities.times import set_schedule
from app.utilities.users import verify_user
from datetime import date, datetime
from flask import render_template, request, redirect, url_for
from app.utilities.responses import success_response, error_response


@app.route("/admin/times/schedule")
@verify_user(allowed_roles=["admin"])
def schedule(user):
    return render_template("schedule.html")


@app.route("/admin/times/schedule", methods=["POST"])
@verify_user(allowed_roles=["admin"])
def schedule_post(user):
    start = datetime.strptime(request.json.get("start"), "%Y-%m-%d").date()
    end = datetime.strptime(request.json.get("end"), "%Y-%m-%d").date()
    day = int(request.json.get("day"))
    app.logger.info(f"Received schedule request for {start} to {end} with day {day}")
    set_schedule(start, end, day)
    return success_response("Schedule set")
