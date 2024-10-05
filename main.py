from flask import Flask, request, jsonify, render_template, redirect, send_from_directory
from flask_apscheduler import APScheduler
from flask_limiter import Limiter, HEADERS
import typing, platform, shutil, requests
from werkzeug.middleware.proxy_fix import ProxyFix
import json, functools, datetime, re, os, waitress, logging, random, smtplib
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from threading import Lock
from markupsafe import escape
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
app = Flask(__name__, template_folder='templates', static_folder='static')
app.logger.info('Starting ClassFinder...')
devmode = not platform.uname()[1] == 'classfinder'
app.logger.setLevel(logging.INFO if not devmode else logging.DEBUG)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2)
app.secret_key = os.environ['APP_KEY'].encode('utf-8')
smtp_server = os.environ.get('SMTP_SERVER', 'mail.smtp2go.com')
smtp_port = int(os.environ.get('SMTP_PORT', 2525))
smtp_user = os.environ.get('SMTP_USER', 'oneauth')
smtp_password = os.environ.get('SMTP_PASSWORD', '')
from_addr = os.environ.get('FROM_ADDR', 'classfinder@trey7658.com')
canvas_url = os.environ.get('CANVAS_URL', 'https://stem.instructure.com/')
limiter = Limiter(app=app, default_limits=["75/minute", "5/second"], headers_enabled=True, key_func=lambda: request.cookies.get('username') if 'username' in request.cookies else request.remote_addr, default_limits_exempt_when=lambda: request.cookies.get('username') in admins)
limiter.header_mapping = {
    HEADERS.LIMIT: "X-RateLimit-Limit",
    HEADERS.RESET: "X-RateLimit-Reset",
    HEADERS.REMAINING: "X-RateLimit-Remaining",
    HEADERS.RETRY_AFTER: "X-RateLimit-Retry-After"
}
bcrypt = Bcrypt(app)
csrf = CSRFProtect(app)
scheduler = APScheduler()
jsondir = os.environ.get('CLASSFINDER_DATA_DIR', '')
try:
    with open(f'{jsondir}users.json', 'r') as f: users = json.load(f)
except FileNotFoundError:
    users = {'trwy': {'password': bcrypt.generate_password_hash('passwordtrwy'.encode('utf-8')).decode('utf-8'), 'courses': ["p1"], "createdby": "server"}}
    with open(f'{jsondir}users.json', 'w') as f: json.dump(users, f)
try:
    with open(f'{jsondir}courses.json', 'r') as f: courses = json.load(f)
except FileNotFoundError:
    courses = {"p1": {"name": "Test Course", "room": "Test Room", "period": 1, "hidden": False, "lunch": None, "canvasid": None}}
    with open(f'{jsondir}courses.json', 'w') as f: json.dump(courses, f)
try:
    with open(f'{jsondir}requests.json', 'r') as f: requests = json.load(f)
except FileNotFoundError:
    with open(f'{jsondir}requests.json', 'w') as f: f.write('{"feature": {}, "bug": {}, "other": {}}')
    requests = {'feature': {}, 'bug': {}, 'other': {}}
backup_locks = {'courses': Lock(),'users': Lock(), 'requests': Lock()}
coursetimes = []
lunchtimes = {}
admins = ['trwy']
linkcodes = {}
courseday = 0
usermessages = {}
emailids = {}
resetpasswordemailids = {}
adminmessages = [f"Server started at {datetime.datetime.now().strftime('%m %d, %Y %H:%M:%S')}"]

def backup(selection: typing.Literal['courses', 'users', 'requests' 'all'] = 'all', bypass: bool = False):
    if selection in backup_locks:
        lock = backup_locks[selection]
        if not lock.acquire(blocking=not bypass):
            return False
        try:
            shutil.copyfile(f'{jsondir}{selection}.json', f'{jsondir}{selection}.bak.json')
        except Exception as e:
            app.logger.error(f'An error occurred while copying backup {selection}: ' + str(e) + " " + str(vars(e)))
        try:
            if selection == 'courses':
                globals()['courses'] = {(course['room'] if course['room'] != "N/A" else "") + 'p' + str(course['period']): course for course in sorted(globals()['courses'].values(), key=lambda x: x['period'])}
            with open(f'{jsondir}{selection}.json', 'w') as f:
                json.dump(globals()[selection], f, indent=4)
        except PermissionError:
            app.logger.critical(f'Permission error while backing up {selection}')
            adminmessages.append(f'Permission error while backing up {selection}') if not f'Permission error while backing up {selection}' in adminmessages else None
        except Exception as e:
            app.logger.critical('An error occurred while backing up: ' + str(e) + " " + str(vars(e)))
        finally:
            if selection == 'courses':
                courses = sorted(globals()['courses'].values(), key=lambda x: x['period'])
            lock.release()
    elif selection == 'all':
        for key in backup_locks:
            if not backup(key, bypass):
                return False
    else:
        return False
    return True
def verify_user(f=None, *, required: bool = True, onfail=redirect('/login/'), allowedusers: typing.List[str] = None):
    def decorator(func):
        @functools.wraps(func)
        def decorated_function(*args, **kwargs):
            username = authenticate(request)
            if required:
                if username is None:
                    app.logger.debug('Not logged in')
                    return onfail
                if allowedusers and username not in allowedusers:
                    app.logger.debug('Not allowed: ' + username)
                    return onfail
            return func(username, *args, **kwargs)
        return decorated_function

    if f is None:
        return decorator
    else:
        return decorator(f)

def is_admin(username):
    return username in admins

def authenticate(request):
    # Authenticate the user, return the username if successful, otherwise return None
    if 'token' in request.cookies and 'username' in request.cookies:
        if request.cookies.get('username') in users:
            if users[request.cookies.get('username')]['password'] == request.cookies.get('token'):
                return request.cookies.get('username')
    else:
        if 'Authorization' in request.headers:
            authorization = request.headers['Authorization']
            token = authorization.split(' ')[1]
            username = authorization.split(' ')[0]
            if username in users:
                if users[username]['password'] == token:
                    return username
                
    return None

def createuser(username, password, createdby='server'):
    hashed_password = bcrypt.generate_password_hash((password+username+'AFu328DF28f').encode('utf-8')).decode('utf-8')
    users[username] = {'password': hashed_password, 'courses': ["p1"], "createdby": createdby}
    backup('users')
    return hashed_password

def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]
def message(message: str, username: str = 'admin'):
    if username == 'admin':
        adminmessages.append(message) if not message in adminmessages else None
    elif username in usermessages:
        usermessages[username].append(message) if not message in usermessages[username] else None
    else:
        usermessages[username] = [message]

