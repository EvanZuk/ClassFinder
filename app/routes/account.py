from app import app
from flask import render_template, request
from app.utilities.users import verify_user, delete_user
from app.utilities.responses import success_response, error_response
from app.utilities.classes import (
    get_today_courses,
    neededperiods,
    get_periods_of_user_classes,
)
from app.utilities.config import canvas_url, allow_leave


@app.route("/account")
@verify_user
def account():
    user = request.user
    needcanvaslink = False
    for course in user.classes:
        if course.canvasid == None:
            needcanvaslink = True
            break
    return render_template(
        "account.html",
        user=user,
        currentclasses=get_today_courses(user),
        classestoadd=[
            period
            for period in neededperiods
            if period not in get_periods_of_user_classes(user)
        ],
        neededperiods=neededperiods,
        canvasurl=canvas_url,
        needcanvaslink=needcanvaslink,
        allow_leave=allow_leave,
    )

@app.route("/account/delete", methods=["GET"])
def account_delete_get():
    return render_template("account_delete.html")

@app.route("/account/delete", methods=["POST"])
@verify_user
def account_delete():
    delete_user(request.user)
    return success_response("User deleted successfully")

