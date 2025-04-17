"""
This file contains the functions and data structures for the schedule of the school.
"""

from datetime import date, timedelta, time, datetime
from reportlab.pdfgen import canvas
from app import app
from app.db import Schedule, db, User

# classtime_dict = {daynumber: {
#   "classtimes": [...],
#   "lunchtimes": {}
#}

BELL_DELAY = 5
class period:
    def __init__(self, start: time, end: time, period: str, passing: bool, lunchactive: bool):
        self.start = (datetime.combine(date.today(), start) + timedelta(seconds=BELL_DELAY)).time()
        self.end = (datetime.combine(date.today(), end) + timedelta(seconds=BELL_DELAY)).time()
        self.period = period
        self.passing = passing
        self.lunchactive = lunchactive

classtime_dict = {
    0: { # Monday
        "classtimes": [
            period(time(7, 0), time(7, 30), "1", False, False),
            period(time(7, 30), time(7, 50), "2", True, False),
            period(time(7, 50), time(9, 30), "2", False, False),
            period(time(9, 30), time(9, 35), "4", True, False),
            period(time(9, 35), time(11, 10), "4", False, False),
            period(time(11, 10), time(11, 15), "6", True, False),
            period(time(11, 15), time(13, 15), "6", False, True),
            period(time(13, 15), time(13, 20), "8", True, False),
            period(time(13, 20), time(14, 55), "8", False, False),
        ],
        "lunchtimes": {
            "A": {"start": time(11, 15), "end": time(11, 45)},
            "B": {"start": time(12, 0), "end": time(12, 30)},
            "C": {"start": time(12, 45), "end": time(13, 15)},
        }
    },
    1: { # Tuesday
        "classtimes": [
            period(time(7, 0), time(7, 30), "1", False, False),
            period(time(7, 30), time(7, 50), "3", True, False),
            period(time(7, 50), time(9, 30), "3", False, False),
            period(time(9, 30), time(9, 35), "5", True, False),
            period(time(9, 35), time(11, 10), "5", False, False),
            period(time(11, 10), time(11, 15), "7", True, False),
            period(time(11, 15), time(13, 15), "7", False, True),
            period(time(13, 15), time(13, 20), "9", True, False),
            period(time(13, 20), time(14, 55), "9", False, False),
        ],
        "lunchtimes": {
            "A": {"start": time(11, 15), "end": time(11, 45)},
            "B": {"start": time(12, 0), "end": time(12, 30)},
            "C": {"start": time(12, 45), "end": time(13, 15)},
        }
    },
    2: { # Wednesday
        "classtimes": [
            period(time(7, 0), time(7, 30), "1", False, False),
        period(time(7, 30), time(7, 50), "2", True, False),
            period(time(7, 50), time(9, 5), "2", False, False),
            period(time(9, 5), time(9, 10), "4", True, False),
            period(time(9, 10), time(10, 25), "4", False, False),
            period(time(10, 25), time(10, 30), "Access", True, False),
            period(time(10, 30), time(11, 40), "Access", False, False),
            period(time(11, 40), time(11, 45), "6", True, False),
            period(time(11, 45), time(13, 35), "6", False, True),
            period(time(13, 35), time(13, 40), "8", True, False),
            period(time(13, 40), time(14, 55), "8", False, False),
        ],
        "lunchtimes": {
            "A": {"start": time(11, 45), "end": time(12, 15)},
            "B": {"start": time(12, 25), "end": time(12, 55)},
            "C": {"start": time(13, 5), "end": time(13, 35)},
        }
    },
    3: { # Thursday
        "classtimes": [
            period(time(7, 0), time(7, 30), "1", False, False),
            period(time(7, 30), time(7, 50), "3", True, False),
            period(time(7, 50), time(9, 5), "3", False, False),
            period(time(9, 5), time(9, 10), "5", True, False),
            period(time(9, 10), time(10, 25), "5", False, False),
            period(time(10, 25), time(10, 30), "Access", True, False),
            period(time(10, 30), time(11, 40), "Access", False, False),
            period(time(11, 40), time(11, 45), "7", True, False),
            period(time(11, 45), time(13, 35), "7", False, True),
            period(time(13, 35), time(13, 40), "9", True, False),
            period(time(13, 40), time(14, 55), "9", False, False)
        ],
        "lunchtimes": {
            "A": {"start": time(11, 45), "end": time(12, 15)},
            "B": {"start": time(12, 25), "end": time(12, 55)},
            "C": {"start": time(13, 5), "end": time(13, 35)},
        }
    },
    4: { # Friday
        "classtimes": [
            period(time(7, 0), time(7, 30), "1", False, False),
            period(time(7, 30), time(7, 50), "2", True, False),
            period(time(7, 50), time(8, 35), "2", False, False),
            period(time(8, 35), time(8, 40), "3", True, False),
            period(time(8, 40), time(9, 20), "3", False, False),
            period(time(9, 20), time(9, 25), "4", True, False),
            period(time(9, 25), time(10, 5), "4", False, False),
            period(time(10, 5), time(10, 10), "5", True, False),
            period(time(10, 10), time(10, 50), "5", False, False),
            period(time(10, 50), time(10, 55), "6", True, False),
            period(time(10, 55), time(12, 40), "6", False, True),
            period(time(12, 40), time(12, 45), "7", True, False),
            period(time(12, 45), time(13, 25), "7", False, False),
            period(time(13, 25), time(13, 30), "8", True, False),
            period(time(13, 30), time(14, 10), "8", False, False),
            period(time(14, 10), time(14, 15), "9", True, False),
            period(time(14, 15), time(14, 55), "9", False, False),
        ],
        "lunchtimes": {
            "A": {"start": time(10, 55), "end": time(11, 25)},
            "B": {"start": time(11, 32), "end": time(12, 2)},
            "C": {"start": time(12, 10), "end": time(12, 40)},
        }
    },
    5: { # No school
        "classtimes": [],
        "lunchtimes": {
            "A": {"start": time(0, 0), "end": time(0, 0)},
            "B": {"start": time(0, 0), "end": time(0, 0)},
            "C": {"start": time(0, 0), "end": time(0, 0)},
        }
    },
    6: { # No school
        "classtimes": [],
        "lunchtimes": {
            "A": {"start": time(0, 0), "end": time(0, 0)},
            "B": {"start": time(0, 0), "end": time(0, 0)},
            "C": {"start": time(0, 0), "end": time(0, 0)},
        }
    },
    7: { # Early Release Blue
        "classtimes": [
            period(time(7, 0), time(7, 30), "1", False, False),
            period(time(7, 30), time(7, 50), "2", True, False),
            period(time(7, 50), time(9, 0), "2", False, False),
            period(time(9, 0), time(9, 5), "4", True, False),
            period(time(9, 5), time(10, 5), "4", False, False),
            period(time(10, 5), time(10, 10), "6", True, False),
            period(time(10, 10), time(11, 10), "6", False, True),
            period(time(11, 10), time(11, 15), "8", True, False),
            period(time(11, 15), time(12, 20), "8", False, False),
        ],
        "lunchtimes": {
            "A": {"start": time(0, 0), "end": time(0, 0)},
            "B": {"start": time(0, 0), "end": time(0, 0)},
            "C": {"start": time(0, 0), "end": time(0, 0)},
        }
    },
    8: { # Early Release Gold
        "classtimes": [
            period(time(7, 0), time(7, 30), "1", False, False),
            period(time(7, 30), time(7, 50), "3", True, False),
            period(time(7, 50), time(9, 0), "3", False, False),
            period(time(9, 0), time(9, 5), "5", True, False),
            period(time(9, 5), time(10, 5), "5", False, False),
            period(time(10, 5), time(10, 10), "7", True, False),
            period(time(10, 10), time(11, 10), "7", False, True),
            period(time(11, 10), time(11, 15), "9", True, False),
            period(time(11, 15), time(12, 20), "9", False, False),
        ],
        "lunchtimes": {
            "A": {"start": time(0, 0), "end": time(0, 0)},
            "B": {"start": time(0, 0), "end": time(0, 0)},
            "C": {"start": time(0, 0), "end": time(0, 0)},
        }
    },
}
readable_days = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "No school",
    6: "No school",
    7: "Early Release Blue",
    8: "Early Release Gold",
}


