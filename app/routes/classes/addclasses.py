from flask import render_template, redirect, request, send_from_directory, Response
from app import app
from app.utilities.other import split_list
from app.utilities.users import verify_user
from app.utilities.classes import (
    add_class,
    add_user_to_class,
    check_if_class_exists,
    get_course,
    check_if_user_in_class,
    get_periods_of_user_classes,
    neededperiods,
)
from app.db import db
from app.utilities.validation import validate_room
from app.utilities.responses import error_response, success_response
import better_profanity
import asyncio

@app.route("/addclasses")
@verify_user
def addclasses(user):
    if len(get_periods_of_user_classes(user)) == len(neededperiods):
        app.logger.debug(
            f"User already has all of their classes. ({len(get_periods_of_user_classes(user))}/{len(neededperiods)})"
        )
        return redirect("/")
    return render_template(
        "addcourses.html",
        neededperiods=[
            period
            for period in neededperiods
            if period not in get_periods_of_user_classes(user)
        ],
    )


@app.route("/addclasses", methods=["POST"])
@verify_user(
    onfail=lambda:({"status": "error", "message": "You must be logged in to do that."}, 401)
)
def addclasses_post(user):
    if len(get_periods_of_user_classes(user)) == len(neededperiods):
        return error_response("You already have all of your classes."), 400
    if len(request.json) % 5 != 0:
        return (
            error_response(
                "Make sure you copied your classes from infinite campus, and that you have copied everything."
            ),
            400,
        )
    classes = split_list(request.json, 5)
    for course in classes:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        tasks = [process_course(course, user) for course in classes]
        results = loop.run_until_complete(asyncio.gather(*tasks))
        for result in results:
            if result is not None:
                return result
        loop.close()
        db.session.commit()
    for course in classes:
        newcourse = {
            "period": course[0].strip(),
            "room": course[4].strip().replace("Room: ", ""),
        }
        newclass = get_course(newcourse["period"], newcourse["room"])
        if newcourse["period"] in get_periods_of_user_classes(user):
            continue
        if not check_if_user_in_class(user, newclass):
            add_user_to_class(user, newclass)
    return success_response("Classes added successfully."), 200

async def process_course(course, user):
    app.logger.debug(f"Processing course: {course}")
    newcourse = {
        "period": course[0].strip(),
        "name": course[1].removeprefix("MS ").strip(),
        "room": course[4].replace("Room: ", "").strip(),
    }
    if newcourse["period"] not in neededperiods:
        app.logger.debug(f"Invalid period: {newcourse['period']}")
        return error_response("Invalid period for a course."), 400
    if newcourse["period"] in get_periods_of_user_classes(user):
        app.logger.debug(
            f"User already has a class in period {newcourse['period']}"
        )
        return None
    if not validate_room(newcourse["room"]):
        app.logger.debug(f"Invalid room number: {newcourse['room']}")
        return error_response("Invalid room number for a course."), 400
    if better_profanity.profanity.contains_profanity(newcourse["name"]):
        app.logger.debug(f"Course name with profanity: {newcourse['name']}")
        return error_response("Invalid course name."), 400
    if check_if_class_exists(newcourse["room"], newcourse["period"]):
        return None
    createdclass = add_class(
        newcourse["name"],
        newcourse["period"],
        newcourse["room"],
        created_by=user.username,
        commit=False,
    )
    if not check_if_user_in_class(user, createdclass):
        add_user_to_class(user, createdclass)
    return None

@app.route("/addclasses/help.gif")
def addclasses_help():
    return send_from_directory("static", "addclasses.gif")
