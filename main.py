import os
import re
import platform
import functools
from flask import Flask, render_template, request, redirect, url_for, jsonify
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from flask_limiter import Limiter
from better_profanity import profanity
import smtplib
import datetime
from waitress import serve
from sqlalchemy.sql import func

app = Flask(__name__, static_folder='static', template_folder='templates')

limiter = Limiter(app, default_limits=["75/minute", "5/second"])
scheduler = APScheduler()

app.secret_key = os.environ.get("APP_KEY", "HOUFSyf938oJjg893y)(S*_)").encode('utf-8')
emailconfig = {
    'host': os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
    'port': os.environ.get('EMAIL_PORT', 587),
    'username': os.environ.get('EMAIL_USERNAME'),
    'password': os.environ.get('EMAIL_PASSWORD'),
    'from': os.environ.get('EMAIL_FROM', "classfinder@trey7658.com")
}
emailids = {}
linkcodes={}
bcrypt = Bcrypt(app)
debugmode = platform.node() != 'classfinder'
app.logger.setLevel('DEBUG' if debugmode else 'INFO')
classtimes=[]
day_of_week=0
lunchtimes=[]
@app.cli.command('reset_db')
def reset_db():
    db.drop_all()
    db.create_all()
    if User.query.count() == 0:
        useractions.create_user(username='admin', password='admin', email='admin@example.com', created_by='system', role='admin')
        app.logger.info("Created admin user with username 'admin' and password 'admin'")
class User(db.Model):
    username = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    created_by = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(50), nullable=False)
    courses = db.relationship('Course', secondary='user_courses', back_populates='users')
    tokens = db.relationship('Token', backref='user')

