"""
Account routes
"""

from flask import render_template, request
from app import app
from app.utilities.users import verify_user, delete_user, change_username
from app.utilities.responses import success_response
from app.utilities.classes import (
    get_today_courses,
    neededperiods,
    get_periods_of_user_classes,
)
from app.utilities.config import canvas_url, allow_leave


@app.route("/account")
@verify_user
def account():
    """
    This route displays the user's account information.
    """
    user = request.user
    needcanvaslink = False
    for course in user.classes:
        if course.canvasid is None:
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
    """
    This route displays the account deletion page.
    """
    return render_template("account_delete.html")

@app.route("/account/delete", methods=["POST"])
@verify_user
def account_delete():
    """
    This route deletes the user's account.
    """
    delete_user(request.user)
    return success_response("User deleted successfully")

@app.route("/account/changeusername")
@verify_user
def account_changeusername_get():
    """
    This route displays the username change page.
    """
    if not request.user.requires_username_change:
        return {"error": "Username change not required"}, 400
    return render_template("changeusername.html")

@app.route("/account/changeusername", methods=["POST"])
@verify_user
def account_changeusername():
    """
    This route changes the user's username.
    """
    if not request.user.requires_username_change:
        return {"error": "Username change not required"}, 400
    newusername = request.json.get("username")
    if not newusername:
        return {"error": "No username provided"}, 400
    change_username(request.user, newusername, requires_change=False)
    return success_response("Username changed successfully")

