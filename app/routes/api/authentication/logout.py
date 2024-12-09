from app import app
from app.utilities.users import verify_user, delete_token, get_token
from app.utilities.responses import success_response, error_response
from flask import request

@app.route("/api/v2/logout", methods=["POST"])
def logout_post():
    token = request.json.get("token")
    if token is None:
        return error_response("Token Required"), 400
    token = get_token(token)
    if token is None:
        return error_response("Invalid Token"), 400
    delete_token(token)
    return success_response("Logout Successful"), 200