#trey did you see the new comment https://www.youtube.com/watch?v=E_HUrfQqUmA (not a rickroll)


def get_current_day():
    """
    Get the current day of the week, as defined by the schedule.

    Returns:
        int: The simulated day of the week.
    """
    day = datetime.today().date()
    with app.app_context():
        schedule = Schedule.query.filter_by(day=day).first()
    if schedule:
        return schedule.type
    return datetime.today().weekday()

def get_classtimes():
    """
    Get the class times for the current day.

    Returns:
        list: A list of class times.
    """
    return classtime_dict[get_current_day()]['classtimes']

def get_lunchtimes():
    """
    Get the lunch times for the current day.

    Returns:
        dict: A dictionary of lunch
    """
    return classtime_dict[get_current_day()]['lunchtimes']

def set_schedule(start: date, end: date, simulated_day: int):
    """
    Set the schedule for a range of days.

    Args:
        start (date): The start date.
        end (date): The end date.
        simulated_day (int): The type of day to simulate.

    Returns:
        None
    """
    app.logger.info(f"Setting schedule for {start} to {end}")
    schedules = []
    for i in range((end - start).days + 1):
        day = start + timedelta(days=i)
        schedules.append(Schedule(day=day, type=simulated_day))
    app.logger.info(f"Schedules set from {start} to {end} for day type {simulated_day}")
    for schedule in schedules:
        existing_schedule = Schedule.query.filter_by(day=schedule.day).first()
        if existing_schedule:
            db.session.delete(existing_schedule)
        db.session.add(schedule)
    db.session.commit()

