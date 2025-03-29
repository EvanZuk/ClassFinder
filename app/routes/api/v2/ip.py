"""
This module is only used for debugging reverse proxies.
"""
from flask import request
from app import app
from app.utilities.responses import success_response

@app.route("/api/v2/requestdata", methods=["GET"])
def get_ip():
    """
    Returns the request data including IP, headers, and arguments.
    """
    return success_response("Request data",
                            {"ip": request.remote_addr,
                             "headers": dict(request.headers),
                             "args": dict(request.args)
                             }
                            )
