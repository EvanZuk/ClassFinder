from app import app
from app.utilities.classes import get_user_current_period
from app.utilities.users import verify_user
from flask import render_template, url_for, redirect
from datetime import datetime

@app.route('/timer')
@verify_user
def timer(user):
    period = get_user_current_period(user)
    if period is None:
        return redirect(url_for('dashboard'))
    formatted_time = datetime.combine(datetime.now().date(), period['end']).strftime('%m/%d/%Y %I:%M %p')
    return render_template('timer.html', nextclass=formatted_time)