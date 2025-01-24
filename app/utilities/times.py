from app import app
from app.db import Schedule, db, User
from datetime import date, timedelta, time, datetime
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics 
from reportlab.lib import colors 
import random

# classtime_dict = {daynumber: {
#   "classtimes": [...],
#   "lunchtimes": {}
#}
classtime_dict = {
    0: { # Monday
        "classtimes": [
            {
                "start": time(7, 0),
                "end": time(7, 30),
                "period": "1",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(7, 30),
                "end": time(7, 50),
                "period": "2",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(7, 50),
                "end": time(9, 30),
                "period": "2",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(9, 30),
                "end": time(9, 35),
                "period": "4",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(9, 35),
                "end": time(11, 10),
                "period": "4",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(11, 10),
                "end": time(11, 15),
                "period": "6",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(11, 15),
                "end": time(13, 15),
                "period": "6",
                "passing": False,
                "lunchactive": True,
            },
            {
                "start": time(13, 15),
                "end": time(13, 20),
                "period": "8",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(13, 20),
                "end": time(14, 55),
                "period": "8",
                "passing": False,
                "lunchactive": False,
            },
        ],
        "lunchtimes": {
            "A": {"start": time(11, 15), "end": time(11, 45)},
            "B": {"start": time(12, 0), "end": time(12, 30)},
            "C": {"start": time(12, 45), "end": time(13, 15)},
        }
    },
    1: { # Tuesday
        "classtimes": [
            {
                "start": time(7, 0),
                "end": time(7, 30),
                "period": "1",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(7, 30),
                "end": time(7, 50),
                "period": "3",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(7, 50),
                "end": time(9, 30),
                "period": "3",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(9, 30),
                "end": time(9, 35),
                "period": "5",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(9, 35),
                "end": time(11, 10),
                "period": "5",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(11, 10),
                "end": time(11, 15),
                "period": "7",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(11, 15),
                "end": time(13, 15),
                "period": "7",
                "passing": False,
                "lunchactive": True,
            },
            {
                "start": time(13, 15),
                "end": time(13, 20),
                "period": "9",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(13, 20),
                "end": time(14, 55),
                "period": "9",
                "passing": False,
                "lunchactive": False,
            },
        ],
        "lunchtimes": {
            "A": {"start": time(11, 15), "end": time(11, 45)},
            "B": {"start": time(12, 0), "end": time(12, 30)},
            "C": {"start": time(12, 45), "end": time(13, 15)},
        }
    },
    2: { # Wednesday
        "classtimes": [
            {
                "start": time(7, 0),
                "end": time(7, 30),
                "period": "1",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(7, 30),
                "end": time(7, 50),
                "period": "2",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(7, 50),
                "end": time(9, 5),
                "period": "2",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(9, 5),
                "end": time(9, 10),
                "period": "4",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(9, 10),
                "end": time(10, 25),
                "period": "4",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(10, 25),
                "end": time(10, 30),
                "period": "Access",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(10, 30),
                "end": time(11, 40),
                "period": "Access",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(11, 40),
                "end": time(11, 45),
                "period": "6",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(11, 45),
                "end": time(13, 35),
                "period": "6",
                "passing": False,
                "lunchactive": True,
            },
            {
                "start": time(13, 35),
                "end": time(13, 40),
                "period": "8",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(13, 40),
                "end": time(14, 55),
                "period": "8",
                "passing": False,
                "lunchactive": False,
            },
        ],
        "lunchtimes": {
            "A": {"start": time(11, 45), "end": time(12, 15)},
            "B": {"start": time(12, 25), "end": time(12, 55)},
            "C": {"start": time(13, 5), "end": time(13, 35)},
        }
    },
    3: { # Thursday
        "classtimes": [
            {
                "start": time(7, 0),
                "end": time(7, 30),
                "period": "1",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(7, 30),
                "end": time(7, 50),
                "period": "3",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(7, 50),
                "end": time(9, 5),
                "period": "3",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(9, 5),
                "end": time(9, 10),
                "period": "5",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(9, 10),
                "end": time(10, 25),
                "period": "5",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(10, 25),
                "end": time(10, 30),
                "period": "Access",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(10, 30),
                "end": time(11, 40),
                "period": "Access",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(11, 40),
                "end": time(11, 45),
                "period": "7",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(11, 45),
                "end": time(13, 35),
                "period": "7",
                "passing": False,
                "lunchactive": True,
            },
            {
                "start": time(13, 35),
                "end": time(13, 40),
                "period": "9",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(13, 40),
                "end": time(14, 55),
                "period": "9",
                "passing": False,
                "lunchactive": False,
            },
        ],
        "lunchtimes": {
            "A": {"start": time(11, 45), "end": time(12, 15)},
            "B": {"start": time(12, 25), "end": time(12, 55)},
            "C": {"start": time(13, 5), "end": time(13, 35)},
        }
    },
    4: { # Friday
        "classtimes": [
            {
                "start": time(7, 0),
                "end": time(7, 30),
                "period": "1",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(7, 30),
                "end": time(7, 50),
                "period": "2",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(7, 50),
                "end": time(8, 35),
                "period": "2",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(8, 35),
                "end": time(8, 40),
                "period": "3",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(8, 40),
                "end": time(9, 20),
                "period": "3",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(9, 20),
                "end": time(9, 25),
                "period": "4",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(9, 25),
                "end": time(10, 5),
                "period": "4",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(10, 5),
                "end": time(10, 10),
                "period": "5",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(10, 10),
                "end": time(10, 50),
                "period": "5",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(10, 50),
                "end": time(10, 55),
                "period": "6",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(10, 55),
                "end": time(12, 40),
                "period": "6",
                "passing": False,
                "lunchactive": True,
            },
            {
                "start": time(12, 40),
                "end": time(12, 45),
                "period": "7",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(12, 45),
                "end": time(13, 25),
                "period": "7",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(13, 25),
                "end": time(13, 30),
                "period": "8",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(13, 30),
                "end": time(14, 10),
                "period": "8",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(14, 10),
                "end": time(14, 15),
                "period": "9",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(14, 15),
                "end": time(14, 55),
                "period": "9",
                "passing": False,
                "lunchactive": False,
            },
        ],
        "lunchtimes": {
            "A": {"start": time(10, 55), "end": time(11, 25)},
            "B": {"start": time(11, 32), "end": time(12, 2)},
            "C": {"start": time(12, 10), "end": time(12, 40)},
        }
    },
    5: { # No school
        "classtimes": [],
        "lunchtimes": {}
    },
    6: { # No school
        "classtimes": [],
        "lunchtimes": {}
    },
    7: { # Early Release Blue
        "classtimes": [
            {
                "start": time(7, 0),
                "end": time(7, 30),
                "period": "1",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(7, 30),
                "end": time(7, 50),
                "period": "2",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(7, 50),
                "end": time(9, 0),
                "period": "2",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(9, 0),
                "end": time(9, 5),
                "period": "4",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(9, 5),
                "end": time(10, 5),
                "period": "4",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(10, 5),
                "end": time(10, 10),
                "period": "6",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(10, 10),
                "end": time(11, 10),
                "period": "6",
                "passing": False,
                "lunchactive": True,
            },
            {
                "start": time(11, 10),
                "end": time(11, 15),
                "period": "8",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(11, 15),
                "end": time(12, 20),
                "period": "8",
                "passing": False,
                "lunchactive": False,
            },
        ],
        "lunchtimes": {
            "A": {"start": time(0, 0), "end": time(0, 0)},
            "B": {"start": time(0, 0), "end": time(0, 0)},
            "C": {"start": time(0, 0), "end": time(0, 0)},
        }
    },
    8: { # Early Release Gold
        "classtimes": [
            {
                "start": time(7, 0),
                "end": time(7, 30),
                "period": "1",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(7, 30),
                "end": time(7, 50),
                "period": "3",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(7, 50),
                "end": time(9, 0),
                "period": "3",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(9, 0),
                "end": time(9, 5),
                "period": "5",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(9, 5),
                "end": time(10, 5),
                "period": "5",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(10, 5),
                "end": time(10, 10),
                "period": "7",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(10, 10),
                "end": time(11, 10),
                "period": "7",
                "passing": False,
                "lunchactive": True,
            },
            {
                "start": time(11, 10),
                "end": time(11, 15),
                "period": "9",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(11, 15),
                "end": time(12, 20),
                "period": "9",
                "passing": False,
                "lunchactive": False,
            },
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

def get_current_day():
    day = datetime.today().date()
    with app.app_context():
        schedule = Schedule.query.filter_by(day=day).first()
    if schedule:
        return schedule.type
    return datetime.today().weekday()

def get_classtimes():
    return classtime_dict[get_current_day()]['classtimes']

def get_lunchtimes():
    return classtime_dict[get_current_day()]['lunchtimes']

def set_schedule(start: date, end: date, simulated_day: int):
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

def create_schedule_pdf(user: User=None, days: list[int]=None, separate: bool=False, showperiod: bool=True, showclass: bool=True, showroom: bool=True, showtime: bool=True, showlunch: bool=True, smalltext: bool=False):
    if not days:
        days = [get_current_day()]
    file_path = f"/tmp/{user.username if user else 'schedule'}ClassFinderSchedule.pdf"
    c = canvas.Canvas(file_path)
    c.setTitle("School Schedule")
    c.setFont("Helvetica", 20 if not smalltext else 12)
    y = 820 if not smalltext else 818
    app.logger.debug(f"Creating schedule PDF for {user.username if user else 'a guest user'} for days {days}")
    app.logger.debug(f"seperate: {separate}, showclass: {showclass}, showroom: {showroom}, showtime: {showtime}, showlunch: {showlunch}, smalltext: {smalltext}")
    for day in days:
        y -= 10 if not smalltext else 5
        c.setFont("Helvetica-Bold", 16 if not smalltext else 10)
        c.drawString(50, y, readable_days[day])
        y -= 20 if not smalltext else 10
        c.setFont("Helvetica", 12 if not smalltext else 8)
        classtimes = classtime_dict[day]['classtimes']
        for time in classtimes:
            if time['passing'] or time['period'] == "1":
                continue
            course = None
            if user:
                for ncourse in user.classes:
                    if ncourse.period == time['period']:
                        course = ncourse
                        break
            start_time = time['start'].strftime("%I:%M %p")
            end_time = time['end'].strftime("%I:%M %p")
            # c.drawString(50, y, f"{('Period ' + time['period']) if time['period'] != 'Access' else time['period']}: {start_time} - {end_time}" + (f" - {course.name} - {course.room}" if course else ""))
            drawthings = []
            if showperiod: drawthings.append(f"Period {time['period'] if time['period'] != 'Access' else 'Access'}")
            if showtime: drawthings.append(f"{start_time} - {end_time}")
            if showclass and course: drawthings.append(course.name)
            if showroom and course: drawthings.append(course.room)
            if drawthings:
                c.drawString(50, y, " - ".join(drawthings))
                y -= 15 if not smalltext else 10
            if showlunch and time['lunchactive'] and course and course.lunch:
                lunchtime = classtime_dict[day]['lunchtimes'][course.lunch]
                start_time = lunchtime['start'].strftime("%I:%M %p")
                end_time = lunchtime['end'].strftime("%I:%M %p")
                #c.drawString(50, y, f"{course.lunch} lunch" + (f": {start_time} - {end_time}" if showtime else ""))
                drawthings = []
                drawthings.append(f"{course.lunch} lunch")
                if showtime: drawthings.append(f"{start_time} - {end_time}")
                c.drawString(50, y, " - ".join(drawthings))
                y -= 15 if not smalltext else 10
        if separate:
            c.showPage()
            c.setFont("Helvetica", 20 if not smalltext else 12)
            y = 820 if not smalltext else 818
    c.showPage()
    c.save()
    return file_path