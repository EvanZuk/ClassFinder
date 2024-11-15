import os
import re
import platform
import functools
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from flask_limiter import Limiter
import smtplib
import datetime
from sqlalchemy.sql import func

app = Flask(__name__, static_folder='static', template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_PATH', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

limiter = Limiter(app, default_limits=["75/minute", "5/second"], key_func=lambda: request.remote_addr)
scheduler = APScheduler()

app.secret_key = os.environ.get("APP_KEY", "HOUFSyf938oJjg893y)(S*_)").encode('utf-8')
db = SQLAlchemy(app)
emailconfig = {
    'host': os.environ.get('EMAIL_HOST', 'smtp.gmail.com'),
    'port': os.environ.get('EMAIL_PORT', 587),
    'username': os.environ.get('EMAIL_USERNAME'),
    'password': os.environ.get('EMAIL_PASSWORD'),
    'from': os.environ.get('EMAIL_FROM', "classfinder@trey7658.com")
}
emailids = {}
bcrypt = Bcrypt(app)
debugmode = platform.node() != 'classfinder'
app.logger.setLevel('DEBUG' if debugmode else 'INFO')
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
    room = db.Column(db.String(10), nullable=False)
    period = db.Column(db.Integer, nullable=False)
    canvasid = db.Column(db.String(50), nullable=False)
    users = db.relationship('User', secondary='user_courses', back_populates='courses')

class Schedule(db.Model):
    day = db.Column(db.Integer, nullable=False, primary_key=True, unique=True)
    type = db.Column(db.String(50), nullable=False)
    virtual = db.Column(db.Boolean, nullable=False)

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
        if email is None:
            return {'status': 'error', 'message': 'Invalid emailid'}
        json = request.json
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            useractions.create_user(username='admin', password='admin', email='admin@example.com', created_by='system', role='admin')
            app.logger.info("Created admin user with username 'admin' and password 'admin'")
    app.run(debug=True, port=5200)