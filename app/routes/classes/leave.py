from app import app
from flask import request
from app.utilities.users import verify_user
from app.utilities.responses import success_response, error_response
from app.utilities.classes import get_periods_of_user_classes, remove_class, get_course_by_id, remove_user_from_class
from app.utilities.config import canvas_url, allow_leave

@app.route("/classes/<classid>/leave", methods=["POST"])
@verify_user
def leave_class(classid):
    user = request.user
    if not allow_leave:
        return error_response("Leaving classes is disabled")
    course = get_course_by_id(classid)
    if course.period == "Access":
        return error_response("You cannot leave your Access class")
    if course is None:
        return error_response("Course not found")
    if course not in user.classes:
        return error_response("You are not in that class")
    remove_user_from_class(user, course)
    return success_response("Left class successfully")