@app.route('/')
@verify_user
def home(username):
    classes = []
    allperiods = get_periods()
    if allperiods is not None:
        for course in users[username]['courses']:
            period = courses[course]['period']
            if period in allperiods:
                classes.append(courses[course])
    else:
        app.logger.debug("allperiods is None")
    app.logger.debug(allperiods)
    current_period, next_class = get_user_next_class(username)
    app.logger.debug
    return render_template('index.html', username=username, classes=classes, dayoff=coursetimes == None, currentperiod=current_period[2], devmode=devmode, nextclass=next_class.strftime('%m %d, %Y %H:%M:%S'), p='p', canvas_url=canvas_url)

def get_next_class():
    if not coursetimes == None:
        current_period = get_current_period()
    #     next_period = get_current_period()[2] + 1
    #     next_class = datetime.datetime.combine(datetime.datetime.today(), coursetimes[next_period][0]).strftime('%m %d, %Y %H:%M:%S') if next_period < len(coursetimes) else '08 2, 3000 14:55:00'
        if current_period != (datetime.time(0, 0), datetime.time(0, 0), 0, None):
            app.logger.debug(f'Currentperiod: {current_period}')
            next_class = (datetime.datetime.combine(datetime.datetime.today(), current_period[1])) + datetime.timedelta(seconds=3)
        else:
            app.logger.debug("No more classes today")
            next_class = datetime.datetime(3000, 8, 2, 14, 55)
    else:
        current_period = (datetime.datetime(3000, 8, 2, 7, 50), datetime.datetime(3000, 8, 2, 14, 55), 0)
        next_class = datetime.datetime(3000, 8, 2, 14, 55)
    return current_period,next_class

def get_user_next_class(username):
    current_period,next_class = get_next_class()
    for id,course in {course: courses[course] for course in users[username]['courses']}.items():
        if (current_period[2] == course['period']) and (current_period[3]) and course['lunch'] != None:
            lunch = lunchtimes[course['lunch']]
            time = datetime.datetime.now().time()
            if lunch:
                app.logger.debug(f'{str(time)} - {str(lunch)}')
                if time < lunch[0]:
                    app.logger.debug('time < lunch[0]')
                    next_class = datetime.datetime.combine(datetime.datetime.today(), lunch[0])
                elif lunch[0] <= time <= lunch[1]:
                    app.logger.debug('lunch[0] <= time <= lunch[1]')
                    next_class = datetime.datetime.combine(datetime.datetime.today(), lunch[1])
                else:
                    app.logger.debug('else')
                    next_class = datetime.datetime.combine(datetime.datetime.today(), current_period[1]) 
    return current_period,next_class

def get_user_current_class(username):
    current_period, _ = get_user_next_class(username)
    for course_id in users[username]['courses']:
        course = courses[course_id]
        if course['period'] == current_period[2]:
            return course
    return None

@app.errorhandler(404)
def page_not_found(e):
    app.logger.debug('404: ' + str(e))
    return redirect('/')

@app.errorhandler(429)
def ratelimit(e):
    app.logger.debug('Rate limit exceeded on ' + request.remote_addr + ' for ' + str(e))
    return jsonify({'status': 'failure', 'message': 'Rate limit exceeded'}), 429

@app.errorhandler(500)
def internal_error(e):
    app.logger.debug('Internal server error: ' + str(e))
    return jsonify({'status': 'failure', 'message': 'Internal server error'}), 500

@app.route('/indexa.css')
def index_css():
    app.logger.debug('index.css loaded')
    return app.send_static_file('index.css')

@app.route('/index.js/')
def index_js():
    return app.send_static_file('index.js')

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/icon.png')
def icon():
    return app.send_static_file('icon.png')

@app.route('/icon.small.png')
def iconsmall():
    return app.send_static_file('icon.small.png')

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/app-release.apk/')
def apk():
    return app.send_static_file('app-release.apk')

@app.route('/message/', methods=['POST', 'GET'])
@verify_user(allowedusers=admins)
def messageadmin(username):
    if request.method == 'GET':
        return render_template('message.html', users=[username for username in users])
    message(request.json['message'], request.json['username'])
    return jsonify({'status': 'success', 'message': 'Message sent'})

@app.route('/api/v1/link/', methods=['POST', 'GET'])
@csrf.exempt
@limiter.limit("2/minute", key_func=lambda: request.remote_addr, exempt_when=lambda: request.method == 'POST')
def link():
    if request.method == 'POST':
        code = request.json.get('code', None)
        if code is not None and int(code) in linkcodes:
            if linkcodes[int(request.json.get('code'))]['ip'] == request.remote_addr:
                if not linkcodes[int(request.json.get('code'))]['username'] == None:
                    response = jsonify({'status': 'success', 'token': users[linkcodes[int(request.json.get('code'))]['username']]['password'], 'username': linkcodes[int(request.json.get('code'))]['username']})
                    del linkcodes[int(request.json.get('code'))]
                    return response
                else:
                    return jsonify({'status': 'failure', 'message': 'No account linked'})
            else:
                return jsonify({'status': 'failure', 'message': 'This code does not belong to this device'}), 400
        else:
            return jsonify({'status': 'failure', 'message': 'Invalid code'}), 400
    code = random.randint(100000, 999999)
    linkcodes[code] = {'ip': request.remote_addr, 'username': None}
    return jsonify({'status': 'success', 'code': code})

@app.route('/api/v1/messages/', methods=['GET'])
@verify_user(onfail=({'status': 'failure', 'message': 'Not logged in'}, 401))
@csrf.exempt
def apimessages(username):
    return jsonify({'status': 'success', 'messages': usermessages[username] if username in usermessages else []})

@app.route('/api/v1/adminmessages/', methods=['GET'])
@verify_user(allowedusers=admins, onfail=({'status': 'failure', 'message': 'Not logged in'}, 401))
@csrf.exempt
def apiadminmessages(username):
    return jsonify({'status': 'success', 'messages': adminmessages})

@app.route('/api/v1/requests/', methods=['GET'])
@verify_user(allowedusers=admins, onfail=({'status': 'failure', 'message': 'Not logged in'}, 401))
@csrf.exempt
def apirequests(username):
    return jsonify({'status': 'success', 'requests': requests})

@app.route('/api/v1/courses/<courseid>/users', methods=['GET'])
@verify_user
@csrf.exempt
def courseusers(username, courseid):
    if courseid in users[username]['courses']:
        return jsonify({'status': 'success', 'users': [username for username in get_users_with_class(courseid)]})
    return jsonify({'status': 'failure', 'message': 'You are not enrolled in this course'}), 400

