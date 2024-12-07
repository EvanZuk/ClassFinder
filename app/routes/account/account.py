from app import app
from flask import render_template
from app.utilities.users import verify_user
from app.utilities.classes import get_today_courses, neededperiods, get_periods_of_user_classes
from app.utilities.canvas import canvas_url

@app.route('/account')
@verify_user
def account(user):
    needcanvaslink = False
    for course in user.classes:
        if course.canvasid == None:
            needcanvaslink = True
            break
    return render_template('account.html',  
                           user=user, 
                           currentclasses=get_today_courses(user),
                           classestoadd=[period for period in neededperiods if period not in get_periods_of_user_classes(user)],
                           neededperiods=neededperiods,
                           canvasurl=canvas_url,
                           needcanvaslink=needcanvaslink
                           )