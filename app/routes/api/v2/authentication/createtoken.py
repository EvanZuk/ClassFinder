"""
This module handles the creation of API tokens for users.
"""
from flask import request, jsonify
from app import app
from app.addons.limiter import limiter
from app.utilities.users import verify_user, create_token

@app.route("/api/v2/createtoken", methods=["POST", "GET"])
@verify_user
@limiter.limit("6 per minute")
def api_v2_createtoken():
    """
    This route creates an API token for the user.
    """
    user = request.user
    token = create_token(
        user.username,
        "api"
    )
    return jsonify(token.token)

@app.route("/api/v2/createscopedtoken", methods=["POST"])
@verify_user
@limiter.limit("6 per minute")
def api_v2_createscopedtoken():
    """
    This route creates an API token for the user with specific scopes.
    """
    user = request.user
    scopes = request.json.get("scopes", None)
    if not scopes:
        return jsonify({"error": "No scopes provided"}), 400
    if not isinstance(scopes, list):
        return jsonify({"error": "Scopes must be a list"}), 400
    token = create_token(
        user.username,
        "api",
        scopes=scopes,
        noexpiry=scopes == ["calendar"] # The calendar scope is a special case
    )
    return jsonify(token.token)