@app.route('/canvas/')
@verify_user
def canvas(username):
    current_course = get_user_current_class(username)
    if (current_course and current_course.get('canvasid')) and (not "access" in current_course.get('name').lower()) and (not "study hall" in current_course.get('name').lower()):
        return redirect(f"{canvas_url}/courses/{current_course['canvasid']}")
    return redirect(canvas_url)

@app.route('/signup/<emailid>', methods=['POST', 'GET'])
@limiter.limit("8/hour", key_func=lambda: request.remote_addr, exempt_when=lambda: request.method == 'GET')
def signupwithID(emailid):
    if 'token' in request.cookies:
        return redirect('/')
    if request.method == 'GET':
        if emailid in emailids:
            return render_template('signupstage2.html', email=emailids[emailid])
        else:
            return redirect('/signup/')
    if emailid in emailids:
        for user in users:
            if 'email' in users[user] and users[user]['email'] == emailids[emailid]:
                return jsonify({'status': 'failure', 'message': 'Email already in use'}), 400
        username = request.json['username']
        if not re.compile(r'^[a-z0-9_]{3,20}$').match(username):
            return jsonify({'status': 'failure', 'message': 'Invalid username, must be 3-20 characters, and only letters.'}), 400
        password = request.json['password']
        if username in users:
            return jsonify({'status': 'failure', 'message': 'Username already exists'}), 400
        hashed_password = bcrypt.generate_password_hash((password+username+'AFu328DF28f').encode('utf-8')).decode('utf-8')
        users[username] = {'password': hashed_password, 'courses': ["p1"], "createdby": username, 'email': emailids[emailid]}
        token = hashed_password
        response = jsonify({'status': 'success', 'message': 'Account created'})
        response.set_cookie('token', token, httponly=True, max_age=604800)
        response.set_cookie('username', username, httponly=True, max_age=604800)
        backup('users')
        del emailids[emailid]
        return response
    return jsonify({'status': 'failure', 'message': 'Invalid emailid'}), 400

@app.route('/signup/', methods=['POST', 'GET'])
@limiter.limit("2/hour", key_func=lambda: request.json['email'], exempt_when=lambda: request.method == 'GET')
def signup():
    if 'token' in request.cookies:
        return redirect('/')
    if request.method == 'GET':
        return render_template('signup.html')
    email = request.json['email']
    if not re.match(r'[a-z]*\.[a-z]*(@s.stemk12.org|@stemk12.org)', email):
        return jsonify({'status': 'failure', 'message': 'Invalid email'}), 400 
    for user in users:
        if 'email' in users[user] and users[user]['email'] == email:
            return jsonify({'status': 'failure', 'message': 'Email already in use'}), 400
    emailid = random.randbytes(16).hex()
    emailids[emailid] = email
    if not devmode:
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = email
        msg['Subject'] = 'Email Verification'
        msg.attach(MIMEText(f'Click this link to verify your email: https://class.trey7658.com/signup/{emailid}', 'plain'))
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_addr, email, msg.as_string())
        server.quit()
    else:
        app.logger.info(f'Email verification link: https://class.trey7658.com/signup/{emailid}')
    return jsonify({'status': 'success', 'message': 'Email sent'})
@app.route('/canvas/<path>/')
@verify_user
def canvaswithPath(username, path):
    current_course = get_user_current_class(username)
    if (current_course and current_course.get('canvasid')) and (not "access" in current_course.get('name').lower()) and (not "study hall" in current_course.get('name').lower()):
        return redirect(f"{canvas_url}/courses/{current_course['canvasid']}/{path}")
    return redirect(canvas_url)

@app.route('/link/', methods=['POST', 'GET'])
@verify_user
def linkaccount(username):
    if request.method == 'GET':
        code = request.args.get('code', None)
        if code is None or int(code) not in linkcodes:
            return render_template('linkreq.html', username=username, devmode=devmode)
        else:
            return render_template('link.html', username=username, code=int(request.args.get('code')), ip=linkcodes[int(request.args.get('code'))]['ip'], currentip=request.remote_addr, devmode=devmode)
    code = int(request.json['code'])
    if code not in linkcodes:
        return jsonify({'status': 'failure', 'message': 'Invalid code'}), 400
    linkcodes[code]['username'] = username
    return jsonify({'status': 'success', 'message': 'Account linked'})

@app.route('/app-apk-updates/')
def apkupdates():
    current_version = request.args.get('version')
    with open('apkver.txt', 'r') as f:
        vers = f.read().split('\n')
    app.logger.debug(vers)
    new_version = vers[0]
    new_version_str = vers[1]
    app.logger.debug(f'Current version: {current_version}, New version: {new_version}, New version string: {new_version_str}')
    if current_version == None:
        return jsonify({'status': 'failure', 'message': 'No version specified'}), 400
    elif current_version != new_version:
        return jsonify({'status': 'success', 'message': 'Update available', 'url': '/app-release.apk/', 'version': new_version, 'versionstr': new_version_str, 'newversion': True})
    else:
        return jsonify({'status': 'success', 'message': 'No update available', 'version': new_version, 'versionstr': new_version_str, 'newversion': False})

@app.route('/robots.txt/')
def robots():
    return "User-agent: *\nDisallow: /"

@app.route('/AddCourseBulk.gif')
@verify_user
def addcoursebulk():
    return app.send_static_file('AddCourseBulk.gif')

@app.route('/clearcolors/', methods=['GET', 'POST'])
@verify_user
@csrf.exempt
def clearcolors(username):
    users[username]['colors'] = {}
    backup('users')
    return jsonify({'status': 'success', 'message': 'Colors cleared'}) if request.method == 'POST' else redirect('/')

@app.route('/api/v1/userdata/', methods=['GET'])
@verify_user
@csrf.exempt
def userdata(username):
    return jsonify({'status': 'success', 'data': {key: value for key, value in users[username].items() if key != 'password'}, 'message': 'Password is not included'})

@app.route('/CreateToken.gif/')
@verify_user
def createtoken(username):
    return app.send_static_file('createtoken.gif')

@app.route('/removemessage/', methods=['DELETE'])
@verify_user
def removemessage(username):
    if request.json['message'] in usermessages[username]:
        usermessages[username].remove(request.json['message'])
    return jsonify({'status': 'success', 'message': 'Message removed'})

@app.route('/admin/removemessage/', methods=['DELETE'])
@verify_user(allowedusers=admins)
def adminremovemessage(username):
    if request.json['message'] in adminmessages:
        adminmessages.remove(request.json['message'])
    return jsonify({'status': 'success', 'message': 'Message removed'})

