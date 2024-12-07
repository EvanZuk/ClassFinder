from app import app
from flask import render_template, request, redirect, url_for
from app.utilities.users import (
    verify_user,
    get_user,
    delete_user,
    create_token,
    create_user,
    get_user_by_email,
)
from app.utilities.validation import validate_username
from app.utilities.responses import error_response, success_response


@app.route("/admin/account/<username>", methods=["DELETE"])
@verify_user(allowed_roles=["admin"])
def delete_account(user, username):
    deluser = get_user(username)
    if deluser:
        if deluser == user:
            return error_response("Cannot delete own account."), 403
        delete_user(deluser)
        return success_response("User deleted."), 200
    return error_response("User not found."), 404


@app.route("/admin/login/<username>", methods=["POST", "GET"])
@verify_user(allowed_roles=["admin"])
def login_as(user, username):
    loguser = get_user(username)
    if loguser:
        token = create_token(username, type="admin")
        response = (
            success_response("Logged in as user.")
            if request.method == "POST"
            else redirect(url_for("dashboard"))
        )
        response.set_cookie(
            "token",
            token.token,
            httponly=True,
            samesite="Strict",
            secure=True,
            max_age=600,
        )
        response.set_cookie(
            "admin_token",
            request.cookies.get("token"),
            httponly=True,
            samesite="Strict",
            secure=True,
            max_age=604800,
        )
        return response
    return error_response("User not found."), 404


@app.route("/admin/create/account")
@verify_user(allowed_roles=["admin"])
def create_account(user):
    return render_template("createaccount.html")


@app.route("/admin/create/account", methods=["POST"])
@verify_user(allowed_roles=["admin"])
def create_account_post(user):
    username = request.json.get("username")
    email = request.json.get("email")
    password = request.json.get("password")
    app.logger.info(
        f"Creating account for {username} with email {email} by {user.username}."
    )
    if not validate_username(username):
        return error_response("Invalid username."), 400
    # if not validate_email(email):
    #     return error_response("Invalid email."), 400
    if not password:
        return error_response("Password is required."), 400
    if get_user(username):
        return error_response("Username already exists."), 400
    if get_user_by_email(email):
        return error_response("Email already exists."), 400
    create_user(username, email, password)
    return success_response("User created."), 200
