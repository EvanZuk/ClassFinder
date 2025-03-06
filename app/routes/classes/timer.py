"""
Handles the timer page
"""
from datetime import datetime
from flask import render_template, url_for, redirect, request, make_response
from app import app
from app.utilities.classes import get_user_current_period, get_current_period
from app.utilities.users import verify_user

@app.route('/timer/')
@verify_user(required=False)
def timer():
    """
    Handles the timer page
    """
    user = request.user
    app.logger.debug(request.args.get('noredirect', "false"))
    if user is None:
        period = get_current_period()
        if period is None:
            if request.args.get('noredirect', "false") != "false":
                return render_template('timer.html', nextclass="nothing")
            return redirect(url_for('dashboard'))
        formatted_time = datetime.combine(datetime.now().date(), period['end']).strftime('%m/%d/%Y %I:%M %p')
        response = make_response(render_template('timer.html', nextclass=formatted_time))
        # if period is not None:
        #     end_time = datetime.combine(datetime.today(), period['end'])
        # else:
        #     end_time = datetime.combine(datetime.today(), datetime.strptime("06:00", "%H:%M").time())
        #     end_time += timedelta(days=1)
        # response.headers["Cache-Control"] = f"max-age={round((end_time - datetime.now()).total_seconds())}, immutable, must-revalidate, private"
        return response
    else:
        period = get_user_current_period(user)
        if period is None:
            if request.args.get('noredirect', "false") != "false":
                return render_template('timer.html', nextclass="nothing")
            return redirect(url_for('dashboard'))
        formatted_time = datetime.combine(datetime.now().date(), period['end']).strftime('%m/%d/%Y %I:%M %p')
        response = make_response(render_template('timer.html', nextclass=formatted_time))
        # if period is not None:
        #     end_time = datetime.combine(datetime.today(), period['end'])
        # else:
        #     end_time = datetime.combine(datetime.today(), datetime.strptime("06:00", "%H:%M").time())
        #     end_time += timedelta(days=1)
        # response.headers["Cache-Control"] = f"max-age={round((end_time - datetime.now()).total_seconds())}, immutable, must-revalidate, private"
        return response