@app.route('/login/', methods=['POST', 'GET'])
@limiter.limit("4/minute", key_func=lambda: request.remote_addr, exempt_when=lambda: request.method == 'GET')
def login():
    if 'token' in request.cookies:
        if request.cookies.get('username') in users:
            if users[request.cookies.get('username')]['password'] == request.cookies.get('token'):
                return redirect('/')
        response = redirect('/login/')
        response.set_cookie('token', '', expires=0)
        response.set_cookie('username', '', expires=0)
        return response
    if request.method == 'GET':
        if request.cookies.get('admtoken') != None and request.cookies.get('admusername') != None:
            token = request.cookies['admtoken']
            username = request.cookies['admusername']
            response = redirect('/')
            response.set_cookie('token', token, httponly=True, max_age=604800)
            response.set_cookie('username', username, httponly=True, max_age=604800)
            response.set_cookie('admtoken', '', expires=0)
            response.set_cookie('admusername', '', expires=0)
            return response
        return render_template('login.html', devmode=devmode, dayoff=coursetimes == None)
    request.get_json()
    username = request.json['username']
    if username not in users:
        return jsonify({'status': 'failure', 'message': 'Username does not exist'}), 400
    password = request.json['password']
    if not bcrypt.check_password_hash(users[username]['password'], (password+username+'AFu328DF28f').encode('utf-8')):
        return jsonify({'status': 'failure', 'message': 'Incorrect password'}), 400
    token = users[username]['password']  # Generate a token for the user
    response = jsonify({'status': 'success', 'message': 'Logged in'})
    response.set_cookie('token', token, httponly=True, max_age=604800)  # Set the token as a cookie in the response
    response.set_cookie('username', username, httponly=True, max_age=604800)
    return response

@app.route('/ping/', methods=['GET', 'POST'])
def ping():
    return jsonify({'status': 'success', 'message': 'Pong'})

@app.route('/request/', methods=['POST', 'GET'])
@verify_user
@limiter.limit("2/day", key_func=lambda: request.cookies.get('username'), exempt_when=lambda: request.method == 'GET' or request.cookies.get('username') == 'trwy')
def requestform(username):
    if request.method == 'GET':
        return render_template('request.html', username=request.cookies.get('username'))
    if not request.json['type'] in ['feature', 'bug', 'other']:
        return jsonify({'status': 'failure', 'message': 'Invalid type'}), 400
    if not request.json['request']:
        return jsonify({'status': 'failure', 'message': 'No request specified'}), 400
    if not request.json['description']:
        return jsonify({'status': 'failure', 'message': 'No description specified'}), 400
    request_type = escape(request.json['type'])
    request_content = escape(request.json['request'])
    request_description = escape(request.json['description'])
    requests[request_type][str(random.randint(100000000, 999999999))] = {
        'request': request_content,
        'description': request_description,
        'username': request.cookies.get('username')
    }
    backup('requests')
    return jsonify({'status': 'success', 'message': 'Request submitted'})

@app.route('/admin/deleterequest/', methods=['DELETE'])
@verify_user(allowedusers=admins)
def deleterequest(username):
    request_type = request.json['type']
    request_id = request.json['id']
    if request_type not in requests or request_id not in requests[request_type]:
        return jsonify({'status': 'failure', 'message': 'Request does not exist'}), 400
    del requests[request_type][request_id]
    backup('requests')
    return jsonify({'status': 'success', 'message': 'Request deleted'})

@app.route('/api/v1/login/', methods=['POST'])
@limiter.limit("2/minute", key_func=lambda: request.remote_addr)
@csrf.exempt
def apilogin():
    username = request.json['username']
    if username not in users:
        return jsonify({'status': 'failure', 'message': 'Username does not exist'}), 400
    password = request.json['password']
    if not bcrypt.check_password_hash(users[username]['password'], (password+username+'AFu328DF28f').encode('utf-8')):
        return jsonify({'status': 'failure', 'message': 'Incorrect password'}), 400
    token = users[username]['password']
    return jsonify({'status': 'success', 'message': 'Logged in', 'token': token})

@app.route('/api/v1/courses/', methods=['GET'])
@verify_user(onfail=({'status': 'failure', 'message': 'Not logged in'}, 401))
@csrf.exempt
def apicourses(username):
    return jsonify({'status': 'success', 'courseids': users[username]['courses'], 'courses': [courses[course] for course in users[username]['courses']]})

@app.route('/api/v1/currentcourses/', methods=['GET'])
@verify_user(onfail=({'status': 'failure', 'message': 'Not logged in'}, 401))
@csrf.exempt
def apicurrentcourses(username):
    current_period, next_class = get_user_next_class(username)
    classes = []
    allperiods = get_periods()
    if allperiods is not None:
        for course in users[username]['courses']:
            period = courses[course]['period']
            if period in allperiods:
                classes.append(courses[course])
    return jsonify({
        'status': 'success', 
        'courses': classes,
        'status': 'success', 
        'currentperiod': current_period[2], 
        'nextclass': int(next_class.timestamp()) if isinstance(next_class, datetime.datetime) else next_class,
        'dayoff': coursetimes == None
    })

@app.route('/api/v1/currentperiod/', methods=['GET'])
@verify_user(onfail=({'status': 'failure', 'message': 'Not logged in'}, 401), required=False)
@csrf.exempt
def apicurrentperiod(username):
    current_period, next_class = (get_next_class()) if username == None else get_user_next_class(username)
    response = jsonify({
        'status': 'success', 
        'currentperiod': current_period[2], 
        'nextclass': int(next_class.timestamp()) if isinstance(next_class, datetime.datetime) else next_class
    })
    return response

@app.route('/api/v1/change-password/', methods=['POST'])
@verify_user(onfail=({'status': 'failure', 'message': 'Not logged in'}, 401))
@csrf.exempt
def apichange_password(username):
    password = request.json['password']
    users[username]['password'] = bcrypt.generate_password_hash((password+username+'AFu328DF28f').encode('utf-8')).decode('utf-8')
    backup('users')
    return jsonify({'status': 'success', 'message': 'Password changed', 'token': users[username]['password']})

@app.route('/api/v1/deleteaccount/', methods=['DELETE'])
@verify_user(onfail=({'status': 'failure', 'message': 'Not logged in'}, 401))
@csrf.exempt
def apideleteaccount(username):
    del users[username]
    backup('users')
    return jsonify({'status': 'success', 'message': 'Account deleted'})

@app.route('/bookmarks/')
@verify_user
def bookmarks(username):
    return render_template('bookmarks.html', username=username)

@app.route('/change-password/', methods=['POST', 'GET'])
@verify_user
def change_password(username):
    if request.method == 'GET':
        return render_template('change-password.html', username=username)
    password = request.json['password']
    users[username]['password'] = bcrypt.generate_password_hash((password+username+'AFu328DF28f').encode('utf-8')).decode('utf-8')
    backup('users')
    response = jsonify({'status': 'success', 'message': 'Password changed'})
    response.set_cookie('token', users[username]['password'], httponly=True, max_age=604800)
    return response

