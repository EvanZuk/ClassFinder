from app import app
from app.db import Schedule, db, Class
from datetime import date, timedelta, time, datetime
from reportlab.pdfgen import canvas 
from reportlab.pdfbase.ttfonts import TTFont 
from reportlab.pdfbase import pdfmetrics 
from reportlab.lib import colors 
import random

classtimes: list = []
day_of_week: int = 0  # Not the actual day of the week, but the preset
lunchtimes: dict = {}
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

get_classtimes = lambda: classtimes
get_lunchtimes = lambda: lunchtimes


def update_times(override: int = None):
    global classtimes, day_of_week, lunchtimes
    if override is not None:
        app.logger.info(f"Overriding day of week to {override}")
        day_of_week = override
    else:
        day = datetime.today().date()
        with app.app_context():
            schedule = Schedule.query.filter_by(day=day).first()
        if schedule:
            app.logger.info(f"Found schedule for {day}: {schedule.type}")
            day_of_week = schedule.type
        else:
            app.logger.debug(f"Updating times for day {day_of_week}")
            day_of_week = datetime.today().weekday()
    classtimes = []
    lunchtimes = {}
    if day_of_week == 0:  # Monday
        classtimes = [
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
        ]
        lunchtimes = {
            "A": {"start": time(11, 15), "end": time(11, 45)},
            "B": {"start": time(12, 0), "end": time(12, 30)},
            "C": {"start": time(12, 45), "end": time(13, 15)},
        }
    elif day_of_week == 1:  # Tuesday
        classtimes = [
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
        ]
        lunchtimes = {
            "A": {"start": time(11, 15), "end": time(11, 45)},
            "B": {"start": time(12, 0), "end": time(12, 30)},
            "C": {"start": time(12, 45), "end": time(13, 15)},
        }
    elif day_of_week == 2:  # Wednesday
        classtimes = [
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
        ]
        lunchtimes = {
            "A": {"start": time(11, 45), "end": time(12, 15)},
            "B": {"start": time(12, 25), "end": time(12, 55)},
            "C": {"start": time(13, 5), "end": time(13, 35)},
        }
    elif day_of_week == 3:  # Thursday
        classtimes = [
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
        ]
        lunchtimes = {
            "A": {"start": time(11, 45), "end": time(12, 15)},
            "B": {"start": time(12, 25), "end": time(12, 55)},
            "C": {"start": time(13, 5), "end": time(13, 35)},
        }
    elif day_of_week == 4:  # Friday
        classtimes = [
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
        ]
        lunchtimes = {
            "A": {"start": time(10, 55), "end": time(11, 25)},
            "B": {"start": time(11, 32), "end": time(12, 2)},
            "C": {"start": time(12, 10), "end": time(12, 40)},
        }
    elif day_of_week == 7:  # Early Release Blue
        classtimes = [
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
                "end": time(8, 45),
                "period": "2",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(8, 45),
                "end": time(8, 50),
                "period": "4",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(8, 50),
                "end": time(9, 40),
                "period": "4",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(9, 40),
                "end": time(9, 45),
                "period": "6",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(9, 45),
                "end": time(11, 25),
                "period": "6",
                "passing": False,
                "lunchactive": True,
            },
            {
                "start": time(11, 25),
                "end": time(11, 30),
                "period": "8",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(11, 30),
                "end": time(12, 20),
                "period": "8",
                "passing": False,
                "lunchactive": False,
            },
        ]
        lunchtimes = {
            "A": {"start": time(9, 45), "end": time(10, 15)},
            "B": {"start": time(10, 20), "end": time(10, 50)},
            "C": {"start": time(10, 55), "end": time(11, 25)},
        }
    elif day_of_week == 8:  # Early Release Gold
        classtimes = [
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
                "end": time(8, 45),
                "period": "3",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(8, 45),
                "end": time(8, 50),
                "period": "5",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(8, 50),
                "end": time(9, 40),
                "period": "5",
                "passing": False,
                "lunchactive": False,
            },
            {
                "start": time(9, 40),
                "end": time(9, 45),
                "period": "7",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(9, 45),
                "end": time(11, 25),
                "period": "7",
                "passing": False,
                "lunchactive": True,
            },
            {
                "start": time(11, 25),
                "end": time(11, 30),
                "period": "9",
                "passing": True,
                "lunchactive": False,
            },
            {
                "start": time(11, 30),
                "end": time(12, 20),
                "period": "9",
                "passing": False,
                "lunchactive": False,
            },
        ]
        lunchtimes = {
            "A": {"start": time(9, 45), "end": time(10, 15)},
            "B": {"start": time(10, 20), "end": time(10, 50)},
            "C": {"start": time(10, 55), "end": time(11, 25)},
        }
    app.logger.debug(f"Updated times for day {day_of_week}")
    db.session.commit()
    app.logger.debug("Updated class times")


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
    update_times()

def create_time_pdf():
    global classtimes
    times = classtimes
    pdfpath = f"/tmp/ClassFinderSchedule{random.randint(0, 1000000)}.pdf"
    c = canvas.Canvas(pdfpath)
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, f"Schedule - {datetime.today().strftime('%m/%d/%y')} - {readable_days[day_of_week]}")
    y = 750
    for time in times:
        if time['passing'] or time['period'] == '1':
            continue
        start_time = time['start'].strftime('%I:%M %p')
        end_time = time['end'].strftime('%I:%M %p')
        c.drawString(100, y, f"Period {time['period']} - {start_time} to {end_time}")
        y -= 20
    c.save()
    return pdfpath

def create_personal_time_pdf(user):
    global classtimes
    times = classtimes
    pdfpath = f"/tmp/ClassFinderSchedulePersonal{random.randint(0, 1000000)}.pdf"
    c = canvas.Canvas(pdfpath)
    c.setFont("Helvetica", 12)
    c.drawString(100, 800, f"{user.username}'s Schedule - {datetime.today().strftime('%m/%d/%y')} - {readable_days[day_of_week]}")
    y = 750
    for time in times:
        if time['passing'] or time['period'] == '1':
            continue
        course = None
        for class_ in user.classes:
            if class_.period == time['period']:
                course = class_
                break
        start_time = time['start'].strftime('%I:%M %p')
        end_time = time['end'].strftime('%I:%M %p')
        c.drawString(100, y, f"Period {time['period']} - {start_time} to {end_time}" + (f" - {course.name}" if course else ""))
        y -= 20
    c.save()
    return pdfpath