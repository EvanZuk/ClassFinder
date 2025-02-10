from app import app
from app.utilities.responses import error_response, success_response
from flask import request

@app.route("/api/v2/requestdata", methods=["GET"])
def get_ip():
    return success_response("Request data", {"ip": request.remote_addr, "headers": dict(request.headers), "args": dict(request.args)})