@app.route('/reset-password/', methods=['POST', 'GET'])
@limiter.limit("2/hour", key_func=lambda: request.json['email'], exempt_when=lambda: request.method == 'GET')
def reset_password():
    if request.method == 'GET':
        return render_template('reset-password.html')
    email = request.json['email']
    if not re.match(r'[a-z]*\.[a-z]*(@s.stemk12.org|@stemk12.org)', email):
        return jsonify({'status': 'failure', 'message': 'Invalid email'}), 400
    username = ""
    for user in users:
        if 'email' in users[user] and users[user]['email'] == email:
            username = user
            break
    if username == "":
        return jsonify({'status': 'success', 'message': 'Email sent if account exists'})
    emailid = random.randbytes(16).hex()
    resetpasswordemailids[emailid] = username
    if not devmode:
        msg = MIMEMultipart()
        msg['From'] = from_addr
        msg['To'] = email
        msg['Subject'] = 'Password Reset'
        msg.attach(MIMEText(f'Click this link to reset your password: https://class.trey7658.com/reset-password/{emailid}', 'plain'))
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(from_addr, email, msg.as_string())
        server.quit()
    else:
        app.logger.info(f'Password reset link: https://class.trey7658.com/reset-password/{emailid}')
    return jsonify({'status': 'success', 'message': 'Email sent if account exists'})

@app.route('/reset-password/<emailid>/', methods=['POST', 'GET'])
@limiter.limit("8/hour", key_func=lambda: request.remote_addr, exempt_when=lambda: request.method == 'GET')
def resetpasswordwithID(emailid):
    if request.method == 'GET':
        if emailid in resetpasswordemailids:
            return render_template('reset-password-stage2.html', username=resetpasswordemailids[emailid])
        else:
            return redirect('/reset-password/')
    if emailid in resetpasswordemailids:
        username = resetpasswordemailids[emailid]
        password = request.json['password']
        users[username]['password'] = bcrypt.generate_password_hash((password+username+'AFu328DF28f').encode('utf-8')).decode('utf-8')
        response = jsonify({'status': 'success', 'message': 'Password changed'})
        response.set_cookie('token', users[username]['password'], httponly=True, max_age=604800)
        response.set_cookie('username', username, httponly=True, max_age=604800)
        backup('users')
        del resetpasswordemailids[emailid]
        return response
    return jsonify({'status': 'failure', 'message': 'Invalid emailid'}), 400

@app.route('/account/', methods=['POST', 'GET'])
@verify_user
def account(username):
    newcourses={}
    for id, course in courses.items():
        if course['canvasid'] == None and id in users[username]['courses']:
            newcourses[id] = course
    newclasses = []
    for classn in [courses[course] for course in users[username]['courses']]:
        classn['users'] = get_users_with_class(classn['room']+'p'+str(classn['period']))
        newclasses.append(classn)
    return render_template('account.html', username=username, devmode=devmode, classcount=len(users[username]['courses']), showcanvasid=len(newcourses) == len(users[username]['courses']), messages=usermessages[username] if username in usermessages else [], classes=newclasses, canvas_url=canvas_url)

@app.route('/logout/', methods=['POST', 'GET'])
def logout():
    if request.method == 'GET': response = redirect('/login')
    else: response = jsonify({'status': 'success', 'message': 'Logged out'})
    response.set_cookie('token', '', expires=0)
    response.set_cookie('username', '', expires=0)
    return response

@app.route('/admin/')
@verify_user(allowedusers=admins)
def admin(username):
    current_period = get_current_period()
    return render_template('admin.html', username=username, dayoff=False, classes=courses, p='p', currentperiod=current_period[2], requests=requests, messages=adminmessages, users=users, currentuser=username)

@app.route('/admin/deleteuser/', methods=['DELETE'])
@verify_user(allowedusers=admins)
def deleteuser(username):
    if request.json['username'] in users:
        app.logger.info(f'Deleting user {request.json["username"]} by {username}')
        del users[request.json['username']]
        backup('users')
        return jsonify({'status': 'success', 'message': 'User deleted'})
    return jsonify({'status': 'failure', 'message': 'User does not exist'}), 400

@app.route('/admin/backup', methods=['POST', 'GET'])
@verify_user(allowedusers=admins)
def adminbackup(username):
    app.logger.info('backing up from http request by ' + username)
    return {'status': backup('all')}

@app.route('/bulkaddcourse/', methods=['POST', 'GET'])
@verify_user
@limiter.limit("2/day", key_func=lambda: request.cookies.get('username'), exempt_when=lambda: request.method == 'GET' or request.cookies.get('username') == 'trwy')
def bulkaddcourse(username):
    if not (len(users[username]['courses']) < 10 or username == 'trwy'):
        app.logger.debug('')
        if request.method == 'GET':
            return redirect('/')
    if request.method == 'GET':
        return render_template('bulkaddcourse.html', username=username)
    if not request.json['courses']:
        return jsonify({'status': 'failure', 'message': 'No courses specified'}), 400
    coursesr = request.json['courses'].split('\n')
    coursesr = split_list(coursesr, 5)
    if len(coursesr) > (10 - len(users[username]['courses'])):
        return jsonify({'status': 'failure', 'message': 'Too many courses'}), 400
    for course in coursesr:
        course[1] = course[1].rstrip().lstrip()
        course[4] = course[4].rstrip().lstrip()
        course[0] = course[0].rstrip().lstrip()
        room = re.match(re.compile(r'(E?[0-9]{3})|MS Cafe'), course[4].replace("Rm: ", "").replace(":", ""))
        app.logger.debug(course)
        app.logger.debug(room)
        if room:
            room = room.group()
        course[0] = int(course[0]) if course[0] != 'Access' else 4.5
        if not room:
            app.logger.debug(f'Invalid room: {course[4]}')
            continue
        if not (2 <= course[0] <= 9):
            app.logger.debug(f'Invalid period: {course[0]}')
            continue
        # index 0 is the period
        # index 1 is the name
        # ignore index 2 and 3
        # index 4 is the room
        if not room+'p'+str(course[0]) in courses:
            courses[room+'p'+str(course[0])] = {'name': course[1], 'room': room, 'period': course[0], "hidden": False, "lunch": None, "canvasid": None, "createdby": username}
        else:
            app.logger.debug(f'Course already exists: {room}p{course[0]}')
    # Add the user to the course if the json "join" is true
    if request.json['join']:
        for course in coursesr:
            room = re.match(re.compile(r'(E?[0-9]{3})|MS Cafe'), course[4].replace("Rm: ", "").replace(":", ""))
            if room:
                room = room.group()
            else:
                app.logger.debug(f'Invalid room while join: {course[4]}')
                continue
            course[4] = room
            if courses[course[4].rstrip().lstrip()+'p'+str(course[0])]:
                if course[4].rstrip().lstrip()+'p'+str(course[0]) not in users[username]['courses']:
                    users[username]['courses'].append(course[4].rstrip().lstrip()+'p'+str(course[0])) if not course[4].rstrip().lstrip()+'p'+str(course[0]) in users[username]['courses'] else None
                else:
                    app.logger.debug(f'Already in course: {course[4].rstrip().lstrip()}p{course[0]}')
            app.logger.debug(f'Added to course: {course[4].rstrip().lstrip()}p{course[0]}')
    backup('all')
    return jsonify({'status': 'success', 'message': 'Courses added'})

