"""
Admin routes for managing courses.
"""
import shutil
import datetime
from flask import render_template, abort, request
from app import app
from app.utilities.users import verify_user
from app.utilities.classes import get_course_by_id, remove_class, get_all_courses
from app.utilities.responses import success_response, error_response
from app.db import db

@app.route("/admin/class/<courseid>", methods=["DELETE"])
@verify_user(allowed_roles=["admin"])
def delete_course(courseid):
    """
    Deletes a course.
    """
    course = get_course_by_id(courseid)
    if course:
        remove_class(course)
        return success_response("Course deleted."), 200
    return error_response("Course not found."), 404

@app.route("/admin/class/<courseid>/edit")
@verify_user(allowed_roles=["admin"])
def edit_course(courseid):
    """
    Displays the edit course page.
    """
    course = get_course_by_id(courseid)
    if course:
        return render_template("editcourse.html", course=course)
    app.logger.debug(f"Course not found: {courseid}")
    return abort(404)

@app.route("/admin/class/<courseid>/edit", methods=["POST"])
@verify_user(allowed_roles=["admin"])
def edit_course_post(courseid):
    """
    Handles the edit course form submission.
    """
    course = get_course_by_id(courseid)
    if course:
        response = request.json
        course.name = response["name"]
        course.room = response["room"]
        course.canvasid = (
            response["canvasid"] if response["canvasid"].isdigit() else None
        )
        course.lunch = (
            response["lunch"] if response["lunch"] != "" else None
        )
        course.verified = True
        db.session.commit()
        return success_response("Course updated."), 200
    app.logger.debug(f"Course not found: {courseid}")
    return error_response("Course not found."), 404


@app.route("/admin/class/<courseid>/verify", methods=["POST"])
@verify_user(allowed_roles=["admin"])
def verify_course(courseid):
    """
    Verifies a course.
    """
    course = get_course_by_id(courseid)
    if course:
        course.verified = True
        db.session.commit()
        app.logger.info(f"Course verified: {courseid}")
        return success_response("Course verified."), 200
    app.logger.debug(f"Course not found: {courseid}")
    return error_response("Course not found."), 404

@app.route("/admin/class/all", methods=["DELETE"])
@verify_user(allowed_roles=["admin"])
def delete_all_courses():
    """
    Deletes all courses.
    """
    app.logger.warning("Deleting all courses, requested by " + request.user.username)
    dbfile = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///","")
    newfile = dbfile.replace(".",f"_backup_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.")
    app.logger.info(f"Copying database to {newfile}")
    shutil.copy(dbfile, newfile)
    for course in get_all_courses():
        if "Access" in course.name:
            app.logger.debug(f"Skipping course: {course.name}")
            continue
        app.logger.info(f"Deleting course: {course.name}")
        remove_class(course)
    return success_response("All courses deleted."), 200
