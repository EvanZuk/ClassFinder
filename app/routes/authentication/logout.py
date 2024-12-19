from app import app
from flask import redirect, url_for, request
from app.utilities.users import verify_user, get_token, delete_token


@app.route("/logout")
@verify_user()
def logout(user):
    token = get_token(request.cookies.get("token"))
    delete_token(token)
    response = redirect(url_for("account"))
    response.set_cookie(
        "token", "", httponly=True, samesite="Lax", secure=True, max_age=0
    )
    return response