@app.route('/setlunch/', methods=['POST', 'GET'])
@verify_user
def set_lunch(username):
    if request.method == 'GET':
        selected_course = request.args.get('course')
        if selected_course and selected_course not in users[username]['courses']:
            return jsonify({'status': 'failure', 'message': 'You are not enrolled in this course'}), 400
        ocourse_data = {selected_course: courses[selected_course]} if selected_course else ({course: courses[course] for course in users[username]['courses']} if not username in admins else courses)
        course_data = ocourse_data.copy()
        for course in ocourse_data:
            if not (courses[course]['period'] == 6 or courses[course]['period'] == 7):
                del course_data[course]
        return render_template('setlunch.html', username=username, courses=course_data)
    
    try:
        course = request.json['course']
        lunch = request.json['lunch']
    except KeyError:
        return jsonify({'status': 'failure', 'message': 'Course or lunch not specified'}), 400

    if course not in courses:
        return jsonify({'status': 'failure', 'message': 'Course does not exist'}), 400
    
    valid_lunch_options = ['A', 'B', 'C', 'None']
    if lunch not in valid_lunch_options:
        return jsonify({'status': 'failure', 'message': 'Invalid lunch'}), 400
    
    if course not in users[username]['courses']:
        return jsonify({'status': 'failure', 'message': 'You are not enrolled in this course'}), 400
    
    if not (courses[course]['period'] == 6 or courses[course]['period'] == 7):
        return jsonify({'status': 'failure', 'message': 'Cannot set lunch for this course'}), 400

    courses[course]['lunch'] = None if lunch == 'None' else lunch
    backup('courses')
    return jsonify({'status': 'success', 'message': 'Lunch set'})

@app.route('/joincourse/', methods=['POST', 'GET'])
@verify_user
def joincourse(username):
    if request.method == 'GET':
        return render_template('joincourse.html', username=username, courses=courses)
    course = request.json['course']
    if course == None:
        return jsonify({'status': 'failure', 'message': 'Course not specified'}), 400
    if course not in courses:
        return jsonify({'status': 'failure', 'message': 'Course does not exist'}), 400
    if course in users[username]['courses']:
        return jsonify({'status': 'failure', 'message': 'Already in course'}), 400
    users[username]['courses'].append(course)
    backup('users')
    return jsonify({'status': 'success', 'message': 'Course joined'})

@app.route('/setcanvasid/', methods=['POST', 'GET'])
@verify_user
@limiter.limit("5/hour", key_func=lambda: request.cookies.get('username'))
def adminsetcanvasid(username):
    if request.method == 'GET':
        if not request.args.get('canvastoken'):
            return render_template('setcanvasidreq.html')
        headers = {'Authorization': 'Bearer ' + request.args.get('canvastoken')}
        ccourses = requests.get(f'{canvas_url}/api/v1/dashboard/dashboard_cards', headers=headers)
        app.logger.debug(ccourses.json())
        newcourses={}
        for id, course in courses.items():
            if course['canvasid'] == None and id in users[username]['courses'] and not course['hidden']:
                newcourses[id] = course
        if not len(newcourses) == 0:
            return render_template('setcanvasid.html', username=username, ccourses={course['id']: course['shortName'] for course in ccourses.json()}, courses=newcourses)
        else:
            return jsonify({'status': 'failure', "message": 'no classes to be added'})
    app.logger.debug(request.json)
    newcourses=[]
    for id, course in courses.items():
        if course['canvasid'] == None and id in users[username]['courses'] and not course['hidden']:
            newcourses.append(id)
    for id, course in request.json.items():
        if id in newcourses:
            courses[id]['canvasid'] = (course if not course == 'None' else None)
    backup('courses')
    headers = {'Authorization': 'Bearer ' + request.args.get('canvastoken')}
    requests.delete(f'{canvas_url}/login/oauth2/token', headers=headers)
    return jsonify({'status': 'success', 'message': 'Canvas IDs set'})

@app.route('/timer/')
@verify_user(required=False)
def timer(username):
    current_period, next_class = get_user_next_class(username) if username != None else get_next_class()
    print(next_class)
    if (coursetimes != None) and (current_period != None) and (next_class != None) and (next_class != datetime.datetime(3000, 8, 2, 14, 55)):
        return render_template('timer.html', currentperiod=current_period[2], nextclass=next_class.strftime('%Y-%m-%d %H:%M:%S') if isinstance(next_class, datetime.datetime) else next_class)
    return redirect('/')

@app.route('/admin/createaccount/', methods=['POST', 'GET'])
@verify_user(allowedusers=admins)
def admincreateaccount(username):
    requsername= username
    if request.method == 'GET':
        return render_template('admcreateaccount.html', username=username)
    username = request.json['username']
    if not re.compile(r'^[a-z0-9_]{3,20}$').match(username):
        return jsonify({'status': 'failure', 'message': 'Invalid username, must be 3-20 characters, and only letters.'}), 400
    password = request.json['password']
    if username in users:
        return jsonify({'status': 'failure', 'message': 'Username already exists'}), 400
    hashed_password = bcrypt.generate_password_hash((password+username+'AFu328DF28f').encode('utf-8')).decode('utf-8')
    users[username] = {'password': hashed_password, 'courses': ["p1"], "createdby": requsername, 'email': None}
    backup('users')
    token = hashed_password
    login = request.json['login']
    response = jsonify({'status': 'success', 'message': 'Account created', 'token': token})
    response.set_cookie('token', token, httponly=True, max_age=604800) if login else None
    response.set_cookie('username', username, httponly=True, max_age=604800) if login else None
    response.set_cookie('admtoken', request.cookies['token'], httponly=True, max_age=604800)
    response.set_cookie('admusername', request.cookies['username'], httponly=True, max_age=604800)
    return response

