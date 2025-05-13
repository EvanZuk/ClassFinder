"""
Allows exporting classes to a icalendar file for use in google calendar
"""
from datetime import date, timedelta, datetime
import pytz
from ics import Calendar, Event
from flask import request, send_file
from app import app
from app.utilities.config import canvas_url
from app.utilities.users import verify_user
from app.utilities.times import get_current_day, get_classtime_by_period, readable_days
from app.utilities.classes import get_today_courses

GEN_CAL_LENGTH = 91  # Number of days to generate calendar for

@app.route('/<authtoken>/calendar.ics')
@verify_user(required_scopes=[['read-classes']])
def calendar_req(authtoken): # pylint: disable=unused-argument
    """Generate a calendar file for the current and next 90 days."""
    start_datetime = datetime.now()
    app.logger.info(f"Generating calendar for {request.user.username}")

    cal = Calendar()
    cal.name = f"{request.user.username}'s Calendar"

    # Generate events
    generate_events_for_date_range(cal, GEN_CAL_LENGTH)
    add_end_of_calendar_event(cal)

    # Export the calendar
    calendar_path = f"/tmp/{request.user.username}_calendar.ics"
    with open(calendar_path, "w", encoding="UTF-8") as f:
        f.write(cal.serialize())

    app.logger.debug(f"Calendar generated in {datetime.now() - start_datetime}")
    return send_file(calendar_path, as_attachment=True, download_name="calendar.ics", mimetype="text/calendar")


def generate_events_for_date_range(calendar, days):
    """Generate calendar events for a specified number of days."""
    for i in range(0, days):
        current_date = date.today() + timedelta(days=i)
        app.logger.debug(f"Generating calendar for {current_date}")
        generate_events_for_date(calendar, current_date)


def generate_events_for_date(calendar, current_date):
    """Generate calendar events for a specific date."""
    current_day = get_current_day(current_date)
    app.logger.debug(f"Current day is {current_day}")

    classes = get_today_courses(request.user, current_day)

    if not classes:
        handle_no_classes_day(calendar, current_date)
        return

    # Add day type event
    add_day_type_event(calendar, current_date, current_day)

    # Add events for each class
    for course in classes:
        add_class_event(calendar, course, current_date, current_day)

        if "passing" in request.args:
            add_passing_period_event(calendar, course, current_date, current_day)


def handle_no_classes_day(calendar, current_date):
    """Handle days with no classes."""
    # Skip weekends
    if current_date.weekday() == 5 or current_date.weekday() == 6:
        app.logger.debug(f"Weekend on {current_date}")
        return

    app.logger.debug(f"No classes for {current_date}")
    event = Event()
    event.name = "No school"
    event.begin = datetime.combine(current_date, datetime.min.time())
    event.make_all_day()
    event.description = "No school today"
    calendar.events.add(event)


def add_day_type_event(calendar, current_date, current_day):
    """Add an all-day event indicating the schedule type."""
    event = Event()
    event.name = readable_days[current_day]
    event.begin = datetime.combine(current_date, datetime.min.time())
    event.make_all_day()
    event.description = f"School is a {readable_days[current_day]} schedule today."
    calendar.events.add(event)


def add_class_event(calendar, course, current_date, current_day):
    """Add a class event to the calendar."""
    classtime = get_classtime_by_period(period=course.period, passing=False, day=current_day)
    denver_tz = pytz.timezone('America/Denver')
    start_time = denver_tz.localize(datetime.combine(current_date, classtime['start']))
    end_time = denver_tz.localize(datetime.combine(current_date, classtime['end']))

    event = Event()
    event.name = course.name
    event.begin = start_time
    event.end = end_time
    event.description = f"In room {course.room}"
    event.location = course.room

    if course.canvasid:
        event.url = f"{canvas_url}/courses/{course.canvasid}"

    calendar.events.add(event)


def add_passing_period_event(calendar, course, current_date, current_day):
    """Add a passing period event to the calendar."""
    passing_classtime = get_classtime_by_period(period=course.period, passing=True, day=current_day)
    denver_tz = pytz.timezone('America/Denver')
    start_time = denver_tz.localize(datetime.combine(current_date, passing_classtime['start']))
    end_time = denver_tz.localize(datetime.combine(current_date, passing_classtime['end']))

    event = Event()
    event.name = "Passing period"
    event.begin = start_time
    event.end = end_time
    event.description = f"Passing period for {course.name} in room {course.room}"
    event.location = course.room

    calendar.events.add(event)


def add_end_of_calendar_event(calendar):
    """Add an event marking the end of the calendar."""
    final_date = date.today() + timedelta(days=GEN_CAL_LENGTH)
    event = Event()
    event.name = "End of calendar"
    event.begin = datetime.combine(final_date, datetime.min.time())
    event.make_all_day()
    event.description = "End of generated calendar"
    calendar.events.add(event)
