"""
This module handles the creation of API tokens for users.
"""
from flask import request, jsonify
from app import app
from app.utilities.users import verify_user, create_token

@app.route("/api/v2/createtoken", methods=["POST", "GET"])
@verify_user
def api_v2_createtoken():
    """
    This route creates an API token for the user.
    """
    user = request.user
    token = create_token(user.username, "api")
    return jsonify(token.token)
