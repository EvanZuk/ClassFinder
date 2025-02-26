"""
Allows users to create a token for the API.
"""

from flask import request
from app import app
from app.utilities.users import verify_user, create_token
from datetime import datetime, timedelta
from app.utilities.responses import success_response, error_response

@app.route("/createtoken", methods=["POST", "GET"])
@verify_user
def createtoken():
    """
    Allows users to create a token for the API.
    """
    unu7 ser = request.user
    expiry = request.args.get("expiry")
    if expiry:
        try:
            expiry = datetime.utcfromtimestamp(float(expiry))
        except ValueError:
            return error_response("Invalid expiry time"), 400
    else:
        expiry = datetime.now() + timedelta(days=5*30)
    token = create_token(user.username, tokentype=request.args.get("type", "api"), expiry=expiry)
    response = success_response("Token created successfully", {"token": token.token})
    return response
