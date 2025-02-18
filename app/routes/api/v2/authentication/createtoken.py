from app import app
from app.utilities.users import verify_user, create_token
from flask import request, jsonify

@app.route("/api/v2/createtoken", methods=["POST", "GET"])
@verify_user
def api_v2_createtoken():
    user = request.user
    token = create_token(user.username, "api")
    return jsonify(token.token)