from app import app
from app.utilities.classes import get_user_current_period, get_current_period
from app.utilities.users import verify_user
from flask import render_template, url_for, redirect, request
from datetime import datetime

@app.route('/timer/')
@verify_user(required=False)
def timer(user):
    app.logger.debug(request.args.get('noredirect', "false"))
    if user is None:
        period = get_current_period()
        if period is None:
            if request.args.get('noredirect', "false") != "false":
                return render_template('timer.html', nextclass="nothing")
            return redirect(url_for('dashboard'))
        formatted_time = datetime.combine(datetime.now().date(), period['end']).strftime('%m/%d/%Y %I:%M %p')
        return render_template('timer.html', nextclass=formatted_time)
    else:
        period = get_user_current_period(user)
        if period is None:
            if request.args.get('noredirect', "false") != "false":
                return render_template('timer.html', nextclass="nothing")
            return redirect(url_for('dashboard'))
        formatted_time = datetime.combine(datetime.now().date(), period['end']).strftime('%m/%d/%Y %I:%M %p')
        return render_template('timer.html', nextclass=formatted_time)