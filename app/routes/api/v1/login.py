"""
Login route for the legacy API.
"""
from flask import request
from app import app
from app.utilities.users import check_password, create_token
from app.utilities.responses import success_response, error_response
from app.addons.limiter import limiter

@app.route('/api/v1/login/', methods=['POST'])
@limiter.limit("2 per minute")
def legacyapilogin():
    """
    Legacy login route.
    """
    app.logger.debug("Using legacy login")
    creds = request.json
    if creds.get('username') is None or creds.get('password') is None:
        app.logger.debug("Missing username or password")
        return error_response("Missing username or password", 400)
    if not check_password(creds['username'], creds['password']):
        app.logger.debug("Invalid username or password")
        return error_response("Invalid username or password", 401)
    app.logger.debug("Successfully logged in")
    token = create_token(creds['username'], "app")
    return success_response("Successfully logged in", {"token": token.token})
