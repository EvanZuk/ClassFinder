# pylint: disable=missing-function-docstring
"""
Handles error codes.
"""

import random
from flask import render_template
from app import app
from app.utilities.responses import error_response

@app.errorhandler(404)
def page_not_found(e): # pylint: disable=unused-argument
    return render_template("404.html"), 404


@app.errorhandler(401)
def unauthorized(e): # pylint: disable=unused-argument
    return render_template("401.html"), 401

@app.errorhandler(500)
def internal_server_error(e):
    errorcode = random.randbytes(3).hex()
    app.logger.error(e)
    app.logger.error(f"Error code: {errorcode}")
    return error_response("Internal server error", {"error_code": errorcode}), 500
