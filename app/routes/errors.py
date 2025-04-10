# pylint: disable=missing-function-docstring
"""
Handles error codes.
"""

import random
from flask import render_template, request
from app import app
from app.utilities.responses import error_response

@app.errorhandler(404)
def page_not_found(e): # pylint: disable=unused-argument
    """
    Handles the 404 page
    """
    return render_template("404.html"), 404


@app.errorhandler(401)
def unauthorized(e): # pylint: disable=unused-argument
    """
    Handles the 401 page
    """
    return render_template("401.html"), 401

@app.errorhandler(500)
def internal_server_error(e):
    """
    Handles the 500 page, and logs the error
    """
    errorcode = random.randbytes(3).hex()
    app.logger.error(e)
    app.logger.error(f"Error code: {errorcode}")
    ret_dict = {"error_code": errorcode}
    # if request.user and request.user.role == "admin": 
    #     ret_dict["error"] = str(e) # this didnt do much
    return error_response("Internal server error", ret_dict), 500