class Course(db.Model):
    id = db.Column(db.String(20), primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    room = db.Column(db.String(10), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    canvasid = db.Column(db.Integer, nullable=True)
    lunch = db.Column(db.String(1), nullable=True, default=False)
    users = db.relationship('User', secondary='user_courses', back_populates='courses')

class Schedule(db.Model):
    day = db.Column(db.Integer, nullable=False, primary_key=True, unique=True)
    type = db.Column(db.String(50), nullable=False)

user_courses = db.Table('user_courses',
    db.Column('user_username', db.String(80), db.ForeignKey('user.username'), primary_key=True),
    db.Column('course_id', db.String(20), db.ForeignKey('course.id'), primary_key=True)
)

class Token(db.Model):
    token = db.Column(db.String(200), primary_key=True, unique=True, nullable=False)
    username = db.Column(db.String(80), db.ForeignKey('user.username'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    expiry = db.Column(db.DateTime(timezone=True), nullable=False)

user_tokens = db.Table('user_tokens',
    db.Column('user_username', db.String(80), db.ForeignKey('user.username'), primary_key=True),
    db.Column('token', db.String(200), db.ForeignKey('token.token'), primary_key=True)
)

class useractions():
    def generate_token(username, type='session'):
        token = os.urandom(32).hex()
        new_token = Token(token=token, username=username, type=type, expiry=datetime.datetime.now() + datetime.timedelta(days=7))
        db.session.add(new_token)
        db.session.commit()
        return token
    
    def verify_token(token):
        token = Token.query.filter_by(token=token).first()
        if token is None:
            return None
        if token.expiry < datetime.datetime.now():
            db.session.delete(token)
            db.session.commit()
            return None
        return token.username, token.type
    
    def create_user(username, email, password, created_by: str='self', role: str='user'):
        new_user = User(username=username, email=email, password=bcrypt.generate_password_hash(app.secret_key.decode() + password), created_by=created_by, role='user')
        db.session.add(new_user)
        db.session.commit()
        return new_user
    
    def verify_email(email):
        if not re.match(r'[a-z]*\.[a-z]*(@s.stemk12.org|@stemk12.org)', email):
            return False
        return True
    
    class email():
        def create_emailid(email):
            emailid = os.urandom(32).hex()
            emailids[emailid] = email
            return emailid
        
        def send_verify_email(email):
            emailid = useractions.email.create_emailid(email)
            message = f"Click the link to verify your email: {url_for('register_verify', emailid=emailid, _external=True)}"
            send_email(email, "Verify your email", message)

def require_login(func=None, required: bool=True, onfail=None, allowed_roles: list=['user']):
    if func is None:
        return lambda f: require_login(f, required, onfail, allowed_roles)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if onfail is None:
            whenfail = redirect(url_for('login', redirect=request.path))

        token = request.cookies.get('token') # Authenticate using cookie
        user = None
        if token:
            username = useractions.verify_token(token)
            if username:
                user = User.query.filter_by(username=username[0]).first()
            if user and user.role in allowed_roles:
                return func(user.username, *args, **kwargs)
        
        auth = request.authorization # Authenticate using basic authentication
        if auth:
            user = User.query.filter_by(username=auth.username).first()
            if user and user.password == auth.password and user.role in allowed_roles:
                return func(user.username, *args, **kwargs)
        
        bearer_token = request.headers.get('Authorization') # Authenticate using bearer token for api requests
        if bearer_token and bearer_token.startswith('Bearer '):
            token = bearer_token.split(' ')[1]
            username = useractions.verify_token(token)
            if username:
                user = User.query.filter_by(username=username).first()
            if user and user.role in allowed_roles:
                return func(user.username, *args, **kwargs)
        
        return (whenfail if required else func(None, *args, **kwargs))
    return wrapper

def send_email(email, subject, message):
    if debugmode:
        app.logger.info(f"Email to {email} with subject '{subject}' and message '{message}'")
        return
    if emailconfig['username'] is None or emailconfig['password'] is None:
        app.logger.error("Email not configured, cannot send email")
        return
    msg = MIMEMultipart()
    msg['From'] = emailconfig['from']
    msg['To'] = email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP(emailconfig['host'], emailconfig['port'])
    server.starttls()
    server.login(emailconfig['username'], emailconfig['password'])
    server.sendmail(emailconfig['from'], email, msg.as_string())
    server.quit()

class static():
    @app.route('/favicon.ico')
    def favicon():
        return app.send_static_file('favicon.ico' if not debugmode else 'favicondev.ico')
    
    @app.route('/robots.txt')
    def robots():
        return "User-agent: *\nDisallow: /"
    
    @app.route('/index.css')
    def index_css():
        return app.send_static_file('index.css')

class authentication():
    @app.route('/login', methods=['GET'])
    @require_login(required=False)
    def login(username):
        return render_template('login.html') if username is None else redirect(url_for('dashboard'))

    @app.route('/login', methods=['POST'])
    def login_post():
        json = request.json
        user = User.query.filter_by(username=json['username']).first()
        if user is None:
            return {'status': 'error', 'message': 'User not found'}
        if not bcrypt.check_password_hash(user.password, app.secret_key.decode() + json['password']):
            return {'status': 'error', 'message': 'Incorrect password'}
        response = jsonify({'status': 'success', 'message': 'Logged in'})
        response.set_cookie('token', useractions.generate_token(user.username))
        return response

    @app.route('/register', methods=['GET'])
    @require_login(required=False)
    def register(username):
        return render_template('register.html') if username is None else redirect(url_for('dashboard'))

    @app.route('/register', methods=['POST'])
    def register_post():
        json = request.json
        if not useractions.verify_email(json['email']):
            return {'status': 'error', 'message': 'Invalid email'}
        if User.query.filter_by(email=json['email']).first() is not None:
            return {'status': 'error', 'message': 'Email already registered'}
        useractions.email.send_verify_email(json['email'])
        return {'status': 'success', 'message': 'Email sent for verification'}

    @app.route('/register/<emailid>', methods=['GET'])
    def register_verify(emailid):
        email = emailids.get(emailid)
        if email is None:
            return redirect(url_for('register'))
        return render_template('register_final.html', email=email)

    @app.route('/register/<emailid>', methods=['POST'])
    def register_verify_post(emailid):
        email = emailids.get(emailid)
        json = request.json
        if email is None:
            return {'status': 'error', 'message': 'Invalid emailid'}
        if User.query.filter_by(email=email).first() is not None:
            return {'status': 'error', 'message': 'Email already registered'}
        if not re.fullmatch(r'([A-z]|[0-9]){3,15}', json['username']):
            return {'status': 'error', 'message': 'Invalid username, it must be within 3-15 characters and only contain letters and numbers'}
        user = useractions.create_user(json['username'], email, json['password'])
        response = jsonify({'status': 'success', 'message': 'User created'})
        response.set_cookie('token', useractions.generate_token(user.username))
        return response

class errorhandling():
    @app.errorhandler(404)
    def not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(401)
    def internal_error(e):
        return render_template('401.html'), 401

class courses():
    def get_current_period():
        current_time = datetime.datetime.now().time()
        for classtime in classtimes:
            if classtime['start'] <= current_time <= classtime['end']:
                return classtime
        return None

    def get_user_current_period(username):
        current_period = courses.get_current_period()
        current_time = datetime.datetime.now().time()
        if current_period is None:
            return None
        currentcourse = courses.get_current_user_course(username)
        if currentcourse is None:
            return None
        if currentcourse.lunch and current_period['lunch']:
            if lunchtimes[currentcourse.lunch]['start'] <= current_time <= lunchtimes[currentcourse.lunch]['end']:
                return {'period': 'Lunch', 'start': lunchtimes[currentcourse.lunch]['start'], 'end': lunchtimes[currentcourse.lunch]['end'], 'lunch': True, 'passing': False}
        return current_period
    
    def get_current_user_course(username):
        current_period = courses.get_current_period()
        if current_period is None:
            return
        user = User.query.filter_by(username=username).first()
        if user is None:
            return None
        for course in user.courses:
            if course.period == current_period['period']:
                return course
        return None
        

@app.route('/')
@require_login(required=False)
def home(username):
    if username is not None:
        return redirect(url_for('dashboard'))
    return render_template('index.html', username=username)

@app.route('/dashboard')
@require_login
def dashboard(username):
    user = User.query.filter_by(username=username).first()
    return render_template('dashboard.html', username=username, classes=user.courses)

@app.route('/account')
@require_login
def account(username):
    user = User.query.filter_by(username=username).first()
    return render_template('account.html', username=username, courses=user.courses)

@app.route('/addcourses')
@require_login
def addcourses(username):
    return render_template('addcourses.html', username=username)

@app.route('/addcourses', methods=['POST'])
@require_login
def addcourses_post(username):
    json = request.json
    newcourses = [json[i:i + 5] for i in range(0, len(json), 5)]
    tobeadded = []
    for course in newcourses:
        newcourse = {}
        newcourse['period'] = course[0]
        newcourse['name'] = course[1]
        newcourse['room'] = course[4].replace(':', '').replace('Room', '').replace(" ", "").strip()
        if newcourse['period'] == "Access":
            newcourse['period'] = "access"
        else:
            try:
                newcourse['period'] = int(newcourse['period'])
                if newcourse['period'] < 2 or newcourse['period'] > 9:
                    continue
            except ValueError:
                continue
        if re.fullmatch(r'E?[0-9]{3}', newcourse['room']) is None:
            continue
        if profanity.contains_profanity(newcourse['name']):
            continue
        tobeadded.append(newcourse)
    with db.session.no_autoflush:
        for course in tobeadded:
            course_id = course['room'] + "p" + str(course['period'])
            existing_course = Course.query.filter_by(id=course_id).first()
            if not existing_course:
                new_course = Course(id=course_id, name=course['name'], room=course['room'], period=course['period'])
                db.session.add(new_course)
        for course in tobeadded:
            existing_course = Course.query.filter_by(id=course['room']+ "p" + str(course['period'])).first()
            if existing_course:
                user = User.query.filter_by(username=username).first()
                if existing_course not in user.courses:
                    user.courses.append(existing_course)
    db.session.commit()
    return {'status': 'success', 'message': 'Courses added'}

@scheduler.task('cron', id='update_schedule', hour=2)
def update_schedule(override: int=None):
    global day_of_week
    global classtimes
    global lunchtimes
    if override:
        day_of_week = override
    else:
        current_day = (datetime.datetime.today() - datetime.datetime(2024, 1, 1)).days
        schedule = Schedule.query.filter_by(day=current_day).first()
        if schedule:
            day_of_week = schedule.day
        else:
            day_of_week = datetime.datetime.today().weekday()
    classtimes = []
    lunchtimes = []
    # Classtimes is in the format:
    # [{start: 8:00, end: 8:45, period: 1, lunch: false, passing: false}, ...]
    # The period can be an integer or a string, if it is a string it is a special period (such as access). Intermission does not count as a special period and is instead labeled as period 1
    # Passing is the time between classes, lunch is weather or not the periods dedicated "lunch" period should be active
    # Lunch is not included in the classtimes list, it is handled separately in lunchtimes which follows the format:
    # {"A": {start: 11:00, end: 11:30}, "B": {start: 11:30, end: 12:00}, ...}
    # The lunchtimes list is only used when the lunch period is active
    # The lunch period is active if the current time is between the start and end times of the lunch period AND the current period is the lunch period
    if day_of_week == 0: # Monday
        classtimes = [
            {"start": "07:00", "end": "07:30", "period": 1, "lunch": False, "passing": False},
            {"start": "07:30", "end": "07:50", "period": 2, "lunch": False, "passing": True},
            {"start": "07:50", "end": "09:30", "period": 2, "lunch": False, "passing": False},
            {"start": "09:30", "end": "09:35", "period": 4, "lunch": False, "passing": True},
            {"start": "09:35", "end": "11:10", "period": 4, "lunch": False, "passing": False},
            {"start": "11:10", "end": "11:15", "period": 6, "lunch": False, "passing": True},
            {"start": "11:15", "end": "13:15", "period": 6, "lunch": True, "passing": False},
            {"start": "13:15", "end": "13:20", "period": 8, "lunch": False, "passing": True},
            {"start": "13:20", "end": "14:55", "period": 8, "lunch": False, "passing": False},
        ]
        lunchtimes = {
            "A": {"start": "11:15", "end": "11:45"},
            "B": {"start": "12:00", "end": "12:30"},
            "C": {"start": "12:45", "end": "13:15"},
        }
    elif day_of_week == 1: # Tuesday
        classtimes = [
            {"start": "07:00", "end": "07:30", "period": 1, "lunch": False, "passing": False},
            {"start": "07:30", "end": "07:50", "period": 3, "lunch": False, "passing": True},
            {"start": "07:50", "end": "09:30", "period": 3, "lunch": False, "passing": False},
            {"start": "09:30", "end": "09:35", "period": 5, "lunch": False, "passing": True},
            {"start": "09:35", "end": "11:10", "period": 5, "lunch": False, "passing": False},
            {"start": "11:10", "end": "11:15", "period": 7, "lunch": False, "passing": True},
            {"start": "11:15", "end": "13:15", "period": 7, "lunch": True, "passing": False},
            {"start": "13:15", "end": "13:20", "period": 9, "lunch": False, "passing": True},
            {"start": "13:20", "end": "14:55", "period": 9, "lunch": False, "passing": False},
        ]
        lunchtimes = {
            "A": {"start": "11:15", "end": "11:45"},
            "B": {"start": "12:00", "end": "12:30"},
            "C": {"start": "12:45", "end": "13:15"},
        }
    elif day_of_week == 2: # Wednesday
        classtimes = [
            {"start": "07:00", "end": "07:30", "period": 1, "lunch": False, "passing": False},
            {"start": "07:30", "end": "07:50", "period": 2, "lunch": False, "passing": True},
            {"start": "07:50", "end": "09:05", "period": 2, "lunch": False, "passing": False},
            {"start": "09:05", "end": "09:10", "period": 4, "lunch": False, "passing": True},
            {"start": "09:10", "end": "10:25", "period": 4, "lunch": False, "passing": False},
            {"start": "10:25", "end": "10:30", "period": 'access', "lunch": False, "passing": True},
            {"start": "10:30", "end": "11:40", "period": 'access', "lunch": False, "passing": False},
            {"start": "11:40", "end": "11:45", "period": 6, "lunch": False, "passing": True},
            {"start": "11:45", "end": "13:35", "period": 6, "lunch": True, "passing": False},
            {"start": "13:35", "end": "13:40", "period": 8, "lunch": False, "passing": True},
            {"start": "13:40", "end": "14:55", "period": 8, "lunch": False, "passing": False},
        ]
        lunchtimes = {
            "A": {"start": "11:45", "end": "12:15"},
            "B": {"start": "12:25", "end": "12:55"},
            "C": {"start": "13:05", "end": "13:35"},
        }
    elif day_of_week == 3: # Thursday
        classtimes = [
            {"start": "07:00", "end": "07:30", "period": 1, "lunch": False, "passing": False},
            {"start": "07:30", "end": "07:50", "period": 3, "lunch": False, "passing": True},
            {"start": "07:50", "end": "09:05", "period": 3, "lunch": False, "passing": False},
            {"start": "09:05", "end": "09:10", "period": 5, "lunch": False, "passing": True},
            {"start": "09:10", "end": "10:25", "period": 5, "lunch": False, "passing": False},
            {"start": "10:25", "end": "10:30", "period": 'access', "lunch": False, "passing": True},
            {"start": "10:30", "end": "11:40", "period": 'access', "lunch": False, "passing": False},
            {"start": "11:40", "end": "11:45", "period": 7, "lunch": False, "passing": True},
            {"start": "11:45", "end": "13:35", "period": 7, "lunch": True, "passing": False},
            {"start": "13:35", "end": "13:40", "period": 9, "lunch": False, "passing": True},
            {"start": "13:40", "end": "14:55", "period": 9, "lunch": False, "passing": False},
        ]
        lunchtimes = {
            "A": {"start": "11:45", "end": "12:15"},
            "B": {"start": "12:25", "end": "12:55"},
            "C": {"start": "13:05", "end": "13:35"},
        }
    elif day_of_week == 4: # Friday
        classtimes = [
            {"start": "07:00", "end": "07:30", "period": 1, "lunch": False, "passing": False},
            {"start": "07:30", "end": "07:50", "period": 2, "lunch": False, "passing": True},
            {"start": "07:50", "end": "08:35", "period": 2, "lunch": False, "passing": False},
            {"start": "08:35", "end": "08:40", "period": 3, "lunch": False, "passing": True},
            {"start": "08:40", "end": "09:20", "period": 3, "lunch": False, "passing": False},
            {"start": "09:20", "end": "09:25", "period": 4, "lunch": False, "passing": True},
            {"start": "09:25", "end": "10:05", "period": 4, "lunch": False, "passing": False},
            {"start": "10:05", "end": "10:10", "period": 5, "lunch": False, "passing": True},
            {"start": "10:10", "end": "10:50", "period": 5, "lunch": False, "passing": False},
            {"start": "10:50", "end": "10:55", "period": 6, "lunch": False, "passing": True},
            {"start": "10:55", "end": "12:40", "period": 6, "lunch": True, "passing": False},
            {"start": "12:40", "end": "12:45", "period": 7, "lunch": False, "passing": True},
            {"start": "12:45", "end": "13:25", "period": 7, "lunch": False, "passing": False},
            {"start": "13:25", "end": "13:30", "period": 8, "lunch": False, "passing": True},
            {"start": "13:30", "end": "14:10", "period": 8, "lunch": False, "passing": False},
            {"start": "14:10", "end": "14:15", "period": 9, "lunch": False, "passing": True},
            {"start": "14:15", "end": "14:55", "period": 9, "lunch": False, "passing": False},
        ]
        lunchtimes = {
            "A": {"start": "10:55", "end": "11:25"},
            "B": {"start": "11:32", "end": "12:02"},
            "C": {"start": "12:10", "end": "12:40"},
        }
    elif day_of_week == 7: # Early release blue
        classtimes = [
            {"start": "07:00", "end": "07:30", "period": 1, "lunch": False, "passing": False},
            {"start": "07:30", "end": "07:50", "period": 2, "lunch": False, "passing": True},
            {"start": "07:50", "end": "08:45", "period": 2, "lunch": False, "passing": False},
            {"start": "08:45", "end": "08:50", "period": 4, "lunch": False, "passing": True},
            {"start": "08:50", "end": "09:40", "period": 4, "lunch": False, "passing": False},
            {"start": "09:40", "end": "09:45", "period": 6, "lunch": False, "passing": True},
            {"start": "09:45", "end": "11:25", "period": 6, "lunch": False, "passing": False},
            {"start": "11:25", "end": "11:30", "period": 8, "lunch": False, "passing": True},
            {"start": "11:30", "end": "12:20", "period": 8, "lunch": False, "passing": False},
        ]
        lunchtimes = {
            "A": {"start": "09:45", "end": "10:15"},
            "B": {"start": "10:20", "end": "10:50"},
            "C": {"start": "10:55", "end": "11:25"},
        }
    elif day_of_week == 8: # Early release gold
        classtimes = [
            {"start": "07:00", "end": "07:30", "period": 1, "lunch": False, "passing": False},
            {"start": "07:30", "end": "07:50", "period": 3, "lunch": False, "passing": True},
            {"start": "07:50", "end": "08:45", "period": 3, "lunch": False, "passing": False},
            {"start": "08:45", "end": "08:50", "period": 5, "lunch": False, "passing": True},
            {"start": "08:50", "end": "09:40", "period": 5, "lunch": False, "passing": False},
            {"start": "09:40", "end": "09:45", "period": 7, "lunch": False, "passing": True},
            {"start": "09:45", "end": "11:25", "period": 7, "lunch": False, "passing": False},
            {"start": "11:25", "end": "11:30", "period": 9, "lunch": False, "passing": True},
            {"start": "11:30", "end": "12:20", "period": 9, "lunch": False, "passing": False},
        ]
        lunchtimes = {
            "A": {"start": "09:45", "end": "10:15"},
            "B": {"start": "10:20", "end": "10:50"},
            "C": {"start": "10:55", "end": "11:25"},
        }
    
    for classtime in classtimes:
        classtime['start'] = datetime.datetime.strptime(classtime['start'], '%H:%M').time()
        classtime['end'] = datetime.datetime.strptime(classtime['end'], '%H:%M').time()
    
    for key, value in lunchtimes.items():
        value['start'] = datetime.datetime.strptime(value['start'], '%H:%M').time()
        value['end'] = datetime.datetime.strptime(value['end'], '%H:%M').time()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            useractions.create_user(username='admin', password='admin', email='admin@example.com', created_by='system', role='admin')
            app.logger.info("Created admin user with username 'admin' and password 'admin'")
        update_schedule()
    app.run(debug=True, port=5200, host="0.0.0.0") if debugmode else serve(app, host='0.0.0.0', port=7842)