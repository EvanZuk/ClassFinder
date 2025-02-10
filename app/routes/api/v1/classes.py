from app import app
from app.utilities.users import verify_user
from app.utilities.responses import success_response, error_response
from app.utilities.classes import get_user_current_period, get_today_courses, get_current_period
from flask import jsonify
from datetime import datetime

@app.route('/api/v1/currentcourses/', methods=['GET'])
@verify_user(onfail=lambda:(error_response("You must be logged in to do that."), 401))
def apicurrentcourses(user):
    currentperiod = get_user_current_period(user)
    today = get_today_courses(user)
    return jsonify({
        'status': 'success',
        'courses': {
            c.period: {
                'id': c.id,
                'name': c.name,
                'room': c.room,
                'lunch': c.lunch,
                'verified': c.verified,
                'canvasid': c.canvasid
            } for c in today
        }, 
        'currentperiod': currentperiod['period'] if currentperiod is not None else None,
        'nextclass': int(datetime.combine(datetime.today(), currentperiod['end']).timestamp()) if (currentperiod is not None) else None,
        'dayoff': today == [] or today is None
    })

@app.route('/api/v1/currentperiod/', methods=['GET'])
@verify_user(onfail=lambda:(error_response("You must be logged in to do that."), 401), required=False)
def apicurrentperiod(user):
    currentperiod = get_user_current_period(user) if user is not None else get_current_period()
    response = jsonify({
        'status': 'success',
        'currentperiod': currentperiod['period'] if currentperiod is not None else None,
        'nextclass': int(datetime.combine(datetime.today(), currentperiod['end']).timestamp()) if (currentperiod is not None) else None,
    })
    return response