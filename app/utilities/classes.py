from app.utilities.times import get_classtimes, get_lunchtimes
from app.db import User, Class, db
from datetime import datetime
from app import app
import typing

neededperiods = ["2", "3", "4", "5", "6", "7", "8", "9", "Access"]


def get_current_period():
    """
    Determine the current period.
    Returns:
        dict: A dictionary containing the current period information, including:
            - "lunchactive" (bool): Whether this periods lunch should be counted for schedule purposes.
            - "period" (str): The current period.
            - "end" (datetime.time): The end time of the current period.
            - "start" (datetime.time): The start time of the current period.
    """
    current_time = datetime.now().time()
    for time in get_classtimes():
        app.logger.debug(f"Checking period {time['period']}")
        if time["start"] <= current_time <= time["end"]:
            app.logger.debug(f"Current period is {time['period']}")
            return time
    app.logger.debug("No current period")
    return None


def get_user_current_period(user: User):
    """
    Determine the user's current period and lunch status.
    Args:
        user (User): The user object containing class information.
    Returns:
        dict: A dictionary containing the current period information, including:
            - "lunch" (str or None): The lunch period if active, otherwise None.
            - "period" (str): The current period.
            - "end" (datetime.time): The end time of the current period.
            - "start" (datetime.time): The start time of the current period.
            - "course" (Course or None): The current course if found, otherwise None.
    Logs:
        Various debug information about the current period, lunch status, and course checking.
    """
    current_time = datetime.now().time()
    current_period = get_current_period()
    app.logger.debug(f"Current period: {current_period}")
    if current_period is None:
        app.logger.debug("No current period")
        return None
    if not current_period["lunchactive"]:
        app.logger.debug("Lunch not active")
        return current_period | {"lunch": None, "course": None}
    currentcourse = None
    for course in user.classes:
        app.logger.debug(f"Checking course {course.name}")
        if course.period == current_period["period"]:
            app.logger.debug(
                f"Found course {course.name} for period {current_period['period']}"
            )
            currentcourse = course
            break
    if currentcourse is None:
        app.logger.debug(
            f"No course found for period {current_period['period']} and user {user.username}"
        )
        return {
            "lunch": None,
            "period": current_period["period"],
            "end": current_period["end"],
            "start": current_period["start"],
            "course": None,
        }
    if get_lunchtimes()[currentcourse.lunch]["start"] <= current_time <= get_lunchtimes()[currentcourse.lunch]["end"]:
        app.logger.debug(f"User {user.username} is in lunch {currentcourse.lunch}")
        return {
            "lunch": currentcourse.lunch,
            "period": "Lunch",
            "end": get_lunchtimes()[currentcourse.lunch]["end"],
            "start": get_lunchtimes()[currentcourse.lunch]["start"],
            "course": currentcourse,
        }
    if current_time < get_lunchtimes()[currentcourse.lunch]["start"]:
        app.logger.debug(
            f"User {user.username} is in period {current_period['period']} for course {currentcourse.name}, before lunch"
        )
        return {
            "lunch": None,
            "period": current_period["period"],
            "end": get_lunchtimes()[currentcourse.lunch]["start"],
            "start": current_period["start"],
            "course": currentcourse,
        }
    app.logger.debug(
        f"User {user.username} is in period {current_period['period']} for course {currentcourse.name}, after lunch"
    )
    return current_period | {"lunch": None, "course": currentcourse}


def get_today_courses(user: User):
    """
    Retrieve the list of courses for the given user that are scheduled for today.

    Args:
        user (User): The user object containing information about the user's classes.

    Returns:
        list: A list of courses that the user has scheduled for today.
    """
    app.logger.debug(f"Retrieving today's courses for user {user.username}")
    user_periods = [time["period"] for time in get_classtimes()]
    app.logger.debug(f"Retrieved user periods: {user_periods}")
    app.logger.debug(f"User {user.username} periods: {user_periods}")
    newcourses = []
    for course in user.classes:
        if course.period in user_periods:
            app.logger.debug(f"Adding course {course.name} for period {course.period}")
            newcourses.append(course)
    app.logger.debug(
        f"User {user.username} courses for today: {[course.name for course in newcourses]}"
    )
    return newcourses


def add_class(name: str, period: int, room: str, created_by: str, commit: bool = True):
    newclass = Class(
        id=f"{room}p{period}",
        name=name,
        room=room,
        period=period,
        created_by=created_by,
    )
    db.session.add(newclass)
    if commit:
        db.session.commit()
    return newclass


def add_user_to_class(user: User, course: Class):
    user.classes.append(course)
    db.session.commit()
    return user


def remove_user_from_class(user: User, course: Class):
    user.classes.remove(course)
    db.session.commit()
    return user


def remove_class(course: Class):
    db.session.delete(course)
    db.session.commit()
    return course


def get_course(period: int, room: str):
    return db.session.query(Class).filter_by(period=period, room=room).first()


def get_course_by_id(id: str):
    return db.session.query(Class).filter_by(id=id).first()


def check_if_class_exists(room: str, period: int):
    return get_course(period=period, room=room) is not None


def check_if_user_in_class(user: User, course: Class):
    return course in user.classes


def get_periods_of_user_classes(user: User):
    return [course.period for course in user.classes]


def set_canvas_id(course: Class, canvasid: int):
    app.logger.debug(f"Setting canvas id for {course.name} to {canvasid}")
    course.canvasid = canvasid
    db.session.commit()
    return course


def set_lunch(course: Class, lunch: typing.Literal["A", "B", "C"]):
    app.logger.debug(f"Setting lunch for {course.name} to {lunch}")
    course.lunch = lunch
    db.session.commit()
    return course
