"""
This route returns a list of valid scopes that can be requested.
"""

from app import app
from app.utilities.responses import success_response
from app.utilities.users import readable_scopes

@app.route('/api/v2/scopes', methods=['GET'])
def get_scopes():
    """
    This route returns a list of valid scopes that can be requested.
    """
    scopes = readable_scopes
    return success_response("Scopes retrieved successfully", {"scopes": scopes})
