from app import app
from flask import render_template
from app.utilities.users import verify_user
from app.db import Class, User


@app.route("/admin")
@verify_user(allowed_roles=["admin"])
def admin(user):
    return render_template(
        "admin.html", user=user, classes=Class.query.all(), users=User.query.all()
    )
