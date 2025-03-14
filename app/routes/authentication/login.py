from app import app
from flask import render_template, request
from app.utilities.config import devmode
from app.utilities.users import check_password, create_token
from app.addons.limiter import limiter
from app.utilities.responses import error_response, success_response


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
@limiter.limit("40/minute")
def login_post():
    username = request.json.get("username")
    password = request.json.get("password")
    if check_password(username, password):
        response = success_response("Login Successful")
        response.set_cookie(
            "token",
            create_token(username, 'refresh').token,
            httponly=True,
            samesite="Lax",
            secure=True if not devmode else False,
            max_age=604800,
        )
        return response, 200
    return error_response("Invalid Credentials"), 400
