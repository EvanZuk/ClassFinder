from flask import render_template, request, url_for, redirect, jsonify
import sys
from app import app
from app.utilities.email import send_email, create_email_id, check_email_id
from app.utilities.users import create_user, check_email, get_user_count, create_token
from app.utilities.validation import validate_email, validate_username
from app.addons.limiter import limiter
from app.utilities.responses import error_response, success_response


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
@limiter.limit("2/minute;6/hour")
def register_post():
    email = request.json.get("email")
    if check_email(email):
        return error_response("Already taken"), 400
    if not validate_email(email):
        return error_response("Invalid email"), 400
    emailid = create_email_id(email)
    send_email(
        email=email,
        subject="Confirm your email",
        message="Confirm your email at "
        + url_for("register_confirm", _external=True, emailid=emailid, _scheme="https"),
    )
    if app.config.get("TESTING"):
        return {"status": "success", "message": "Email sent", "emailid": emailid}, 200
    return success_response("Email sent"), 200


@app.route("/register/<emailid>")
def register_confirm(emailid):
    email = check_email_id(emailid)
    if email is None:
        return redirect(url_for("register"))
    return render_template("register_final.html", email=email)


@app.route("/register/<emailid>", methods=["POST"])
def register_confirm_post(emailid):
    email = check_email_id(emailid)
    if email is None:
        return error_response("Invalid email id"), 400
    username = request.json.get("username")
    if not validate_username(username):
        return error_response("Invalid username"), 400
    password = request.json.get("password")
    role = "user"
    if get_user_count() == 0:
        role = "admin"
        app.logger.info(f"{username} has become the first user and is now an admin")
    if create_user(username, email, password, role=role, created_by="email"):
        newtoken = create_token(username, 'refresh').token
        response = success_response("User created.") if not app.config.get("TESTING") else success_response("User created.", {"token": newtoken})
        response.set_cookie(
            "token",
            newtoken,
            httponly=True,
            samesite="Lax",
            secure=True,
            max_age=604800,
        )
        return response, 200
    return error_response("User creation failed."), 400