@app.route('/admin/deletecourse/', methods=['POST', 'GET'])
@verify_user(allowedusers=admins)
def admindeletecourse(username):
    if request.method == 'GET':
        return render_template('admin.html', username=username)
    course = request.json['course']
    if course == None:
        return jsonify({'status': 'failure', 'message': 'Course not specified'}), 400
    if course not in courses:
        return jsonify({'status': 'failure', 'message': 'Course does not exist'}), 400
    del courses[course]
    for user in users.values():
        if course in user['courses']:
            user['courses'].remove(course)
    backup('all')
    return jsonify({'status': 'success', 'message': 'Course deleted'})

@app.route('/admin/login/', methods=['POST', 'GET'])
@verify_user(allowedusers=admins)
def adminlogin(username):
    # allow switching to other user without password.
    if request.method == 'GET':
        return render_template('adminlogin.html')
    request.get_json()
    username = request.json['username']
    if username not in users:
        return jsonify({'status': 'failure', 'message': 'Username does not exist'}), 400
    token = users[username]['password']
    response = jsonify({'status': 'success', 'message': 'Logged in'})
    response.set_cookie('admtoken', request.cookies['token'], httponly=True, max_age=604800)
    response.set_cookie('admusername', request.cookies['username'], httponly=True, max_age=604800)
    response.set_cookie('token', token, httponly=True, max_age=300)
    response.set_cookie('username', username, httponly=True, max_age=300)
    return response

@app.route('/admin/addtoall/')
@verify_user(allowedusers=admins)
def addtoall(username): 
    key = request.args.get('key')
    if not key:
        return jsonify({'status': 'failure', 'message': 'No key specified'}), 400
    for course in courses:
        # Add the key to all courses
        courses[course][key] = None
    backup('courses')
    return jsonify({'status': 'success', 'message': 'Added to all courses'})

@app.route('/admin/removefromall/')
@verify_user(allowedusers=admins)
def removefromall(username):
    key = request.args.get('key')
    if not key:
        return jsonify({'status': 'failure', 'message': 'No key specified'}), 400
    for course in courses:
        # Remove the key from all courses
        del courses[course][key]
    backup('courses')
    return jsonify({'status': 'success', 'message': 'Removed from all courses'})

@app.route('/admin/courses/')
@verify_user(allowedusers=admins)
def admincourses(username):
    return jsonify({'status': 'success', 'courses': courses})

@app.route('/deleteaccount/', methods=['POST', 'GET'])
@verify_user
def deleteaccount(username):
    del users[username]
    backup('users')
    if request.method == 'GET':
        return redirect('/logout')
    return jsonify({'status': 'success', 'message': 'Account deleted'})

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@scheduler.task('interval', id='backup', minutes=30, misfire_grace_time=60)
def backup_task():
    app.logger.debug('Backing up...')
    if backup('all'):
        app.logger.info('Backup successful')
    else:
        app.logger.error('Backup failed')

