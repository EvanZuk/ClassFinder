from app import app
from app.addons.limiter import limiter
from app.utilities.users import check_password, create_token
from app.utilities.responses import error_response, success_response
from flask import request
from datetime import datetime

@app.route("/api/v2/login", methods=["POST"])
@limiter.limit("20/minute")
def api_login_post():
    username = request.json.get("username")
    password = request.json.get("password")
    type = request.json.get("type", "app")
    expiry = request.json.get("expiry", None)
    if expiry:
        expiry = datetime.fromtimestamp(expiry, datetime.timezone.utc)
    if type not in ["app", "api"]:
        return error_response("Invalid token type"), 400
    if check_password(username, password):
        response = success_response("Login Successful", {"token": create_token(username, type=type, expiry=expiry).token})
        return response, 200
    return error_response("Invalid Credentials"), 400