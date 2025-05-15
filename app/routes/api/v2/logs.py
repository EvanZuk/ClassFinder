"""
Allows administrators to view logs.
"""
from flask import request
from app import app, get_logs, get_request_logs
from app.utilities.users import verify_user

@app.route("/api/v2/logs", methods=["GET"])
@verify_user(allowed_roles=["admin"])
def get_logs_route():
    """
    Returns the logs of the application.
    """
    app.logger.info(f"{request.user.username} requested logs")
    logs = get_logs()
    return logs, 200

@app.route("/api/v2/request_logs", methods=["GET"])
@verify_user(allowed_roles=["admin"])
def get_request_logs_route():
    """
    Returns the request logs of the application.
    """
    app.logger.info(f"{request.user.username} requested request logs")
    logs = get_request_logs()
    return logs, 200
