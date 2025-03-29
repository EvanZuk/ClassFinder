"""
Basic admin route
"""
from flask import render_template, request
from app import app
from app.utilities.users import verify_user
from app.db import Class, User

@app.route("/admin")
@verify_user(allowed_roles=["admin"])
def admin():
    """
    Display the admin dashboard.
    """
    user = request.user
    return render_template(
        "admin.html", user=user, classes=Class.query.all(), users=User.query.all()
    )