def create_schedule_pdf( # pylint: disable=too-many-arguments, too-many-positional-arguments, too-many-locals, too-many-branches, too-many-statements
        user: User=None,
        days: list[int]=None,
        separate: bool=False,
        showperiod: bool=True,
        showclass: bool=True,
        showroom: bool=True,
        showtime: bool=True,
        showlunch: bool=True,
        smalltext: bool=False
    ):
    """
    Create a PDF of the schedule for a user.

    Args:
        user (User): The user to create the schedule for.
        days (list[int]): The days to create the schedule for.
        separate (bool): Whether to separate the days.
        showperiod (bool): Whether to show the period.
        showclass (bool): Whether to show the class.
        showroom (bool): Whether to show the room.
        showtime (bool): Whether to show the time.
        showlunch (bool): Whether to show the lunch.
        smalltext (bool): Whether to use small text.
    """
    if not days:
        days = [get_current_day()]
    file_path = f"/tmp/{user.username if user else 'schedule'}ClassFinderSchedule.pdf"
    c = canvas.Canvas(file_path)
    c.setTitle("School Schedule")
    c.setFont("Helvetica", 20 if not smalltext else 12)
    y = 820 if not smalltext else 818
    app.logger.debug(f"Creating schedule PDF for {user.username if user else 'a guest user'} for days {days}")
    app.logger.debug(f"seperate: {separate}, showclass: {showclass}, showroom: {showroom}, showtime: {showtime}, showlunch: {showlunch}, smalltext: {smalltext}") # pylint: disable=line-too-long
    for day in days:
        y -= 10 if not smalltext else 5
        c.setFont("Helvetica-Bold", 16 if not smalltext else 10)
        c.drawString(50, y, readable_days[day])
        y -= 20 if not smalltext else 10
        c.setFont("Helvetica", 12 if not smalltext else 8)
        classtimes = classtime_dict[day]['classtimes']
        for ctime in classtimes:
            if ctime['passing'] or ctime['period'] == "1":
                continue
            course = None
            if user:
                for ncourse in user.classes:
                    if ncourse.period == ctime['period']:
                        course = ncourse
                        break
            start_time = ctime['start'].strftime("%I:%M %p")
            end_time = ctime['end'].strftime("%I:%M %p")
            drawthings = []
            if showperiod:
                drawthings.append(f"Period {ctime['period'] if ctime['period'] != 'Access' else 'Access'}")
            if showtime:
                drawthings.append(f"{start_time} - {end_time}")
            if showclass and course:
                drawthings.append(course.name)
            if showroom and course:
                drawthings.append(course.room)
            if drawthings:
                c.drawString(50, y, " - ".join(drawthings))
                y -= 15 if not smalltext else 10
            if showlunch and ctime['lunchactive'] and course and course.lunch:
                lunchtime = classtime_dict[day]['lunchtimes'][course.lunch]
                start_time = lunchtime['start'].strftime("%I:%M %p")
                end_time = lunchtime['end'].strftime("%I:%M %p")
                #c.drawString(50, y, f"{course.lunch} lunch" + (f": {start_time} - {end_time}" if showtime else ""))
                drawthings = []
                drawthings.append(f"{course.lunch} lunch")
                if showtime:
                    drawthings.append(f"{start_time} - {end_time}")
                c.drawString(50, y, " - ".join(drawthings))
                y -= 15 if not smalltext else 10
        if separate:
            c.showPage()
            c.setFont("Helvetica", 20 if not smalltext else 12)
            y = 820 if not smalltext else 818
    c.showPage()
    c.save()
    return file_path
