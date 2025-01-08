import requests
from flask import render_template, request, redirect, url_for
from app import app
from app.utilities.users import verify_user
from app.utilities.classes import set_canvas_id
from app.utilities.responses import success_response
from app.utilities.config import canvas_url
from app.addons.limiter import limiter


@app.route("/classes/canvaslink")
@verify_user
def canvaslink(user):
    newcourses = []
    for course in user.classes:
        app.logger.debug(
            f"Checking if course {course.name} is linked to a canvas course."
        )
        if course.canvasid is None:
            app.logger.debug(f"Course {course.name} is not linked to a canvas course.")
            newcourses.append(course)
            if request.args.get("token") is None:
                return render_template("canvasaskfortoken.html")
        else:
            app.logger.debug(
                f"Course {course.name} is already linked to a canvas course: {course.canvasid}"
            )
    if len(newcourses) == 0:
        app.logger.debug(f"User {user.username} has no courses to link to canvas.")
        return redirect(url_for("dashboard"))
    cards = requests.get(
        f"{canvas_url}/api/v1/dashboard/dashboard_cards",
        headers={"Authorization": f'Bearer {request.args.get("token")}'},
    )
    app.logger.debug(cards.text)
    if cards.status_code != 200:
        return redirect(url_for("canvaslink"))
    newcards = {}
    ids_for_existing_courses = []
    for course in user.classes:
        if course.canvasid is not None:
            ids_for_existing_courses.append(course.canvasid)
    for card in cards.json():
        if card["id"] in ids_for_existing_courses:
            continue
        newcards[card["id"]] = card["shortName"]
    return render_template("canvaslink.html", courses=newcourses, cards=newcards)


@app.route("/classes/canvaslink", methods=["POST"])
@limiter.limit("2/minute")
@verify_user
def canvaslink_post(user):
    token = request.args.get("token")
    for course in user.classes:
        if course.canvasid is None:
            if request.json.get(str(course.id)) is not None:
                if request.json.get(str(course.id)).isdigit():
                    set_canvas_id(course, request.json.get(str(course.id)))
                else:
                    app.logger.debug(
                        f"Course {course.name} was not linked to a canvas course by {user.username} because the canvas course id was not a number."
                    )
            else:
                app.logger.debug(
                    f"Course {course.name} was not linked to a canvas course by {user.username}"
                )
        else:
            app.logger.debug(
                f"Course {course.name} is already linked to a canvas course: {course.canvasid}"
            )
    if isinstance(token, str):
        requests.delete(
            f"{canvas_url}/login/oauth2/token",
            headers={"Authorization": f"Bearer {token}"},
        )
    return success_response("Courses linked successfully."), 200