@scheduler.task('cron', id='update_course_time', hour=1, minute=0, misfire_grace_time=3600)
def update_course_time(dayoverride: typing.Optional[int] = None):
    app.logger.debug('Updating course times...')
    global coursetimes
    global lunchtimes
    global courseday
    day = datetime.datetime.today().weekday() if dayoverride == None else dayoverride
    coursetimes = []
    lunchtimes = {}
    if day == 0:
        coursetimes.append((datetime.time(7, 0), datetime.time(7, 50), 1, False))
        coursetimes.append((datetime.time(7,50), datetime.time(9, 30), 2, False))
        coursetimes.append((datetime.time(9,30), datetime.time(11,10), 4, False))
        coursetimes.append((datetime.time(11, 10), datetime.time(13,15), 6, True))
        coursetimes.append((datetime.time(13,15), datetime.time(14,55), 8, False))
        courseday = 0
        # lunchtimes.append((datetime.time(11,15), datetime.time(11,45)), "A")
        # lunchtimes.append((datetime.time(12,0), datetime.time(12,30)), "B")
        # lunchtimes.append((datetime.time(12,45), datetime.time(13,15)), "C")
        lunchtimes["A"] = (datetime.time(11,15), datetime.time(11,45))
        lunchtimes["B"] = (datetime.time(12,0), datetime.time(12,30))
        lunchtimes["C"] = (datetime.time(12,45), datetime.time(13,15))
    elif day == 1:
        coursetimes.append((datetime.time(7, 0), datetime.time(7, 50), 1, False))
        coursetimes.append((datetime.time(7,50), datetime.time(9, 30), 3, False))
        coursetimes.append((datetime.time(9,30), datetime.time(11,10), 5, False))
        coursetimes.append((datetime.time(11, 10), datetime.time(13,15), 7, True))
        coursetimes.append((datetime.time(13,15), datetime.time(14,55), 9, False))
        courseday = 1
        # lunchtimes.append((datetime.time(11,15), datetime.time(11,45), "A"))
        # lunchtimes.append((datetime.time(12,0), datetime.time(12,30), "B"))
        # lunchtimes.append((datetime.time(12,45), datetime.time(13,15), "C"))
        lunchtimes["A"] = (datetime.time(11,15), datetime.time(11,45))
        lunchtimes["B"] = (datetime.time(12,0), datetime.time(12,30))
        lunchtimes["C"] = (datetime.time(12,45), datetime.time(13,15))
    elif day == 2:
        coursetimes.append((datetime.time(7, 0), datetime.time(7, 50), 1, False))
        coursetimes.append((datetime.time(7,50), datetime.time(9, 5), 2, False))
        coursetimes.append((datetime.time(9,5), datetime.time(10,25), 4, False))
        coursetimes.append((datetime.time(10,25), datetime.time(11,40), 4.5, False))
        coursetimes.append((datetime.time(11,40), datetime.time(13,35), 6, True))
        coursetimes.append((datetime.time(13,35), datetime.time(14,55), 8, False))
        courseday = 2
        # lunchtimes.append((datetime.time(11,45), datetime.time(12,15), "A"))
        # lunchtimes.append((datetime.time(12,25), datetime.time(12,55), "B"))
        # lunchtimes.append((datetime.time(13,5), datetime.time(13,35), "C"))
        lunchtimes["A"] = (datetime.time(11,45), datetime.time(12,15))
        lunchtimes["B"] = (datetime.time(12,25), datetime.time(12,55))
        lunchtimes["C"] = (datetime.time(13,5), datetime.time(13,35))
    elif day == 3:
        coursetimes.append((datetime.time(7, 0), datetime.time(7, 50), 1, False))
        coursetimes.append((datetime.time(7,50), datetime.time(9, 5), 3, False))
        coursetimes.append((datetime.time(9,5), datetime.time(10,25), 5, False))
        coursetimes.append((datetime.time(10,25), datetime.time(11,40), 4.5, False))
        coursetimes.append((datetime.time(11,40), datetime.time(13,35), 7, True))
        coursetimes.append((datetime.time(13,35), datetime.time(14,55), 9, False))
        courseday = 3
        # lunchtimes.append((datetime.time(11,45), datetime.time(12,15), "A"))
        # lunchtimes.append((datetime.time(12,25), datetime.time(12,55), "B"))
        # lunchtimes.append((datetime.time(13,5), datetime.time(13,35), "C"))
        lunchtimes["A"] = (datetime.time(11,45), datetime.time(12,15))
        lunchtimes["B"] = (datetime.time(12,25), datetime.time(12,55))
        lunchtimes["C"] = (datetime.time(13,5), datetime.time(13,35))

    elif day == 4:
        coursetimes.append((datetime.time(7, 0), datetime.time(7, 50), 1, False))
        coursetimes.append((datetime.time(7,50), datetime.time(8,35), 2, False))
        coursetimes.append((datetime.time(8,35), datetime.time(9,20), 3, False))
        coursetimes.append((datetime.time(9,20), datetime.time(10,5), 4, False))
        coursetimes.append((datetime.time(10,5), datetime.time(10,50), 5, False))
        coursetimes.append((datetime.time(10,50), datetime.time(12,40), 6, True))
        coursetimes.append((datetime.time(12,40), datetime.time(13,25), 7, False))
        coursetimes.append((datetime.time(13,25), datetime.time(14,10), 8, False))
        coursetimes.append((datetime.time(14,10), datetime.time(14,55), 9, False))
        courseday = 4
        # lunchtimes.append((datetime.time(10,55), datetime.time(11,25), "A"))
        # lunchtimes.append((datetime.time(11,32), datetime.time(12,2), "B"))
        # lunchtimes.append((datetime.time(12,10), datetime.time(12,40), "C"))
        lunchtimes["A"] = (datetime.time(10,55), datetime.time(11,25))
        lunchtimes["B"] = (datetime.time(11,32), datetime.time(12,2))
        lunchtimes["C"] = (datetime.time(12,10), datetime.time(12,40))
    elif dayoverride == 6:
        coursetimes.append((datetime.time(7, 0), datetime.time(7, 50), 1, False))
        coursetimes.append((datetime.time(7,50), datetime.time(8,45), 2, False))
        coursetimes.append((datetime.time(8,45), datetime.time(9,40), 4, False))
        coursetimes.append((datetime.time(9,40), datetime.time(11,25), 6, True))
        coursetimes.append((datetime.time(11,25), datetime.time(12,20), 8, False))
        courseday = 6
        # lunchtimes.append((datetime.time(9,45), datetime.time(10,15), "A"))
        # lunchtimes.append((datetime.time(10,20), datetime.time(10,50), "B"))
        # lunchtimes.append((datetime.time(10,55), datetime.time(11,25), "C"))
        lunchtimes["A"] = (datetime.time(9,45), datetime.time(10,15))
        lunchtimes["B"] = (datetime.time(10,20), datetime.time(10,50))
        lunchtimes["C"] = (datetime.time(10,55), datetime.time(11,25))
    elif dayoverride == 7:
        coursetimes.append((datetime.time(7, 0), datetime.time(7, 50), 1, False))
        coursetimes.append((datetime.time(7,50), datetime.time(8,45), 3, False))
        coursetimes.append((datetime.time(8,45), datetime.time(9,40), 5, False))
        coursetimes.append((datetime.time(9,40), datetime.time(11,25), 7, True))
        coursetimes.append((datetime.time(11,25), datetime.time(12,20), 9, False))
        courseday = 7
        # lunchtimes.append((datetime.time(9,45), datetime.time(10,15), "A"))
        # lunchtimes.append((datetime.time(10,20), datetime.time(10,50), "B"))
        # lunchtimes.append((datetime.time(10,55), datetime.time(11,25), "C"))
        lunchtimes["A"] = (datetime.time(9,45), datetime.time(10,15))
        lunchtimes["B"] = (datetime.time(10,20), datetime.time(10,50))
        lunchtimes["C"] = (datetime.time(10,55), datetime.time(11,25))
    else:
        coursetimes = None
        lunchtimes = None
        courseday = 5
    app.logger.info('Course times updated')
    app.logger.debug('Coursetimes is none' if coursetimes == None else 'Coursetimes is not none')

@scheduler.task('cron', id='delete_login_codes', hour=1, minute=0, misfire_grace_time=3600)
def delete_login_codes():
    global linkcodes
    linkcodes = {}

def get_current_period():
    # Returns the current period
    # The 5th value is the current lunch
    # The 4th value is if the periods lunch time applies today
    # The 3rd value is the current period
    if coursetimes == None:
        return (datetime.time(0, 0), datetime.time(0, 0), 0, None)
    now = datetime.datetime.now().time()
    lunch = get_lunch()
    for course in coursetimes:
        if course[0] <= now <= course[1]:
            return course + ((lunch[1],) if lunch != None else (None,))
    return (datetime.time(0, 0), datetime.time(0, 0), 0, None)

def get_lunch():
    # Returns the current lunch period
    if not isinstance(lunchtimes, dict):
        return None
    now = datetime.datetime.now().time()
    for lunch, times in lunchtimes.items():
        if isinstance(times, tuple) and len(times) == 2 and all(isinstance(t, datetime.time) for t in times):
            if times[0] <= now <= times[1]:
                return lunch, times[0], times[1]
    return None

@app.route('/admin/changetimes/', methods=['POST', 'GET'])
@verify_user(allowedusers=admins)
def adminchangetimes(username):
    if request.method == 'GET':
        return render_template('changetimes.html', username=username)
    # coursetimes = []
    # for time in request.json['times']:
    #     if time[0] == None:
    #         continue
    #     coursetimes.append((datetime.time(time['start']['hour'], time['start']['minute']), datetime.time(time['end']['hour'], time['end']['minute']), time['period']))
    app.logger.info(f'Updating course times via http by {username}...')
    update_course_time(int(request.json['day']))
    return jsonify({'status': 'success', 'message': 'Course times changed'})

def get_periods():
    return [course[2] for course in coursetimes] if not coursetimes == None else None

def get_users_with_class(classid):
    newusers = {username: user for username, user in users.items() if classid in user['courses']}
    if 'pingbot' in newusers: del newusers['pingbot']
    return newusers

if __name__ == '__main__':
    update_course_time()
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0', port=5200) if not platform.uname()[1] == 'classfinder' else waitress.serve(app, host='0.0.0.0', port=7842)
