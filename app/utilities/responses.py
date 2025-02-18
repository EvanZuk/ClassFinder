"""
This file contains the response functions for API endpoints.
"""

from flask import jsonify

def error_response(message: str, extra: dict = {}): # pylint: disable=dangerous-default-value
    """
    Return a JSON response with an error status.
    """
    return jsonify({"message": message, "status": "error"} | extra)


def success_response(message: str, extra: dict = {}): # pylint: disable=dangerous-default-value
    """
    Return a JSON response with a success status.
    """
    return jsonify({"message": message, "status": "success"} | extra)
