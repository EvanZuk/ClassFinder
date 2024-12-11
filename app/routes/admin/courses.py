from app import app
from flask import render_template, abort, request
from app.utilities.users import verify_user
from app.utilities.classes import get_course_by_id, remove_class
from app.utilities.responses import success_response, error_response
from app.db import db


@app.route("/admin/class/<courseid>", methods=["DELETE"])
@verify_user(allowed_roles=["admin"])
def delete_course(user, courseid):
    course = get_course_by_id(courseid)
    if course:
        remove_class(course)
        return success_response("Course deleted."), 200
    return error_response("Course not found."), 404


@app.route("/admin/class/<courseid>/edit")
@verify_user(allowed_roles=["admin"])
def edit_course(user, courseid):
    course = get_course_by_id(courseid)
    if course:
        return render_template("editcourse.html", course=course)
    app.logger.debug(f"Course not found: {courseid}")
    return abort(404)


@app.route("/admin/class/<courseid>/edit", methods=["POST"])
@verify_user(allowed_roles=["admin"])
def edit_course_post(user, courseid):
    course = get_course_by_id(courseid)
    if course:
        response = request.json
        course.name = response["name"]
        course.room = response["room"]
        course.canvasid = (
            response["canvasid"] if response["canvasid"].isdigit() else None
        )
        course.lunch = response["lunch"]
        db.session.commit()
        return success_response("Course updated."), 200
    app.logger.debug(f"Course not found: {courseid}")
    return error_response("Course not found."), 404


@app.route("/admin/class/<courseid>/verify", methods=["POST"])
@verify_user(allowed_roles=["admin"])
def verify_course(user, courseid):
    course = get_course_by_id(courseid)
    if course:
        course.verified = True
        db.session.commit()
        app.logger.info(f"Course verified: {courseid}")
        return success_response("Course verified."), 200
    app.logger.debug(f"Course not found: {courseid}")
    return error_response("Course not found."), 404
