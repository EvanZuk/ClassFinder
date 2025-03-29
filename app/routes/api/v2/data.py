"""
Allows getting data of a user. Used differently from /export as this is to be used by scoped tokens to get user data.
"""

from flask import request
from app import app
from app.utilities.users import verify_user
from app.utilities.responses import error_response, success_response

@app.route("/api/v2/data", methods=["GET"])
@verify_user(required_scopes=[])
def get_user_data():
    """
    Allows getting data of a user. Used differently from /export as this is to be used by scoped tokens to get user data.
    """
    return_data = {"username": request.user.username, "role": request.user.role}
    token_scopes = request.token.scopes.split(" ") if request.token.scopes is not None else None
    if token_scopes is None:
        return error_response("Please use /export instead. This endpoint is for scoped tokens only, like the ones granted through /auth.", 400)
    return_data["token_scopes"] = [scope for scope in token_scopes if scope != ""]
    if "read-email" in token_scopes:
        return_data["email"] = request.user.email
    if "read-classes" in token_scopes:
        return_data["classes"] = sorted([
            {
                "name": course.name,
                "room": course.room,
                "period": course.period,
                "lunch": course.lunch,
                "canvasid": course.canvasid,
                "verified": course.verified,
            }
            for course in request.user.classes
        ], key=lambda x: x["period"])
    if "read-misc" in token_scopes:
        return_data["created_at"] = round(request.user.created_at.timestamp())
        return_data["created_by"] = request.user.created_by
        return_data["requires_username_change"] = request.user.requires_username_change
    return success_response("User data retrieved successfully", return_data)