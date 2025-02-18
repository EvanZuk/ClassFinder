from app import app
from app.utilities.users import verify_user
from app.utilities.classes import set_lunch, get_course_by_id
from app.utilities.responses import success_response, error_response
from flask import request, render_template


@app.route("/class/<courseid>/setlunch")
@verify_user
def setlunch(courseid):
    course = get_course_by_id(courseid)
    if not course:
        return error_response("Course not found."), 404
    return render_template("setlunch.html", course=course)


@app.route("/class/<courseid>/setlunch", methods=["POST"])
@verify_user
def setlunch_post(courseid):
    user = request.user
    course = get_course_by_id(courseid)
    if course not in user.classes:
        return error_response("Course not found."), 404
    lunch = request.json.get("lunch")
    if lunch in ["A", "B", "C"]:
        set_lunch(course, lunch)
        return success_response("Lunch set."), 200
    app.logger.debug(f"Invalid lunch period: {lunch}")
    return error_response("Invalid lunch period."), 400
