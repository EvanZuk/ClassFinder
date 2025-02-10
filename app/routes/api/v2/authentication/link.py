"""
This module handles the linking of external applications for authentication purposes.
"""

from app import app
from flask import request, render_template, redirect, url_for
from app.utilities.responses import success_response, error_response
from app.utilities.users import create_token, verify_user
from app.addons.limiter import limiter
import random


link_codes = {}

# TODO: Verify this works

@app.route("/api/v2/link/create", methods=["POST"])
@limiter.limit("5/minute")
def create_link_code():
    """
    Create a link code for an external application to use to link to the user's account.
    """
    code = random.randint(100000, 999999)
    link_codes[code] = {"ip": request.remote_addr, "user": None}
    return success_response("Code generated", {"code": code})

@app.route("/api/v2/link/verify", methods=["GET"])
def verify_link_code():
    """
    Verify that a link code is valid, and return the user's information if it is.
    """
    code = request.args.get("code")
    if code not in link_codes:
        return error_response("Invalid code"), 404
    if link_codes[code]["ip"] != request.remote_addr:
        return error_response("Code not generated from this IP"), 403
    if link_codes[code]["user"] is None:
        return success_response("Code verified", {"user": None}), 204
    token = create_token(link_codes[code]["user"].username)
    del link_codes[code]
    return success_response("Code verified", {"user": link_codes[code]["user"].username, "token": token})

@app.route("/link")
def redir_link():
    """
    Redirect to the link page.
    """
    return redirect(url_for("account_link"))

@app.route("/account/link")
@verify_user
def account_link(user):
    """
    The account linking page.
    """
    return render_template("link.html", user=user)

@app.route("/account/link/<code>")
@verify_user
def account_link_code(user, code):
    """
    Link the user's account to an external application.
    """
    if code not in link_codes:
        return redirect(url_for("account_link"))
    return render_template("finallink.html", user=user, code=code, codedata=link_codes[code], ip=request.remote_addr)

@app.route("/account/link/<code>", methods=["POST"])
@verify_user
def account_link_confirm(user, code):
    """
    Confirm the linking of the user's account to an external application.
    """
    if code not in link_codes:
        return error_response("Invalid code"), 404
    link_codes[code]["user"] = user
    return success_response("Code confirmed")